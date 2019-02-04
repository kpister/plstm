"""Pipeline
Usage:
    pipeline.py <patent_file> [options]

Options:
    -h, --help              show this message and exit
    -m, --model FILE   set model file [default: ./model.h5]
    -d, --map FILE   set mapping file [default: ./map.json]
"""

import json
from docopt import docopt
import logging

# personal tooling
import sys
sys.path.append('utils/')
from validate import predict_word
from parse_patent import XMLDoc
from parse_tsv import PatentTSV
from generator import gen_ngrams
from length import pad
from keras.models import load_model


# cross reference against intro
def printDict(name, dic, logger):
    logger.info(f'Found {len(dic)} possible targets from {name}')
    if len(dic) != 0:
        logger.info('Printing top 10:')
        for k,v in sorted(dic.items(), key=lambda kv:kv[1][0])[:10]:
            logger.info(f"{k} {v[0]*100:2.1f}% {v[1]*100:2.1f}%")

def pipeline(patent_file, model_file, mapping_file, logger=None, errlog=None): 
    try:
        model = load_model(model_file)
        with open(mapping_file) as mf:
            mapping = json.load(mf)
    except: 
        print('Input failure')
        return
 
    ## Parse input xml file
    # filename should be direct path from current location
    # set intro to true when searching cits and intro

    doc = XMLDoc(patent_file, intro=True, citations=True)

    ## Parse related tsv file for true targets
    # tsv file should be correlated in name
    # and located in the same directory
    try:
        tsvname = patent_file.replace("US0", "US")
        tsvname = tsvname[:tsvname.find("-")] + ".tsv"
        true_targets = '\n'.join(PatentTSV(tsvname).targets)

        if logger:
            logger.info(f"True proteins (from tsv):\n{true_targets}")
    except Exception as e:
        if errlog:
            errlog.error(f'{patent_file}:{e}\nContinuing')

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

    ref_preds = {}
    intro_preds = {}
    cross_preds = {}

    if logger:
        logger.info(f'Parsing {len(ref_ngrams)} possible reference sequences...')
    if errlog and len(ref_ngrams) == 0:
        errlog.error(f'{patent_file}:references:found 0 sequences')
    for seq in ref_ngrams:
        if seq not in ref_preds:
            pred = list(predict_word(seq, model, mapping)[0])
            if pred[1] > 0.9:
                ref_preds[seq] = pred
    if logger:
        printDict('references', ref_preds, logger)

    if logger:
        logger.info(f'Parsing {len(intro_ngrams)} possible background sequences...')
    if errlog and len(intro_ngrams) == 0:
        errlog.error(f'{patent_file}:background:found 0 sequences')
    for seq in intro_ngrams:
        if seq in ref_preds:
            cross_preds[seq] = ref_preds[seq]
            intro_preds[seq] = ref_preds[seq]
        else:
            pred = list(predict_word(seq, model, mapping)[0])
            if pred[1] > 0.9:
                intro_preds[seq] = pred

    if logger:
        printDict('background', intro_preds, logger)
        printDict('crossover', cross_preds, logger)

if __name__ == '__main__':
    arguments = docopt(__doc__)
    logger = logging.getLogger('root')
    f_handler = logging.StreamHandler()
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('%(levelname)s:%(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
 
    pipeline(arguments['<patent_file>'], arguments['--model'], arguments['--map'], logger)
