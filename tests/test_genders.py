import pytest
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

def test_genders():
    nlp = spacy.load('en')
    document = nlp(u"he lives like a king")
    male_matcher = PhraseMatcher(nlp.vocab)
    male_patterns = [nlp.make_doc(text) for text in MALE_WORDS]

    male_matcher.add('MaleList', None, *male_patterns)
    male_matches = male_matcher(document)
    toredact = [(document[start:end].text,document[start:end].start_char,document[start:end].end_char,'MALE') for match_id, start, end in male_matches]

    print(toredact)
    assert len(toredact) == 2

