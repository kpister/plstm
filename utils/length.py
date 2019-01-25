import sys

def pad(lines, length):
    sequences = []
    for line in lines:
        line = line.strip()
        if '\n' in line:
            continue
        line_len = len(line)
        if line_len > 0 and line_len <= length:
            sequences.append(line + '~' * (length - line_len))
    return sequences

def length(lines, max_length=-1, verbose=False):
    sequences = []
    buckets = {} # histogram
    above = -1
    for line in lines:
        line = line.strip()
        line_len = len(line)

        if line_len not in buckets:
            buckets[line_len] = 0
        buckets[line_len] += 1

        if max_length != -1 and line_len > max_length:
            above += 1
        elif line_len > 0:
            line += '~' * (max_length - line_len)
            sequences.append(line)

    if verbose:
        for key in sorted(buckets):
            if max_length > -1 and key < max_length:
                print(f'{key}: {buckets[key]}')
        if above >= 0:
            print(f'There are {above} lines longer than {max_length}')
    return sequences


if __name__ == '__main__':
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

    sequences = length(in_file.read().split('\n'), max_length, True)
    if out_file:
        out_file.write('\n'.join(sequences))
        out_file.flush()
        out_file.close()
    in_file.close()
