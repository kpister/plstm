"""Choose Proteins
Usage: 
    choose.py <in-file> <k-neighbors>
"""

from sklearn.neighbors import BallTree, DistanceMetric
from docopt import docopt
from leven import levenshtein
import numpy as np

# process a .info file to extract the seqs for 'best_option'
def process_file(filename):
    # open file and read contents
    seqs = []
    f = open(filename)

    # parse contents into sequences
    for line in f:
        if ':' not in line:
            continue
        line = line.split(":")[1]
        if '~' in line and line[0] != '~':
            seq = line[:50]
            percents = line[51:]
            prot = float(percents.split("%")[0])
            seqs.append((seq.lower(), prot))
    return seqs


# Seqs should be a list of tuples, (sequence, probability)
def best_options(seqs, k=4):
    # Convert pieces to [ord(i) for i in seq]
    k = min(k, int(len(seqs)/3))
    k = max(k, 1)

    data = []
    for seq in seqs:
        data.append(seq[0])
    X = np.arange(len(data)).reshape(-1, 1)

    def lev_metric(a, b):
        i, j = int(a[0]), int(b[0])
        return levenshtein(data[i].lower(), data[j].lower())

    # use k-means instead (creat k forests)

    # using k-nn 
    tree = BallTree(X, metric=lev_metric)

    best_group = (None, 0)

    for i in range(len(X)):
        dist, ind = tree.query(X[i:i+1], k=k)
        avg_score = 0
        for j in ind[0]:
            avg_score += seqs[j][1]
        if avg_score > best_group[1]:
            best_group = (ind[0], avg_score)

    res = []
    for j in best_group[0]:
        res.append(seqs[j])
    return res

if __name__ == '__main__':
    args = docopt(__doc__)
    print(best_options(args['<in-file>'], int(args['<k-neighbors>'])))

