import random
import sys

# Sample from an array in a file, output to a new file
# in_file should have elemented separated by '\n'
def sample(in_text, quantity):
    text = in_text.split('\n')
    small = random.sample(text, quantity)
    return small


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python sample.py in_file out_file quantity')
        sys.exit(1)

    try:
        in_file  = open(sys.argv[1])
        out_file = open(sys.argv[2], 'w')
        quantity = int(sys.argv[3])
    except:
        print('Usage: python sample.py in_file out_file quantity')
        print('     : quantity must be an integer')
        sys.exit(1)

    small = sample(in_file.read(), quantity)
    out_file.write('\n'.join(small))

    in_file.close()
    out_file.close()
