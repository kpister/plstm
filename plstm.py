#!/usr/bin/env python
"""PLSTM
Usage:
    plstm.py --positive=FILE --negative=FILE [options]

Options:
    -h, --help          show this message and exit
    -p, --positive FILE set positive input file path
    -n, --negative FILE set negative input file path
    --SEQ_LENGTH LENGTH set SEQ_LENGTH [default: 30]
    --BATCH_SIZE SIZE   set BATCH_SIZE [default: 64]
    --LSTM_NODES NUM    set quantity of lstm nodes [default: 80]
    --DROPOUT PERCENT   set percent dropout [default: 0.20]
    --TEST_PERCENT TP   set test and validation percent [default: 0.15]
"""

import numpy as np
import json
from sys import exit
from numpy import array
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dropout, Dense, LSTM, Bidirectional, Embedding
from keras.callbacks import EarlyStopping
from docopt import docopt

# following https://machinelearningmastery.com/develop-character-based-neural-language-model-keras/
# and       https://github.com/enriqueav/lstm_lyrics/blob/master/classifier_train.py

def load_doc(filename, valid_chars=None):
    with open(filename) as f:
        text = f.read()

    words = [word.strip() for word in text.split('\n')]

    if valid_chars == None:
        return {'words': words, 'text': text}

    # if valid chars is non-empty, make sure everything conforms to it
    vwords = []
    for word in words:
        w = ""
        for c in word:
            # replace c with !
            if c not in valid_chars:
                w += "!"
            else:
                w += c
        vwords.append(w)
    return {'words': vwords, 'text': text}


def shuffle_and_split_training_set(sentences_original, labels_original, test_percent):
    # shuffle at unison
    print('Shuffling sentences')
    tmp_sentences = []
    tmp_labels = []
    for i in np.random.permutation(len(sentences_original)):
        tmp_sentences.append(sentences_original[i])
        tmp_labels.append(labels_original[i])
    val_cut_index = int(len(sentences_original) * (1.-(2.*test_percent)))
    test_cut_index = int(len(sentences_original) * (1.-test_percent))
    x_train, x_val, x_test = tmp_sentences[:val_cut_index], tmp_sentences[val_cut_index:test_cut_index], tmp_sentences[test_cut_index:]
    y_train, y_val, y_test = tmp_labels[:val_cut_index], tmp_labels[val_cut_index:test_cut_index], tmp_labels[test_cut_index:]

    print("Training set = %d\nTest set = %d" % (len(x_train), len(y_test)))
    return array(x_train), array(y_train), array(x_val), array(y_val), array(x_test), array(y_test)

def get_model(vocab_size, arguments):
    # define model
    model = Sequential()
    model.add(LSTM(arguments['--LSTM_NODES'], input_shape=(arguments['--SEQ_LENGTH'], vocab_size)))
    model.add(Dropout(arguments['--DROPOUT']))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model

if __name__=='__main__':
    arguments = docopt(__doc__)

    # Load data
    proteins = load_doc(arguments['--positive'])
    normal   = load_doc(arguments['--negative'], list(set(proteins['text'])))
    print('Files loaded')

    # mapping from chars to nums
    chars = sorted(list(set(proteins['text'] + '!')))
    mapping = dict((c, i) for i, c in enumerate(chars))
    vocab_size = len(mapping)

    with open('map.json', 'w') as mapping_file:
        mapping_file.write(json.dumps(mapping))
        print(f'Mapping created and saved. Vocab size: {vocab_size}')

    # Generate Datasets
    # convert each character to an array of one hot encoded vectors
    lines = proteins['words'] + normal['words']
    X = [to_categorical([mapping[c] for c in l], num_classes=vocab_size) for l in lines]

    y = to_categorical([1]*len(proteins['words']) + [0]*len(normal['words']), num_classes=2)
    x_train, y_train, x_val, y_val, x_test, y_test = shuffle_and_split_training_set(X, y, arguments['--TEST_PERCENT'])
    print('Created dataset')

    # Create Model
    print('Generating model')
    model = get_model(vocab_size, arguments)

    # fit model
    checkpoint = ModelCheckpoint('weights.{epoch:02d}-{val_los:.2f}.hdf5')
    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0.001, patience=2)
    model.fit(x_train, y_train, epochs=20, verbose=2, callbacks=[checkpoint, early_stopping], validation_data=(x_val, y_val))

    # save the model to file and evaluate
    model.save('model.h5')
    model.evaluate(x_test, y_test, batch_size=arguments['--BATCH_SIZE'])
