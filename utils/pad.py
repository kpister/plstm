"""Padder
Usage:
    pad.py <in-file> <out-file> <size>
"""

from docopt import docopt

def pad(lines, length):
    sequences = []
    for line in lines:
        line = line.strip()
        if '\n' in line:
            continue

        if len(line) > 1 and len(line) <= length:
            sequences.append(line + '~' * (length - len(line)))

    return sequences

if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<in-file>']) as i, open(args['<out-file>'], 'w') as o:
        assert(int(args['<size>']) > 0)
        seqs = pad(i.read().split('\n'), int(args['<size>']))
        o.write('\n'.join(seqs))
