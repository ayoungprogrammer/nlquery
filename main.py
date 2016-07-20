from nlquery.nlquery import NLQueryEngine
import os
import sys

def main(argv):
    engine = NLQueryEngine('localhost', 9000)

    while True:
        try:
            line = raw_input("Enter line: ")
            print engine.query(line, format_='plain')
        except EOFError:
            print "Bye!"
            sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
