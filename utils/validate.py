import sys
import json
import numpy as np
from generator import gen_ngrams
from length import length
from keras.models import load_model
from keras.utils import to_categorical

def predict_word(word, model, mapping):
    sequence = np.array([mapping.get(char, len(mapping)-1) for char in word])
    sequence = np.array([to_categorical(x, num_classes=len(mapping)) for x in sequence])
    s = np.empty([1, sequence.shape[0], sequence.shape[1]])
    s[0] = sequence

    return model.predict(s)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python validate.py model_file map_file patent_file')
        sys.exit(1)

    try:
        model = load_model(sys.argv[1])
        mapping = json.load(open(sys.argv[2]))
        p = open(sys.argv[3])
    except Exception as e:
        print(e)
        sys.exit(1)

    gen = gen_ngrams(p.read())
    seqs = length([x.lower() for x in gen], 30)

    preds = []
    for seq in seqs:
        preds.append({'seq':seq, 'pred':predict_word(seq, model, mapping)[0]})

    preds.sort(key=lambda x:x['pred'][1])
    for p in preds:
        print(f"{p['seq']} {p['pred'][0]*100:2.1f}% {p['pred'][1]*100:2.1f}%")

