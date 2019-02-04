import sys

# parse tsv files for their target proteins. 
class PatentTSV:
    def __init__(self, name):
        self.name = name
        self.targets = self.parse_targets()

    # returns a list of strings
    def parse_targets(self):
        f = open(self.name)
        target_col = -1
        header = f.readline()
        for i, val in enumerate(header.split("\t")):
            if "Target Name" in val:
                target_col = i

        if target_col == -1:
            return "Target not found in header"

        targets = []
        for line in f:
            target = line.split("\t")[target_col:target_col+1]
            if target[0] not in targets:
                targets.append(target[0])
        return targets

if __name__ == "__main__":
    try:
        name = sys.argv[1]
        tsv = PatentTSV(name)
        print(tsv.targets)
    except Exception as e:
        print(e)
        print('Usage: python parse_tsv.py patent.tsv')
