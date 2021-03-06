import pandas as pd
import logging
import time
import sys
from multiprocessing import Process, Queue, cpu_count
import argparse
from hansard import *
from hansard.loader import DataStruct
from datetime import datetime


CPU_CORES = 2


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


def export(output_queue, slack_secret):
    import time

    missed_df = pd.DataFrame()
    ambiguities_df = pd.DataFrame()

    hit = 0
    ambiguities = 0
    i = 0

    t0 = time.time()

    # TODO: multiprocess logging.

    while True:
        entry = output_queue.get(block=True)
        if entry is None:
            print('Finished all chunks.')
            break
        else:
            chunk_hitcount, chunk_missed_df, chunk_ambig_df = entry
            hit += chunk_hitcount
            ambiguities += len(chunk_ambig_df)
            i += 1

            missed_df = missed_df.append(chunk_missed_df)
            ambiguities_df = ambiguities_df.append(chunk_ambig_df)

            print(f'Processed {i} chunks so far.')

    from util.slackbot import Blocks, send_slack_post

    total = len(missed_df) + ambiguities + hit

    hit_percent = hit/total * 100
    ambig_percent = ambiguities/total * 100
    missed_percent = len(missed_df)/total * 100

    if slack_secret:
        send_slack_post(slack_secret, [
            Blocks.header('Job completed'),
            Blocks.section(f'Duration: {time.time() - t0:.2f} seconds'),
            Blocks.section(f'Hit percentage: {hit_percent:.2f}% ({hit}/{total} rows)'),
            Blocks.section(f'Ambiguous percentage: {ambig_percent:.2f}%'),
            Blocks.section(f'Missed percentage: {missed_percent:.2f}%'),
        ])

    print('Exporting...')
    print(f'{hit} hits ({hit_percent:.2f}%)...')
    print(f'{ambiguities} ambiguities ({ambig_percent:.2f}%)...')
    print(f'{len(missed_df)} misses ({missed_percent:.2f}%)...')
    print(f'Total rows processed: {total}')
    missed_df.to_csv(os.path.join(OUTPUT_DIR, 'missed_speakers.csv'))
    ambiguities_df.to_csv(os.path.join(OUTPUT_DIR, 'ambig_speakers.csv'))


if __name__ == '__main__':
    parse_config()
    init_logging()

    data = DataStruct()
    data.load()

    from hansard.worker import worker_function

    inq = Queue()
    outq = Queue()

    logging.info('Loading processes...')

    # Reserve a core for the export process.
    process_args = (inq, outq, data)
    processes = [Process(target=worker_function, args=process_args) for _ in range(CPU_CORES - 1)]

    for p in processes:
        p.start()

    logging.info('Loading text...')

    SLACK_SECRET = os.environ.get('SLACK_SECRET')
    if not SLACK_SECRET:
        print('export: Slack updates not enabled.')
    else:
        print('export: Using slack updates.')

    export_process = Process(target=export, args=(outq, SLACK_SECRET))
    export_process.start()

    num_chunks = 0

    for chunk in pd.read_csv(DATA_FILE,
                             sep=',',
                             chunksize=CHUNK_SIZE,
                             usecols=['speechdate', 'speaker']):  # type: pd.DataFrame

        chunk['speechdate'] = pd.to_datetime(chunk['speechdate'], format=DATE_FORMAT)
        inq.put(chunk)
        num_chunks += 1

    logging.info(f'Added {num_chunks} chunks to the queue.')

    for _ in range(len(processes)):
        # Signals to process that no more entries will be added.
        inq.put(None)

    logging.info('Waiting on worker processes...')
    for process in processes:
        process.join()

    # Tell export process to finish.
    outq.put(None)

    logging.info('Waiting on export process...')
    export_process.join()
    logging.info('Complete. Terminating processes...')

    for process in processes:
        process.terminate()

    logging.info('Exiting...')
