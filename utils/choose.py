"""Choose Proteins
Usage: 
    choose.py <in-file> <k-neighbors>
"""

from sklearn.cluster import dbscan
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
def best_options(seqs, distance=10):

    # Convert pieces to [ord(i) for i in seq]
    data = []
    for seq in seqs:
        data.append(seq[0].strip('~'))
    X = np.arange(len(data)).reshape(-1, 1)

    def lev_metric(a, b):
        i, j = int(a[0]), int(b[0])
        return levenshtein(data[i].lower(), data[j].lower())


    # TODO think about eps and min_samples
    cluster = dbscan(X, metric=lev_metric, eps=distance, min_samples=1, algorithm='brute')
    count = max(cluster[1])

    new_clusters = []
    for i in range(count + 1):
        cluster_i = [k for k,c in zip(cluster[0], cluster[1]) if c == i]
        if len(cluster_i) <= 1:
            continue

        cluster_seqs = [seqs[el] for el in cluster_i]
        sorted_cluster_seqs = sorted(cluster_seqs, key=lambda kv:kv[1], reverse=True)
        avg_score = sum([seqs[el][1] for el in cluster_i]) / min(5, len(cluster_i))
        new_clusters.append((sorted_cluster_seqs, avg_score))

    return sorted(new_clusters, key=lambda kv:kv[1], reverse=True)

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    print(best_options(args['<in-file>'], int(args['<k-neighbors>'])))

