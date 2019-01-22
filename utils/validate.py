import sys
import json
import numpy as np
from generator import generate
from length import length
from keras.models import load_model
from keras.utils import to_categorical

def testWord(word, model, mapping):
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

    gen = generate(p.read())
    seqs = length('\n'.join(gen).lower(), 30)

    for seq in seqs:
        prediction = testWord(seq, model, mapping)
        if prediction[0][1] > 0.5:
            print(f'{seq}: {prediction}')
