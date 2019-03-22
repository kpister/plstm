#!/usr/bin/env python
"""PLSTM
Usage:
    plstm.py --positive=FILE --negative=FILE --compounds=FILE --blended=FILE [options]

Options:
    -h, --help              show this message and exit
    -p, --positive FILE     set positive input file path
    -n, --negative FILE     set negative input file path
    -b, --blended FILE      set negative input file path
    -c, --compounds FILE    set compount input file path
    --INPUT_SIZE QUANTITY   set sample size from each file [default: 500000]
    --BATCH_SIZE SIZE       set BATCH_SIZE [default: 64]
    --LSTM_NODES NUM        set quantity of lstm nodes [default: 80]
    --DROPOUT PERCENT       set percent dropout [default: 0.20]
    --LEARNING_RATE FLOAT   set learning rate for adam optimizer [default: 0.001]
    --EPOCHS COUNT          set max number of epochs [default: 20]
    --PRINT_EVERY COUNT     set how often to display output in epochs [default: 1]

Notes:
    Vocab size fixed at 128 (ordinal of a letter in ascii)
"""

import random
from docopt import docopt

import torch 
import torch.nn as nn
from torch_model import LSTMClassifier

import time
import math

# following https://machinelearningmastery.com/develop-character-based-neural-language-model-keras/
# and       https://github.com/enriqueav/lstm_lyrics/blob/master/classifier_train.py
# and       https://github.com/spro/practical-pytorch/blob/master/char-rnn-classification/data.py

# Turn a Unicode string to plain ASCII, thanks to http://stackoverflow.com/a/518232/2809427

vocab_size = 128

# Turn a line into a <line_length x 1 x n_letters>,
# or an array of one-hot letter vectors
def lineToTensor(line):
    tensor = torch.zeros(len(line), vocab_size)
    for li, letter in enumerate(line):
        tensor[li][ord(letter)] = 1
    return tensor

# return a list of size "input_size" sampled from the file.
# removes sequences of incorrect length TODO remove this
# removes non-ascii values from text
def load_doc(filename, input_size):
    with open(filename) as f:
        lines = f.read().split('\n')

    words = [word.strip() for word in lines]
    return random.sample(words, min(len(words), input_size))

def get_model(args):
    # define model
    model = LSTMClassifier(input_dim=vocab_size, 
                          hidden_dim=int(args['--LSTM_NODES']), 
                          output_dim=3)

    optimiser = torch.optim.Adam(model.parameters(), lr=float(args['--LEARNING_RATE']))
    loss = nn.CrossEntropyLoss()

    return (model, optimiser, loss)


def train(model, x, y, batch_size, optimizer, criterion, device):
    epoch_loss = 0

    model.train()

    combined = list(zip(x, y))
    random.shuffle(combined)
    x[:], y[:] = zip(*combined)

    with torch.cuda.device(1):
        model.to(device)
        for i in range(0, len(y), batch_size):
            optimizer.zero_grad()

            batch_x = torch.stack([lineToTensor(word) for word in x[i:i+batch_size]]).permute(1,0,2).cuda()
            batch_y = torch.tensor(y[i:i+batch_size], dtype=torch.long).cuda()

            predictions = model(batch_x).squeeze(0)
            loss = criterion(predictions, batch_y)

            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

    return epoch_loss / len(y) * batch_size

# Run a forward pass on the data outputing the percent correct
def evaluate(test_x, test_y, batch_size, model):
    correct = 0
    total = 0
    
    model.eval()
    with torch.no_grad() and torch.cuda.device(1):
        model.to(device)
        for i in range(0, len(test_y), batch_size):

            batch_x = torch.stack([lineToTensor(word) for word in x[i:i+batch_size]]).permute(1,0,2).cuda()
            batch_y = torch.tensor(y[i:i+batch_size], dtype=torch.long).cuda()

            outputs = model(batch_x).squeeze(0)
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
    return correct / total

if __name__=='__main__':
    arguments = docopt(__doc__)

    epochs      = int(arguments['--EPOCHS'])
    input_size  = int(arguments['--INPUT_SIZE'])
    batch_size  = int(arguments['--BATCH_SIZE'])
    print_every = int(arguments['--PRINT_EVERY'])

    # Load data
    proteins  = load_doc(arguments['--positive'], input_size)
    compounds = load_doc(arguments['--compounds'], input_size)
    normal    = load_doc(arguments['--negative'], input_size)
    normal   += load_doc(arguments['--blended'], input_size)
    print('Files loaded')

    # Shuffle data; probably unnecessary
    random.shuffle(proteins)
    random.shuffle(compounds)
    random.shuffle(normal)

    x = normal + proteins + compounds
    y = [0] * len(normal) + [1] * len(proteins) + [2] * len(compounds)
    fifths = len(y)//5

    # Generate Datasets

    combined = list(zip(x, y))
    random.shuffle(combined)
    x[:], y[:] = zip(*combined)

    train_x = x[:3*fifths]
    train_y = y[:3*fifths]
    val_x = x[3*fifths:4*fifths]
    val_y = y[3*fifths:4*fifths]
    test_x = x[4*fifths:]
    test_y = y[4*fifths:]

    # Create Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using {device}\nCreated dataset\nGenerating model')
    model, optim, criterion = get_model(arguments)

    def timeSince(since):
        now = time.time()
        s = now - since
        m = math.floor(s / 60)
        s -= m * 60
        return f'{m}m {int(s):02d}s'

    start = time.time()
    print(f'Training start at {start}')
    val = [0 for _ in range(4)] # stop when worse than the prev 5 epochs
    for e in range(1, epochs + 1):
        loss = train(model, train_x, train_y, batch_size, optim, criterion, device)

        vacc = evaluate(val_x, val_y, batch_size, model)
        # Print iter number, loss, name and guess
        if e % print_every == 0:
            print(f'{e}\t{e*100//epochs}%\t({timeSince(start)})\tloss:{loss:.4f}\tacc:{vacc*100:.1f}%')

        # Add validation testing for early stopping
        if vacc < min(val[:-1]) and min(val) == val[-1]:
            print(f'Finished early on epoch {e} with validation accuracy of {vacc*100:.1f}%')
            break

        val = val[1:]
        val.append(vacc)
        # Save checkpoints

        torch.save(model.state_dict(), f'./plstm/checkpoints/model_{e}e_{int(vacc*100)}v.pkl')

    # evaluate on test data
    acc = evaluate(test_x, test_y, batch_size, model)
    print(f'Accuracy on test set: {acc}')

    # Save model
    torch.save(model.state_dict(), './model.pkl')

