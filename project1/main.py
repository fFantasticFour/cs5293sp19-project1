# -*- coding: utf-8 -*-
# Brandon Wolfe's main.py for project1 in cs5293

import argparse
import glob
import nltk
import spacy
import numpy as np
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
import os
from operator import itemgetter

#List of gendered terms taken from https://www.oreilly.com/library/view/applied-text-analysis/9781491963036/ch01.html

MALE = 'male'
FEMALE = 'female'
UNKNOWN = 'unknown'
BOTH = 'both'

MALE_WORDS = set([
    'guy','spokesman','chairman',"men's",'men','him',"he's",'his',
    'boy','boyfriend','boyfriends','boys','brother','brothers','dad',
    'dads','dude','father','fathers','fiance','gentleman','gentlemen',
    'god','grandfather','grandpa','grandson','groom','he','himself',
    'husband','husbands','king','male','man','mr','nephew','nephews',
    'priest','prince','son','sons','uncle','uncles','waiter','widower',
    'widowers'
])

FEMALE_WORDS = set([
    'heroine','spokeswoman','chairwoman',"women's",'actress','women',
    "she's",'her','aunt','aunts','bride','daughter','daughters','female',
    'fiancee','girl','girlfriend','girlfriends','girls','goddess',
    'granddaughter','grandma','grandmother','herself','ladies','lady',
    'lady','mom','moms','mother','mothers','mrs','ms','niece','nieces',
    'priestess','princess','queens','she','sister','sisters','waitress',
    'widow','widows','wife','wives','woman'
])

def main(args):

#Load a nice big model. This was needed in order to use word vectors for the conceptual redaction.
#    nlp = spacy.load('en')
    nlp = spacy.load('en_core_web_lg')
#Loop through all files in the indicated directory    
    for f in glob.glob(args.input):
        num_dates = 0
        num_names = 0
        num_addresses = 0
        num_genders = 0
        num_phones = 0
        num_concepts = 0

        print(f)
        document2 = open(f).read()
#Create a spacy tokenization of the inputted document
        document = nlp(document2)
#For each of the required flags, find the tokens to redact. In the case of gender and phone number, this was easiest to
#implement by just comparing to a hard-coded list of words or pattern of numbers.
        toredact = []
        if args.names: 
            rnames = [(e.text, e.start_char, e.end_char, e.label_) for e in filter(lambda w: w.label_ == 'PERSON', document.ents)]
            num_names = len(rnames)
            toredact = rnames

        if args.dates:
            rdates = [(e.text, e.start_char, e.end_char, e.label_) for e in filter(lambda w: w.label_ == 'DATE', document.ents)]
            num_dates = len(rdates)
            toredact += rdates

        if args.addresses:
            raddress = [(e.text, e.start_char, e.end_char, e.label_) for e in filter(lambda w: w.label_ == 'LOC', document.ents)]
            num_addresses = len(raddress)
            toredact += raddress

        if args.genders:
            female_matcher = PhraseMatcher(nlp.vocab)
            male_matcher = PhraseMatcher(nlp.vocab)
            female_patterns = [nlp.make_doc(text) for text in FEMALE_WORDS]
            male_patterns = [nlp.make_doc(text) for text in MALE_WORDS]

            female_matcher.add('FemaleList', None, *female_patterns)
            female_matches = female_matcher(document)
            toredact += [(document[start:end].text,document[start:end].start_char,document[start:end].end_char,'FEMALE') for match_id, start, end in female_matches]
            male_matcher.add('MaleList', None, *male_patterns)
            male_matches = male_matcher(document)
            toredact += [(document[start:end].text,document[start:end].start_char,document[start:end].end_char,'MALE') for match_id, start, end in male_matches]
            num_genders = len(female_matches) + len(male_matches)

        if args.phones:
            matcher = Matcher(nlp.vocab)
            pattern = [{'ORTH': '('}, {'SHAPE': 'ddd'}, {'ORTH': ')'}, {'SHAPE': 'ddd'},
                    {'ORTH': '-', 'OP': '?'}, {'SHAPE': 'dddd'}]
            matcher.add('PHONE_NUMBER', None, pattern)
            pattern = [{'SHAPE': 'ddd'}, {'ORTH': '-', 'OP': '?'},{'SHAPE': 'ddd'},
                    {'ORTH': '-', 'OP': '?'}, {'SHAPE': 'dddd'}]
            matcher.add('PHONE_NUMBER', None, pattern)

            matches = matcher(document)
            toredact += [(document[start:end].text,document[start:end].start_char,document[start:end].end_char,'PHONE_NUMBER') for match_id, start, end in matches]
            num_phones = len(matches)

