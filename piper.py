"""Piper
Usage:
    piper.py [options]

Options:
    -h, --help                  show this message and exit
    -v, --verbose               print logs [default: True]
    -p, --patents PATENT_DIR    directory with patents [default: ../patents/]
    -m, --model FILE            set model file [default: ./model.h5]
    -d, --map FILE              set mapping file [default: ./map.json]
"""


import os
import sys
import queue
import logging
from docopt import docopt
from glob import glob
from pipeline import pipeline

# root logger
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# individual file loggers
def genLogger(name, level):
    logger = logging.getLogger(name)
    f_handler = logging.FileHandler(name)
    f_handler.setLevel(level)
    f_format = logging.Formatter('%(levelname)s:%(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
    return logger

arguments = docopt(__doc__)
patents = glob(f"{arguments['--patents']}*.XML")
errlog = genLogger('err.log', logging.ERROR)

# Set up for multithreading
for patent in patents:
    logging.info(f'Working on {patent}')
    patent_name = os.path.basename(patent)[:-4] + '.info'
    logger = genLogger(f'output/{patent_name}', logging.INFO)

    pipeline(patent, arguments['--model'], arguments['--map'], logger, errlog)
    logging.info(f'Finished working on {patent}')
