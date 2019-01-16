import random
import sys

# Sample from an array in a file, output to a new file
# in_file should have elemented separated by '\n'

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


text = in_file.read().split('\n')

small = random.sample(text, quantity)
out_file.write('\n'.join(small))

in_file.close()
out_file.close()
