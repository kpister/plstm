import numpy as np
from sys import exit
from numpy import array
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dropout, Dense, LSTM, Bidirectional, Embedding

# following https://machinelearningmastery.com/develop-character-based-neural-language-model-keras/
# and       https://github.com/enriqueav/lstm_lyrics/blob/master/classifier_train.py

BATCH_SIZE = 32
SEQ_LENGTH = 30

def load_doc(filename):
    with open(filename) as f:
        text = f.read()

    words = [word.strip() for word in text.split('\n')]
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
    return x_train, y_train, x_test, y_test

# Data generator for fit and evaluate
def generator(word_list, labels_list, batch_size, mapping):
    index = 0
    while True:
        x = np.zeros((batch_size, SEQ_LENGTH), dtype=np.int32)
        y = np.zeros((batch_size), dtype=np.bool)
        for i in range(batch_size):
            for t, w in enumerate(word_list[index % len(word_list)]):
                x[i, t] = mapping[w]
            y[i] = labels_list[index % len(word_list)]
            index = index + 1
        yield x, y

def get_model(vocab_size):
    # define model
    model = Sequential()
    model.add(LSTM(75, input_shape=(vocab_size, SEQ_LENGTH)))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model
        
if __name__ == '__main__':
    proteins = load_doc('names_few_30.txt')
    normal   = load_doc('words_few_30.txt')

    # mapping from chars to nums
    chars = sorted(list(set(proteins['text'] + normal['text'])))
    mapping = dict((c, i) for i, c in enumerate(chars))
    vocab_size = len(mapping)

    # convert each character to an array of one hot encoded vectors
    sequences = [ [to_categorical(mapping[c], num_classes=vocab_size) for c in word] 
                    for word in proteins['words'] + normal['words'] ]

    # create datasets
    X = array(sequences)
    y = [1]*len(proteins['words']) + [0]*len(normal['words'])
    y = to_categorical(y, num_classes=2)
    #x_train, y_train, x_test, y_test = shuffle_and_split_training_set(sequences, y)
    print(X.shape)
    print(X.shape[1])
    print(X.shape[2])

    model = get_model(vocab_size)

    # fit model
    model.fit(X, y, epochs=10, verbose=2)

    # save the model to file
    model.save('model.h5')
