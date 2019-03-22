"""Validate Word
Usage:
    validate.py <patent-file> [options]

Options:
    -h, --help          show this message
    -m, --model FILE    set model file [default: ./model.pkl]
    -d, --device DEV    set the device {'cuda', 'cpu'} [default: cuda]
"""

import torch

# Turn a line into a <line_length x 1 x n_letters>,
# or an array of one-hot letter vectors
def lineToTensor(line, vocab_size=128):
    tensor = torch.zeros(len(line), vocab_size)
    for li, letter in enumerate(line):
        tensor[li][ord(letter)] = 1
    return tensor

def predict_batch(x, model, vocab_size=128, device_id='cuda'):
    if len(x) == 0:
        return []

    batch_size = 1000
    device = torch.device(device_id)
    predictions = []

    model.eval()

    with torch.no_grad():
        model.to(device)
        for i in range(0, len(x) + batch_size, batch_size):
            end = min(i+batch_size, len(x))
            if end <= i:
                break
            batch_x = torch.stack([lineToTensor(word) for word in x[i:end]]).permute(1,0,2)
            if device_id == 'cuda':
                batch_x = batch_x.cuda()

            outputs = model(batch_x).squeeze(0)
            predictions += [el for el in outputs]
    return predictions

if __name__ == '__main__':
    from preprocess import preprocess
    from docopt import docopt
    import sys

    print("STATUS: BROKEN")
    sys.exit(1)
    args = docopt(__doc__)
    model = load_model(args['--model'])
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


