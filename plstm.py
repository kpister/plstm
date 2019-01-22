#!/usr/bin/env python

import numpy as np
import json
from sys import exit
from numpy import array
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dropout, Dense, LSTM, Bidirectional, Embedding

# following https://machinelearningmastery.com/develop-character-based-neural-language-model-keras/
# and       https://github.com/enriqueav/lstm_lyrics/blob/master/classifier_train.py

BATCH_SIZE = 32
SEQ_LENGTH = 30

def load_doc(filename, valid_chars=None):
    with open(filename) as f:
        text = f.read()

    words = [word.strip() for word in text.split('\n')]
    if valid_chars:
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

    return {'words': words, 'text': text}

def shuffle_and_split_training_set(sentences_original, labels_original, percentage_test=10):
    # shuffle at unison
    print('Shuffling sentences')
    tmp_sentences = []
    tmp_next_char = []
    for i in np.random.permutation(len(sentences_original)):
        tmp_sentences.append(sentences_original[i])
        tmp_next_char.append(labels_original[i])
    cut_index = int(len(sentences_original) * (1.-(percentage_test/100.)))
    x_train, x_test = tmp_sentences[:cut_index], tmp_sentences[cut_index:]
    y_train, y_test = tmp_next_char[:cut_index], tmp_next_char[cut_index:]

    print("Training set = %d\nTest set = %d" % (len(x_train), len(y_test)))
    return array(x_train), array(y_train), array(x_test), array(y_test)

def get_model(vocab_size):
    # define model
    model = Sequential()
    model.add(LSTM(75, input_shape=(SEQ_LENGTH, vocab_size)))
    model.add(Dropout(0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model


# Load data

proteins = load_doc('text/protein_names_200000n.txt')
normal   = load_doc('text/trigram_wiki_200000n.txt', list(set(proteins['text'])))
print('Files loaded')

# mapping from chars to nums
chars = sorted(list(set(proteins['text'] + '!')))
mapping = dict((c, i) for i, c in enumerate(chars))
vocab_size = len(mapping)

mapping_file = open('map.json', 'w')
mapping_file.write(json.dumps(mapping))
mapping_file.flush()
mapping_file.close()
print(f'Mapping created and saved. Vocab size: {vocab_size}')


# Generate Datasets

# convert each character to an array of one hot encoded vectors
sequences = list()
for line in (proteins['words'] + normal['words']):
    sequences.append(array([mapping[char] for char in line]))

sequences = array(sequences)
sequences = array([to_categorical(x, num_classes=vocab_size) for x in sequences]) 
X = np.empty([array(sequences).shape[0], sequences[0].shape[0], sequences[0].shape[1]])

for i, seq in enumerate(sequences):
    try:
        X[i] = seq
    except:
        pass     # where is this error coming from?

# create datasets
y = [1]*len(proteins['words']) + [0]*len(normal['words'])
y = to_categorical(y, num_classes=2)
x_train, y_train, x_test, y_test = shuffle_and_split_training_set(X, y)
y_train = y_train
y_test = y_test
print('Created dataset')


# Create Model and fit

print('Generating model')
model = get_model(vocab_size)

# fit model
model.fit(x_train, y_train, epochs=20, verbose=2, validation_data=(x_test, y_test))

# save the model to file and evaluate
model.save('model.h5')
model.evaluate(x_test, y_test, batch_size=BATCH_SIZE)