#Sort the tokens to be redacted by their first appearance
        toredact = sorted(toredact, key=itemgetter(1))

#'r' is the redacted document.
        r = document2
#Scan through and redact all the words/phrases identified above by replacing them with the block character
        for entity in reversed(toredact):
            start=entity[1]
            end=entity[2]
            r=r[0:start]+'█'+r[end:]

#Next, redact the inputted concept.

#The concept includes sentences, and those could have excluded words in them. To avoid confusion, I re-index the redacted document
        if args.concept:
            document = nlp(r)
            sentences=list(document.sents)
#The target here is a word vector representing the inputted concept. By defining the similarity of sentences to this topic,
#you can exclude any information relating to the forbidden concept.
            target = nlp(args.concept)

            sim = [target.similarity(e) for e in sentences]
            sim = np.array(sim)
#Set the threshold for similarity at 0.55. This is enough to get Keurig, Starbucks, and 'good breakfast' from the concept 'coffee'
            maxima = np.where(sim >0.55)
            toredact2 = [(str(sentences[e]), sentences[e].start_char, sentences[e].end_char, 'CONCEPT') for e in maxima[0]]
            num_concepts = len(toredact2)
            for entity in reversed(toredact2):
                start=entity[1]
                end=entity[2]
                r=r[0:start]+'█'+r[end:]
        redacted_f = f+'.redacted'
        open(redacted_f,"w").write(r)
#For stats, 
        if args.stats:
            print('Stats:')
            print('Number of names: ', num_names)
            print('Number of dates: ', num_dates)
            print('Number of Locations/Addresses: ',num_addresses)
            print('Number of gendered terms: ',num_genders)
            print('Number of phone numbers: ',num_phones)
            print('Number of matching concepts: ',num_concepts)
            stats_f = f+'.stats'
            myfile = open(stats_f, "w")
            myfile.write('\nNumber of names: ')
            myfile.write(str(num_names))
            myfile.write('\nNumber of dates: ')
            myfile.write(str(num_names))
            myfile.write('\nNumber of Addresses: ')
            myfile.write(str(num_names))
            myfile.write('\nNumber of Gendered: ')
            myfile.write(str(num_names))
            myfile.write('\nNumber of phone: ')
            myfile.write(str(num_names))
            myfile.write('\nNumber of concepts: ')
            myfile.write(str(num_names))

            myfile.write('\nRedacted tokens: ')
            for mylist in toredact:
                for item in mylist:
                    myfile.write("%s " % item)
                myfile.write("\n")
            for mylist in toredact2:
                for item in mylist:
                    myfile.write("%s " % item)
                myfile.write("\n")


if __name__ == '__main__':
#    main(url2)
#Add flags for each of the required arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True,
                         help="The directory to be redacted.")
    parser.add_argument("--names", action='store_true')
    parser.add_argument("--dates", action='store_true')
    parser.add_argument("--addresses", action='store_true')
    parser.add_argument("--genders", action='store_true')
    parser.add_argument("--phones", action='store_true')
    parser.add_argument("--concept", type=str, required=False,
                         help="The concept string to be redacted.")
    parser.add_argument("--stats", action='store_true', help='Stats are implemented as a simple flag; if included there will be a filename.txt.stats file written')

    args = parser.parse_args()
    if args.input:
        main(args)

