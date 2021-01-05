import pandas as pd
import logging
import time
import sys
from multiprocessing import Process, Queue, cpu_count
import argparse
from hansard import *
from hansard.loader import DataStruct
from datetime import datetime


CPU_CORES = 1


def parse_config():
    global CPU_CORES
    parser = argparse.ArgumentParser()
    parser.add_argument('--cores', nargs=1, default=1, type=int, help='Number of cores to use.')
    args = parser.parse_args()
    CPU_CORES = args.cores[0]
    if CPU_CORES < 0 or CPU_CORES > cpu_count():
        raise ValueError('Invalid core number specified.')


def init_logging():
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logging.basicConfig(filename='logs/{:%y%m%d_%H%M%S}.log'.format(datetime.now()),
                        format='%(asctime)s|%(levelname)s|%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    # Uncomment to log to stdout as well.
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.debug('Initializing...\n')

    logging.debug(f'Utilizing {CPU_CORES} cores...')


if __name__ == '__main__':
    parse_config()
    init_logging()

    data = DataStruct()
    data.load()

    from hansard.worker import worker_function

    inq = Queue()
    outq = Queue()

    logging.info('Loading processes...')

    hit = 0
    ambiguities = 0
    numrows = 0
    index = 0

    process_args = (inq, outq, data)
    processes = [Process(target=worker_function, args=process_args) for _ in range(CPU_CORES)]

    for p in processes:
        p.start()

    missed_df = pd.DataFrame()
    ambiguities_df = pd.DataFrame()

    missed_indexes = []
    ambiguities_indexes = []

    logging.info('Loading text...')

    for chunk in pd.read_csv(DATA_FILE,
                             sep=',',
                             chunksize=CHUNK_SIZE,
                             usecols=['speechdate', 'speaker']):  # type: pd.DataFrame

        chunk['speechdate'] = pd.to_datetime(chunk['speechdate'], format=DATE_FORMAT)

        t0 = time.time()

        for index, speechdate, speaker in chunk.itertuples():
            inq.put((index, speechdate, speaker))

        for i in range(len(chunk)):
            if i % 100000 == 0:
                logging.debug(f'Chunk Progress: {i}/{len(chunk)}')
            is_hit, is_ambig, missed_i = outq.get()
            if is_hit:
                hit += 1
            elif is_ambig:
                ambiguities += 1
                ambiguities_indexes.append(missed_i)
            else:
                missed_indexes.append(missed_i)

        missed_df = missed_df.append(chunk.loc[missed_indexes, :])
        del missed_indexes[:]

        ambiguities_df = ambiguities_df.append(chunk.loc[ambiguities_indexes, :])
        del ambiguities_indexes[:]

        numrows += len(chunk.index)
        logging.info(f'{len(chunk.index)} processed in {int((time.time() - t0) * 100) / 100} seconds')
        logging.info(f'Processed {numrows} rows so far.')

        # Uncomment break to process only 1 chunk.
        # break

    logging.info('Writing missed speakers data...')
    missed_df.to_csv(os.path.join(OUTPUT_DIR, 'missed_speakers.csv'))
    logging.info('Writing ambiguous speakers data...')
    ambiguities_df.to_csv(os.path.join(OUTPUT_DIR, 'ambig_speakers.csv'))
    logging.info('Complete.')

    for process in processes:
        process.terminate()

    logging.info(f'{hit} hits')
    logging.info(f'{ambiguities} ambiguities')
    logging.info(f'{index} rows parsed')
    logging.info('Exiting...')
