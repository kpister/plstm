import sys

# Convert large paragraphs into uni-bi-trigram values separated by newlines
def gen_ngrams(in_text):
    words = in_text.split(' ')
    sequences = []

    for i in range(len(words)-2):
        # add unigram
        unigram = words[i]
        sequences.append(unigram)

        # add bigram
        bigram = f'{unigram} {words[i+1]}'
        sequences.append(bigram)

        # add trigram
        trigram = f'{bigram} {words[i+2]}'
        sequences.append(trigram)
    return sequences

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python generator.py in_file out_file')
        sys.exit(1)

    try:
        in_file = open(sys.argv[1])
        out_file = open(sys.argv[2], 'w')
    except:
        print('Usage: python generator.py in_file out_file')
        sys.exit(1)
    
    out_file.write('\n'.join(gen_ngrams(in_file.read())))
    out_file.close()
    in_file.close()
