"""Pipeline
Usage:
    pipeline.py <patent_file> [options]

Options:
    -h, --help              show this message and exit
    -m, --model FILE   set model file [default: ./model.h5]
    -d, --map FILE   set mapping file [default: ./map.json]
"""

import sys
import json
from docopt import docopt
from keras.models import load_model

# personal tooling
sys.path.append('utils/')
from validate import predict_word
from parse_patent import XMLDoc
from parse_tsv import PatentTSV
from generator import gen_ngrams
from length import pad

try:
    arguments = docopt(__doc__)
    patent_file = open(arguments['<patent_file>'])
    model = load_model(arguments['--model'])
    mapping = json.load(open(arguments['--map']))
except:
    print(__doc__)
    sys.exit(1)

## Parse input xml file
# filename should be direct path from current location
# set intro to true when searching cits and intro

doc = XMLDoc(patent_file, intro=True, citations=True)

## Parse related tsv file for true targets
# tsv file should be correlated in name
# and located in the same directory
try:
    tsvname = sys.argv[1].replace("US0", "US")
    tsvname = tsvname[:tsvname.find("-")] + ".tsv"
    true_targets = PatentTSV(tsvname).targets
    print(f"True proteins (from tsv): {', '.join(true_targets)}")
except:
    print('Could not find .tsv file with targets.\n Continuing')

## Generate refs
# read from xml file
# refs :: paragraph (lowercase)
refs = '\n'.join(doc.nplcit_table).lower()
intro = doc.intro.lower()

## Convert to ngram token sequences
# ref_ngrams :: [sequences]
ref_ngrams = gen_ngrams(refs)
intro_ngrams = gen_ngrams(intro)

## Trim and Pad reference sequences to length
# this won't be needed with variable length lstm
# ref_ngrams :: [sequences | len(sequences) = 30]
# the remaining space on smaller values will be padded
ref_ngrams = pad(ref_ngrams, length=30)
intro_ngrams = pad(intro_ngrams, length=30)

## Validate the references and intro
# ref_ngrams  :: list[sequences]
# intro :: list[sequences]
# model :: .h5 file
# mapping :: .json file

predictions = []
sequences = []
for seq in ref_ngrams:
    if seq not in sequences:
        predictions.append({'seq':seq, 'pred':predict_word(seq, model, mapping)[0]})
        sequences.append(seq)

for seq in intro_ngrams:
    if seq not in sequences:
        predictions.append({'seq':seq, 'pred':predict_word(seq, model, mapping)[0]})
        sequences.append(seq)

# cross reference against intro

predictions.sort(key=lambda x:x['pred'][1])
for p in predictions:
    print(f"{p['seq']} {p['pred'][0]*100:2.1f}% {p['pred'][1]*100:2.1f}%")

