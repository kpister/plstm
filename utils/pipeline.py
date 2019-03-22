"""Pipeline
Usage:
    pipeline.py <patent_file> [options]

Options: 
    -h, --help          show this message and exit 
    -m, --model FILE    set model directory [default: ./model.pkl]
    -d, --device DEV    set the device to predict on {cuda, cpu} [default: cuda]
"""

# personal tooling
from validate import predict_batch
from parse_patent import XMLDoc
from parse_tsv import PatentTSV
from preprocess import preprocess
from preprocess import remove_common
from choose import best_options

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Print out up to 10 of the best proteins from dic
def printProteins(name, dic):
    output = []
    for k,v in sorted(dic.items(), key=lambda kv:kv[1][1], reverse=True)[:10]:
        if v[1] > 0:
            output.append(f"{k} {v[1]:.2f} {v[2]:.2f} {v[0]:.2f}")

    if len(output) == 0:
        print(f'{bcolors.FAIL}{name}:No protein matches{bcolors.ENDC}')
        return []

    prepend = [f'Found {len(dic)} possible targets from {name}',
               f'Printing top {len(output)}:',
               f"{'~'*50} prot, comp, norm"]
    return prepend + output

def predict(text, model, device_id):
    ## Predict the text
    # ngrams  :: list[sequences]
    # model :: pytorch model

    preds = {}
    common = open('utils/words.txt').read().split('\n')
    ngrams = preprocess(remove_common(text, common), seq_len=50)

    for ngram, pred in zip(ngrams, predict_batch(ngrams, model, device_id=device_id)):
        preds[ngram] = pred # stored in normal, protien, compound order

    return preds

def pipeline(patent_file, model, device_id='cuda'): 
    output = []

    ## Parse input xml file
    # filename should be direct path from current location
    # set intro to true when searching cits and intro
    doc = XMLDoc(patent_file)
    print(f'{bcolors.OKBLUE}Loaded {patent_file}{bcolors.ENDC}')

    ## Parse related tsv file for true targets
    # tsv file should be correlated in name
    # and located in the same directory
    try:
        tsvname = patent_file.replace("US0", "US")
        tsvname = tsvname[:tsvname.find("-")] + ".tsv"
        true_targets = '\n# '.join(PatentTSV(tsvname).targets)

        output += [f"True proteins (from tsv):\n# {true_targets}"]
    except Exception as e:
        print(f'{patent_file}:tsv:{e}\nContinuing')

    refs = predict(doc.references, model, device_id)
    abstract = predict(doc.abstract, model, device_id)
    title = predict(doc.title, model, device_id)
    keywords = predict(doc.keywords, model, device_id)
    keypatent = predict(doc.keypatent, model, device_id)

    seqs  = [(k, v[1]) for k, v in refs.items() if v[1] > 0]
    seqs += [(k, v[1]) for k, v in abstract.items() if v[1] > 0]
    seqs += [(k, v[1]) for k, v in title.items() if v[1] > 0]
    seqs += [(k, v[1]) for k, v in keywords.items() if v[1] > 0]
    seqs += [(k, v[1]) for k, v in keypatent.items() if v[1] > 0]

    if len(seqs) == 0:
        print("No sequences found")
        return []

    clusters = best_options(seqs,distance=7)
    if len(clusters) > 0:
        output += [f"Final Guess:\n& {clusters[0][0][0][0].strip('~')}\n\n"]

    output += ['Guesses']

    for index, k in enumerate(clusters):
        cluster = k[0]
        output += [f'Cluster {index}:\tAverage:{k[1]}']

        for guess in cluster: 
            output += [str(guess)]

    debug = ["DEBUGGING INFO",
             f'Abstract: {doc.abstract}',
             f'Title: {doc.title}']

    output += debug

    # add top entries in each category
    output += printProteins('references', refs)
    output += printProteins('abstract', abstract)
    output += printProteins('title', title)
    output += printProteins('keywords', keywords )
    output += printProteins('keypatent', keypatent)

    output += ['\nALL PREDICTIONS\n']
    # add entire output for parsing later if needed
    #output += [f'{k}, {v[1]:.2f}, {v[2]:.2f}, {v[0]:.2f}' for k, v in refs.items()]
    #output += [f'{k}, {v[1]:.2f}, {v[2]:.2f}, {v[0]:.2f}' for k, v in abstract.items()]
    #output += [f'{k}, {v[1]:.2f}, {v[2]:.2f}, {v[0]:.2f}' for k, v in title.items()]
    #output += [f'{k}, {v[1]:.2f}, {v[2]:.2f}, {v[0]:.2f}' for k, v in keywords.items()]
    #output += [f'{k}, {v[1]:.2f}, {v[2]:.2f}, {v[0]:.2f}' for k, v in keypatent.items()]

    return output

if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__)

    import torch
    import sys
    sys.path.append('./')
    from torch_model import LSTMClassifier

    model = LSTMClassifier(128, 120, 3, device_id='cpu')
    model.load_state_dict(torch.load(arguments['--model']))

    device_id = arguments['--device']

    output = pipeline(arguments['<patent_file>'], model, device_id)
    print('\n'.join(output))
