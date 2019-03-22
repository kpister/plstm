"""Preprocess
Usage: 
    preprocess.py <in-file> <out-file>

"""

import random
from generator import gen_ngrams
from pad import pad

def preprocess_word(word):
    word = "".join(i for i in word if ord(i)<128)
    for i, c in enumerate(reversed(word)):
        if c.isalnum() or c in [')',']']:
            return word[:len(word)-i]
    return None

def remove_common(text, common):
    # if three common words are next to each other, remove the inner one
    total = []

    for line in text.split('\n'):
        words = line.split(' ')
        processed_words = []
        for word in words:
            pw = preprocess_word(word)
            if pw:
                processed_words.append(pw.lower())

        new_text = []
        if len(processed_words) < 1:
            continue

        if processed_words[0] not in common:
            new_text.append(words[0])  

        if len(processed_words) < 2:
            total.append(" ".join(new_text))
            continue

        for index in range(1, len(processed_words) - 1):
            # iterate
            prev = processed_words[index-1]
            word = processed_words[index]
            post = processed_words[index+1]

            if prev in common and word in common and post in common:
                pass
            else:
                new_text.append(words[index])
        if processed_words[-1] not in common and processed_words[-2] not in common:
            new_text.append(words[-1])

        total.append(" ".join(new_text))

    return "\n".join(total)

# given a body of text return:
# a list of uni-bi-tri gram sequences s.t.
# each sequence is of length exactly seq_len
# all non-internal punctuation removed
# the list is of size sample or full, if -1
def preprocess(text, seq_len=50, sample=-1):
    total = []

    for line in text.split("\n"):
        ## Remove non-internal punctuation
        words = line.split(' ')
        pwords = []
        for word in words:
            pw = preprocess_word(word)
            if pw:
                pwords.append(pw)
        ptext = ' '.join(pwords)

        ## Convert to ngram token sequences
        # ngrams :: [sequences]
        ngrams = gen_ngrams(ptext)

        ## Trim and Pad reference sequences to length
        # this won't be needed with variable length lstm
        # ngrams :: [sequences | len(sequences) = 50]
        # the remaining space on smaller values will be padded
        ngrams = pad(ngrams, length=seq_len)
        total += ngrams

    if sample != -1:
        return random.sample(total, min(sample, len(total)))

    return total

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    with open(args['<in-file>']) as i, open(args['<out-file>'], 'w') as o:
        ngrams = preprocess(i.read())
        o.write('\n'.join(ngrams))
