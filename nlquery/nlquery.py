from collections import OrderedDict
from lango.matcher import match_rules
from lango.parser import StanfordServerParser
from pattern.en import singularize
from wikidata import WikiData
from utils import first
from api_adapter import LoggingInterface
from answer import Answer

from threading import local

class NLQueryEngine(LoggingInterface):
    """
    Grammar mapping for knowledge queries of the form:
    - What is the X of Y
    - What is X's Y
    """

    def __init__(self, host='localhost', port=9000, properties={}):
        LoggingInterface.__init__(self)
        self.parser = StanfordServerParser(host, port, properties)

        """
        Rule for matching a subject and/or property of NP
        Matches:
        - subject            : Subject to get property of
        - prop     (optional): Propert to get of subject

        Examples:
        - Obama born
        - Obama
        - Obama's birthday
        - Barack Obama's wife
        """
        self.subj_rules = OrderedDict([
            # When was (Obama born)
            ('( NP ( NP:subject-o ) ( VP:prop-o ) )', {}),
            # What is (the birth day of Obama)
            ('( NP ( NP:prop-o ) ( PP ( IN ) ( NP:subject-o ) ) )', {}),
            # What is (Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            # What is (Barrack Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Barack Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            ('( NP:subject-o )', {}),
        ])

        """
        Rule for matching subject property query
        Matches:
        - qtype               : Question type (who, where, what, when)
        - subject             :  Subject to get property of
        - prop      (optional): Property to get of subject
        - prop2     (optional): Second part of property
        - prop3     (optional): Overwrite property
        - jj        (optional): Adjective that will be property (e.g. many/tall/high)

        Examples:
        - What religion is Obama?
        - Who did Obama marry?
        - Who is Obama?
        - Who is Barack Obama's wife?
        - How tall is Mt. Everest?
        """
        self.subject_prop_rules = {
            '( SBARQ ( WHNP/WHADVP/WHADJP:qtype_t ) ( SQ:sq_t ) )': {
                'qtype_t': OrderedDict([
                    # What religion
                    ('( WHNP ( WDT:qtype-o=what ) ( NN:prop3-o ) )', {}),
                    # How many/tall
                    ('( WHADJP ( WRB:qtype-o ) ( JJ:jj-o ) )', {}),
                    # What/where/who
                    ('( WHNP/WHADVP:qtype-o )', {}),
                ]),
                'sq_t': {
                    # What ethnicity is Obama
                    '( SQ ( VP ( ADVP:prop-o ) ) ( VBZ ) ( VP:suject-o ) )': {},
                    # Who did Obama marry
                    '( SQ ( VBD:action-o ) ( NP:subj_t ) ( VP:prop-o ) )': {
                        'subj_t': self.subj_rules
                    },
                    # Who did 
                    '( SQ ( VP ( VBZ/VBD/VBP:action-o ) ( NP:subj_t ) ) )':{
                        'subj_t': self.subj_rules
                    },
                    # Who is Edward Thatch known as
                    '( SQ ( VBZ:action-o ) ( NP:subj_t ) ( VP:prop-o ) )': {
                        'subj_t': self.subj_rules,
                    },
                    # What is Obama
                    '( SQ ( VBZ/VBD/VBP:action-o ) ( NP:subj_t ) )': {
                        'subj_t': self.subj_rules
                    }
                }
            }
        }

        """
        Rule for getting property of NP or VP
        Matches:
        prop : Property of instance to match
        op   : Operation to match property
        value: Value of property 

        Examples:
        - born in 1950
        - have population over 100,000
        """
        self.prop_rules = OrderedDict([
            # 
            ('( SQ/VP ( VB/VBP/VBD ) ( VP ( VBN:prop-o ) ( PP ( IN:op-o ) ( NP:value-o ) ) ) )', {}),
            # are in Asia
            ('( SQ/VP ( VB/VBP/VBD ) ( PP ( IN:op-o ) ( NP:value-o ) ) )', {}),
            # have population over 1000000
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( NP:prop-o ) ( PP ( IN:op-o ) ( NP/CD/JJ:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP:prop-o ) ( NP ( QP ( JJR:op-o ) ( IN ) ( CD:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( QP ( JJR:op-o ) ( IN=than ) ( NP/CD/JJ:value-o ) ) ( NNS:value_units-o ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP ( NP:value-o ) ( PP:pp_t ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP:value-o ) )', {}),
        ])

        """
        Rules for finding entity queries
        Matches:
        qtype                   : question type (how many, which)
        inst                    : instance of entity to match
        prop_match_t  (optional): Parse tree for first property match
        prop_match2_t (optional): Parse tree for second property match

        Examples:
        - How many POTUS are there?
        - Which POTUS are born in 1950?
        - How many books are written by George Orwell?
        - How many countries are in Asia and have population over 100,000?
        """
        self.find_entity_rules = OrderedDict([
            ('( SBARQ ( WHNP ( WHNP ( WHADJP:qtype-o ) ( NNS:inst-O ) ) ( PP:prop_match_t ) ) )', {}),
            ('( SBARQ ( WHNP:qtype-o=who ) ( SQ:sq_t ) )', {
                'sq_t': {
                    '( SQ ( VBD/VBZ ) ( NP ( NP:inst-O ) ( PP:prop_match_t ) ) )': {}
                },
            }),
            ('( SBARQ ( WHNP ( WHADJP/WDT/WHNP:qtype-o ) ( NNS/NN/NP:inst-O ) ) ( SQ:sq_t ) )', {
                'sq_t': OrderedDict([
                    # are there
                    ('( SQ ( VBP ) ( NP ( EX=there ) ) )', {}),
                    # are in Asia and have population over 100,000
                    ('( SQ ( VP ( VP:prop_match_t ) ( CC ) ( VP:prop_match2_t ) ) )', {}),
                    ('( SQ ( VP:prop_match_t ) )', {}),
                    ('( SQ:prop_match_t )', {}),
                ])
            }),
        ])

        self.wd = WikiData()

    def subject_query(self, qtype, subject, action, jj=None, prop=None, prop2=None, prop3=None):
        """Transforms matched context into query parameters and performs query

        Args:
            qtype: Matched type of query (what, who, where, etc.)
            subject: Matched subject (Obama)
            action: Matched verb action (is, was, ran)
            jj (optional): Matched adverb
            prop (optional): Matched prop
            prop2 (optional): Matched prop
            prop3 (optional): Matched prop

        Returns:
            Answer: Answer from query, or empty Answer if None
        """
        if jj == 'old':
            # How old is Obama?
            prop = 'age'

        if jj in ['tall', 'high']:
            # How tall is Yao Ming / Eifel tower?
            prop = 'height'

        if prop2:
            prop = prop + ' ' + prop2

        if prop3 and not prop:
            prop = prop3

        if not prop:
            if action not in ['is', 'was']:
                prop = action

        ans = self.get_property(qtype, subject, prop)
        if not ans:
            ans = Answer()

        ans.params = {
            'qtype': qtype,
            'subject': subject,
            'prop': prop,
        }
        return ans

    def get_prop_tuple(self, prop=None, value=None, op=None, value_units=None, pp_t=None):
        """Returns a property tuple (prop, value, op). E.g. (population, 1000000, >)
        
        Args:
            prop (str): Property to search for (e.g. population)
            value (str): Value property should equal (e.g. 10000000)
            op (str): Operator for value of property (e.g. >)

        Returns:
            tuple: Property tuple, e.g: (population, 10000000, >)
        """

        self.info('Prop tuple: {0},{1},{2},{3},{4}', prop, value, op, value_units, pp_t)

        if op in ['in', 'by', 'of']:
            oper = op
        elif op in ['over', 'above', 'more', 'greater']:
            oper = '>'
        elif op in ['under', 'below', 'less']:
            oper = '<'
        else:
            self.error('NO OP {0}', op)
            return None

        # Infer property to match value
        if prop is None:
            if value_units is not None:
                if value_units in ['people']:
                    prop = 'population'
                if not prop:
                    return None

        props = [(prop, value, oper)]

        if pp_t:
            prop_tuple = match_rules(pp_t, self.prop_rules, self.get_prop_tuple)
            if not prop_tuple:
                return None
            props += prop_tuple

        return props

    def find_entity_query(self, qtype, inst, prop_match_t=None, prop_match2_t=None):
        """Transforms matched context into query parameters and performs query for
        queries to find entities

        Args:
            qtype (str): Matched type of query (what, who, where, etc.)
            inst (str): Matched instance of entity to match (Obama)
            action (str): Matched verb action (is, was, ran)
            prop_match_t (Tree): Matched property Tree
            prop_match2_t (Tree): Matched property Tree

        Returns:
            Answer: Answer from query, or empty Answer if None
        """
        props = []
        if prop_match_t:
            prop = match_rules(prop_match_t, self.prop_rules, self.get_prop_tuple)

            if not prop:
                return

            props += prop

        if prop_match2_t:
            prop = match_rules(prop_match2_t, self.prop_rules, self.get_prop_tuple)

            if not prop:
                return

            props += prop

        if not inst.isupper():
            inst = singularize(inst)

        ans = self.wd.find_entity(qtype, inst, props)
        if not ans:
            ans = Answer()

        ans.params = {
            'qtype': qtype,
            'inst': inst,
            'props': props,
        }
        return ans

    def get_property(self, qtype, subject, prop):
        """Gets property of a subject
        Example: 
            get_property('who', 'Obama', 'wife') = 'Michelle Obama'

        Args:
            subject: Subject to get property of
            prop: Property to get of subject

        Todo:
            * Add other APIs here

        Returns:
            Answer: Answer from query
        """
        return self.wd.get_property(qtype, subject, prop)

    def preprocess(self, sent):
        """Preprocesses a query by adding punctuation"""
        if sent[-1] != '?':
            sent = sent + '?'
        return sent

    def query(self, sent, format_='plain'):
        """Answers a query

        If format is plain, will return the answer as a string
        If format is raw, will return the raw context of query

        Args:
            sent: Query sentence
            format_: Format of answer to return (Default to plain)

        Returns:
            dict: Answer context
            str: Answer as a string

        Raises:
            ValueError: If format_ is incorrect
        """
        sent = self.preprocess(sent)
        tree = self.parser.parse(sent)
        context = {'query': sent, 'tree': tree}
        self.info(tree)
        ans = first([
            match_rules(tree, self.find_entity_rules, self.find_entity_query),
            match_rules(tree, self.subject_prop_rules, self.subject_query),
        ])

        if not ans:
            ans = Answer()

        ans.query = sent
        ans.tree = str(tree)

        if format_ == 'raw':
            return ans.to_dict()
        elif format_ == 'plain':
            return ans.to_plain()
        else:
            raise ValueError('Undefined format: %s' % format_)
