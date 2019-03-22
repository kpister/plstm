"""Generator
Usage:
    generator.py <in-file> <out-file>
"""


# Convert large paragraphs into uni-bi-trigram values separated by newlines
def gen_ngrams(in_text):
    lines = in_text.split('\n')
    paras = ' '.join(lines)
    words = [w.strip() for w in paras.split(' ')]
    sequences = []

    if len(words) < 3:
        return []

    for i in range(len(words)-2):
        if '' in words[i:i+3]:
            continue

        # add unigram
        unigram = words[i]
        sequences.append(unigram)

        # add bigram
        bigram = f'{unigram} {words[i+1]}'
        sequences.append(bigram)

        # add trigram
        trigram = f'{bigram} {words[i+2]}'
        sequences.append(trigram)

    sequences.append(f'{words[-2]} {words[-1]}')
    sequences.append(words[-2])
    sequences.append(words[-1])
    return sequences

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)

    with open(args['<in-file>']) as i, open(args['<out-file>'], 'w') as o:
        o.write('\n'.join(gen_ngrams(i.read())))
    
