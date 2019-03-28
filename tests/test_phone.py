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

def test_phone():
    nlp = spacy.load('en')
    document = nlp(u"Call me at (123) 456-7891 or (123) 456 7892 or (123)456-7893 or 123-456-7894!")
    matcher = Matcher(nlp.vocab)
    pattern = [{'ORTH': '('}, {'SHAPE': 'ddd'}, {'ORTH': ')'}, {'SHAPE': 'ddd'},
               {'ORTH': '-', 'OP': '?'}, {'SHAPE': 'dddd'}]
    matcher.add('PHONE_NUMBER', None, pattern)
    pattern = [{'SHAPE': 'ddd'}, {'ORTH': '-', 'OP': '?'},{'SHAPE': 'ddd'},
               {'ORTH': '-', 'OP': '?'}, {'SHAPE': 'dddd'}]
    matcher.add('PHONE_NUMBER', None, pattern)

    matches = matcher(document)
    toredact = [(document[start:end].text,document[start:end].start_char,document[start:end].end_char,'PHONE_NUMBER') for match_id, start, end in matches]
    print(toredact)
    assert len(toredact) == 3

