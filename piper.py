"""Piper
Usage:
    piper.py [options]

Options:
    -h, --help                  show this message and exit
    -v, --verbose               print logs [default: True]
    -p, --patents PATENT_DIR    directory with patents [default: ../patents/]
    -m, --model FILE            set model director [default: ./model.pkl]
    -o, --output DIR            set output director [default: output/]
"""


import os
import sys
from docopt import docopt
from glob import glob
from load_model import LSTMClassifier

sys.path.append('utils/')
from pipeline import pipeline

arguments = docopt(__doc__)
patents = sorted(glob(f"{arguments['--patents']}*.XML"))

# Set up for multithreading
for patent in patents[:50]:
    try:
        model = LSTMClassifer(128, 80, 3)
        model.load_state_dict(torch.load(arguments['--model']))
        output = pipeline(patent, model)
        print(f'Working on {patent}')

        patent_name = os.path.basename(patent)[:-4] + '.info'
        filename = f"{arguments['--output']}{patent_name}"
        with open(filename, 'w') as f:
            f.write('\n'.join(output))
        print(f'Finished working on {patent}')
    except Exception as e:
        print(f'Exiting with exception:{e}')
        sys.exit(1)
