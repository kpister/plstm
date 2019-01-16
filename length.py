import sys

max_length = -1
out_file = None

# handle arguments
try:
    in_file = open(sys.argv[1])
    if len(sys.argv) >= 3:
        max_length = int(sys.argv[2])
        assert(max_length > 0)
    if len(sys.argv) == 4:
        out_file = open(sys.argv[3], 'w')
except:
    print('Usage: python length.py in_file [max_length] [out_file]')
    sys.exit(1)

buckets = {} # histogram
above = -1
for line in in_file:
    line = line.strip()
    line_len = len(line)

    if line_len not in buckets:
        buckets[line_len] = 0
    buckets[line_len] += 1

    if max_length != -1 and line_len > max_length:
        print(line)
        above += 1
    elif out_file:
        line += '~' * (max_length - line_len)
        out_file.write(f'{line}\n')

if above >= 0:
    print(f'There are {above} lines longer than {max_length}')
for key in sorted(buckets):
    print(f'{key}: {buckets[key]}')

if out_file:
    out_file.flush()
    out_file.close()
in_file.close()
