# cs5293sp19-project1

This program redacts text for various personal information. It uses the spacy module, which decomposes the sentences of the inputted text
into parts of speech. Using this, spacy can create statistical inferences for how a word is being used in context. Spacy
categorizes some types of words (e.g. Names, Locations, Money) automatically.

Spacy also has a library of word vectors for how many different words are used in context in the english language. For example, 
lions, monkeys, and cats are all loosely clustered in an n-dimensional space around 'mammals'. By comparing a particular word's 
vector to a sentence at hand, we can give a similarity measure for what ideas a sentence might connote. Sentences
involving Keurings, Starbucks, and good breakfasts are all near the word vector for 'coffee', for example. This feature of spacy is used 
to censor the documents for a particular idea.

Usage

pipenv run python project1/main.py --input 'docs/*.txt' --names --dates --addresses --phones --genders --concept 'children' --stats

The input flag is required. The directory docs will be searched for all text files, and redacted for the given flags

Names, dates, addresses, phone numbers, and genders are all simple flags to be passed to the redactor. If you do not wish to redact for names, 
for example, leave off that flag.

The concept flag must be followed by a text string to search for. The text string could be one word or any number of words.

The stats flag outputs filename.txt.stats which summarizes the redaction.

Testing

pipenv run python -m pytest -s

This will test the redaction process for various strings. It is very useful to see the test output using the -s flag.

names
'My name is Brandon' is confirmed to identify 'Brandon'

dates
'Today is Wednesday' is confirmed to identify 'Wednesday'

addresses
'I live on Main Street' is confirmed to identify 'Main Street'

phones
'Call me at (123) 456-7891 or (123) 456 7892 or 123-456-7893' is confirmed to identify three phone numbers

gender
'He will live like a king' is confirmed to identify both he and king

Process

I began by researching word vectors and the conceptual search, since this seemed the most difficult and interesting part of the assignment.
Spacy suggested itself as the state-of-the-art module for such similarity measures. From there I followed the Spacy manual on identifying
locations and phone numbers, etc. The gender search started with a list of gendered words, followed by the matching procedure I learned from 
phone numbers. Using Spacy's word vectors, the conceptual search was quite easy--similarity measures are a built-in method!
