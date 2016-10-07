# NLQuery

A natural language query engine on WikiData. 

* [Demo](http://nlquery.ayoungprogrammer.com)
* [Blogpost](http://blog.ayoungprogrammer.com/2016/10/creating-natural-language-query-engine.html/)

Examples:
```
Who is Obama? 44th President of the United States
How tall is Yao Ming? 2.286m
Where was Obama born? Kapiolani Medical Center for Women and Children
When was Obama born? August 04, 1961
Who did Obama marry? Michelle Obama
Who is Obama's wife? Michelle Obama
Who is Barack Obama's wife? Michelle Obama
Who was Malcolm Little known as? Malcolm X
What is the birthday of Obama? August 04, 1961
What religion is Obama? Christianity
Who did Obama marry? Michelle Obama

How many countries are there? 196
Which countries have a population over 1000000000? People's Republic of China, India
Which books are written by Douglas Adams? The Hitchhiker's Guide to the Galaxy, ...
Who was POTUS in 1945? Harry S. Truman
Who was Prime Minister of Canada in 1945? William Lyon Mackenzie King
Who was CEO of Apple Inc in 1980? Steve Jobs
```

# Architecture

```
English query -> Parse Tree -> Matched Context -> Sparql Query -> Answer

Example:
Who did Obama marry?
-> (SBARQ
     (WHNP (WP Who))
     (SQ (VBD did) (NP (NNP Obama)) (VP (VB marry)))
     (. ?))
-> {'subject': 'Obama', 'property': 'marry'}
-> SELECT ?valLabel
        WHERE {
           {
                wd:Q76 p:P26 ?prop .
                ?prop ps:P26 ?val .
            }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en"}
        }
-> Michelle Obama
```

## Install

### Download Stanford CoreNLP

Make sure you have Java installed for the Stanford CoreNLP to work.

[Download Stanford CoreNLP](http://stanfordnlp.github.io/CoreNLP/#download)

### Run the Stanford CoreNLP server

Run the following command in the folder where you extracted Stanford CoreNLP
```
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
```

### Install nlquery

```
git clone https://github.com/ayoungprogrammer/nlquery
cd nlquery
pip install -r requirements.txt
```

## Run

Start the command line:

```
python main.py
```

To run web app, go to nlquery-app/readme.md


## Tests

Run
```
py.test
```
