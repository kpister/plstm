"""Validate Word
Usage:
    validate.py <patent-file> [options]

Options:
    -h, --help          show this message
    -m, --model FILE    set model file [default: ./model.h5]
    -d, --map FILE      set mapping file [default: ./map.json]
"""

from docopt import docopt
import json
import numpy as np
from preprocess import preprocess
from keras.models import load_model
from keras.utils import to_categorical

def predict_word(word, model, mapping):
    sequence = np.array([mapping.get(char, len(mapping)-1) for char in word])
    sequence = np.array([to_categorical(x, num_classes=len(mapping)) for x in sequence])
    s = np.empty([1, sequence.shape[0], sequence.shape[1]])
    s[0] = sequence

    return model.predict(s)

if __name__ == '__main__':
    args = docopt(__doc__)
    model = load_model(args['--model'])
    mapping = json.load(args['--map'])
    p = open(args['<patent-file>'])

    ngrams = preprocess(p.read(), seq_len=50)

    preds = {}
    for ngram in ngrams:
        preds['ngram'] = predict_word(ngram, model, mapping)[0]

    output = []
    for k,v in sorted(preds.items(), key=lambda kv:kv[1][1], reverse=True)[:10]:
        if v[1] > 0.1:
            output.append(f"{k} {v[1]*100:2.1f}% {v[2]*100:2.1f}% {v[0]*100:2.1f}%")

    if len(output) == 0:
        print(f'{bcolors.FAIL}No protein matches{bcolors.ENDC}')
    else:
        print(f"Printing top {len(output)}:\n{'~'*50} prot, comp, norm")
        for s in output:
            print(s)


