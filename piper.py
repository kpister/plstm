"""Piper
Usage:
    piper.py [options]

Options:
    -h, --help                  show this message and exit
    -v, --verbose               print logs [default: True]
    -p, --patents PATENT_DIR    directory with patents [default: ../patents/]
    -m, --model FILE            set model file [default: ./model.h5]
    -d, --map FILE              set mapping file [default: ./map.json]
    -o, --output DIR            set output director [default: 'output/']
    -e, --error FILE            set error log file [default: 'err.log']
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
patents = sorted(glob(f"{arguments['--patents']}*.XML"))
errlog = genLogger(arguments['--error'], logging.ERROR)

logger = logging.getLogger('output')
f_format = logging.Formatter('%(levelname)s:%(message)s')
# Set up for multithreading
for patent in patents:
    logging.info(f'Working on {patent}')
    patent_name = os.path.basename(patent)[:-4] + '.info'

    f_handler = logging.FileHandler(f"{arguments['--output']}{patent_name}")
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    pipeline(patent, arguments['--model'], arguments['--map'], logger, errlog)
    logging.info(f'Finished working on {patent}')
    logger.removeHandler(f_handler)
    f_handler.close()
