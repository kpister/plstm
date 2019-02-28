"""Pipeline
Usage:
    pipeline.py <patent_file> [options]

Options: 
    -h, --help          show this message and exit 
    -m, --model FILE    set model file [default: ./model.h5]
    -d, --map FILE      set mapping file [default: ./map.json]
    -k K-NN             set number of nearest neighbors [default: 4]
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
from preprocess import preprocess
from preprocess import remove_common
import tensorflow as tf
from keras.models import load_model
from choose import best_options

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# cross reference against intro
def printDict(name, dic, logger, errlog):
    logger.info(f'Found {len(dic)} possible targets from {name}')
    if len(dic) == 0:
        return

    output = []
    for k,v in sorted(dic.items(), key=lambda kv:kv[1][1], reverse=True)[:10]:
        if v[1] > 0.1:
            output.append(f"{k} {v[1]*100:2.1f}% {v[2]*100:2.1f}% {v[0]*100:2.1f}%")

    if len(output) == 0:
        errlog.error(f'{bcolors.FAIL}No protein matches{bcolors.ENDC}')
        return

    logger.info(f'Printing top {len(output)}:')
    logger.info(f"{'~'*50} prot, comp, norm")
    for s in output:
        logger.info(s)

def top10(text, title, model, mapping, logger, errlog):
    common = open('words.txt').read().split('\n')
    ngrams = preprocess(remove_common(text, common), seq_len=50)

    ## Validate the references and intro
    # ngrams  :: list[sequences]
    # model :: .h5 file
    # mapping :: .json file
    preds = {}

    logger.info(f'Parsing {len(ngrams)} possible {title} sequences...')
    for seq in ngrams:
        if seq not in preds:
            pred = list(predict_word(seq, model, mapping)[0])
            preds[seq] = pred # stored in normal, protien, compound order

    if len(ngrams) == 0:
        errlog.error(f'{bcolors.FAIL}{title}:found 0 sequences{bcolors.ENDC}')
    else:
        printDict(title, preds, logger, errlog)

    return preds

def pipeline(patent_file, model_file, mapping_file, k, logger, errlog): 
    try:
        # use one gpu, twice as much testing. 
        # create a model class?

        #config = tf.ConfigProto( device_count = {'GPU': 1 , 'CPU': 56} ) 
        #sess = tf.Session(config=config) 
        #keras.backend.set_session(sess)


        model = load_model(model_file)
        with open(mapping_file) as mf:
            mapping = json.load(mf)
    except: 
        print(f'{bcolors.FAIL}Input failure{bcolors.ENDC}')
        return 1 # Error code
 
    ## Parse input xml file
    # filename should be direct path from current location
    # set intro to true when searching cits and intro

    doc = XMLDoc(patent_file, title=True, abstract=True, intro=True, citations=True)
    print(f'{bcolors.OKBLUE}Loaded {patent_file}{bcolors.ENDC}')

    ## Parse related tsv file for true targets
    # tsv file should be correlated in name
    # and located in the same directory
    try:
        tsvname = patent_file.replace("US0", "US")
        tsvname = tsvname[:tsvname.find("-")] + ".tsv"
        true_targets = '\n#'.join(PatentTSV(tsvname).targets)

        logger.info(f"True proteins (from tsv):\n#{true_targets}")
    except Exception as e:
        errlog.error(f'{patent_file}:{e}\nContinuing')

    ## Generate refs
    # read from xml file
    # refs :: paragraph
    refs = '\n'.join(doc.nplcit_table)
    intro = doc.intro
    abstract = doc.abstract
    title = doc.title
    keywords = doc.keywords
    whole = doc.whole

    logger.info(f'Abstract: {abstract}')
    logger.info(f'Title: {title}')

    refs = top10(refs, 'references', model, mapping, logger, errlog)
    intro = top10(intro, 'introduction', model, mapping, logger, errlog)
    abstract = top10(abstract, 'abstract', model, mapping, logger, errlog)
    title = top10(title, 'title', model, mapping, logger, errlog)
    keywords = top10(keywords, 'keywords', model, mapping, logger, errlog)
    #whole = top10(whole, 'whole', model, mapping, logger, errlog)

    seqs = []
    seqs += [(k, v[1]) for k, v in refs.items() if v[1] > 0.2]
    seqs += [(k, v[1]) for k, v in abstract.items() if v[1] > 0.2]
    seqs += [(k, v[1]) for k, v in title.items() if v[1] > 0.2]
    seqs += [(k, v[1]) for k, v in keywords.items() if v[1] > 0.2]
    seqs += [(k, v[1]) for k, v in intro.items() if v[1] > 0.2]

    logger.info('Guesses:')
    if len(seqs) == 0:
        return 0

    guess = best_options(seqs, k)
    for g in guess:
        logger.info(g)

    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    arguments = docopt(__doc__)
    pipeline(arguments['<patent_file>'], arguments['--model'], arguments['--map'], int(arguments['-k']), logger=logging, errlog=logging)
