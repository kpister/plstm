"""Preprocess
Usage: 
    preprocess.py <in-file>

"""

import random
from docopt import docopt
from generator import gen_ngrams
from pad import pad

def preprocess_word(word):
    new_word = ''
    for i, c in enumerate(reversed(word)):
        if c.isalnum() or c in [')',']']:
            return word[:len(word)-i]

# given a body of text return:
# a list of uni-bi-tri gram sequences s.t.
# each sequence is of length exactly seq_len
# all non-internal punctuation removed
# the list is of size sample or full, if -1
def preprocess(text, seq_len=50, sample=-1):
    ## Remove non-internal punctuation
    words = text.split(' ')
    pwords = [pwords.append(preprocess_word(w)) for w in words]
    ptext = ' '.join(pwords)

    ## Convert to ngram token sequences
    # ngrams :: [sequences]
    ngrams = gen_ngrams(ptext)

    ## Trim and Pad reference sequences to length
    # this won't be needed with variable length lstm
    # ngrams :: [sequences | len(sequences) = 50]
    # the remaining space on smaller values will be padded
    ngrams = pad(ngrams, length=seq_len)

    if sample != -1:
        return random.sample(ngrams, min(sample, len(ngrams)))

    return ngrams

if __name__ == '__main__':
    arguments = docopt(__doc__)
    preprocess(arguments['<in-file>'])
