import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Set, Union
import logging
import time
import re
import sys
from multiprocessing import Process, Queue, cpu_count
import argparse


DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT2 = '%Y/%m/%d'

MP_ALIAS_PATTERN = re.compile(r'\(([^\)]+)\)')


INPUT_DIR = os.environ.get('SCRATCH', '.')
OUTPUT_DIR = os.environ.get('SCRATCH', '.')


DATA_FILE = os.path.join(INPUT_DIR, 'hansard_justnine_12192019.csv')

CHUNK_SIZE = 10**6


def cleanse_string(s):
    # Cleanse string from trailing and leading white space.
    s = s.lower().strip()

    # Remove characters that are not alphabetical, a hyphen, or a space.
    s = re.sub(r"[^a-zA-Z\- ]", "", s)

    # Change multiple whitespaces to single spaces.
    s = re.sub(r' +', ' ', s)
    return s


class FirstNameMissingError(Exception):
    pass


class LastNameMissingError(Exception):
    pass


class SpeakerAmbiguityError(Exception):
    pass


class SpeakerReplacement:
    def __init__(self, full_name, first_name, last_name, member_id, start, end):
        self.first_name = cleanse_string(first_name)
        self.last_name = cleanse_string(last_name)

        name_parts = cleanse_string(full_name).split()

        try:
            # Start from the end of the name in case their first name matches a title.
            fn_index = name_parts[::-1].index(self.first_name)
        except ValueError:
            raise FirstNameMissingError

        try:
            # Start from the end of the name in case their surname matches a title.
            ln_index = name_parts[::-1].index(self.last_name)
        except ValueError:
            raise LastNameMissingError

        self.titles = name_parts[:fn_index]
        for i, title in enumerate(self.titles):
            if title.endswith('.'):
                self.titles[i] = title[:-1]

        self.middle_names = name_parts[fn_index + 1:ln_index]

        self.member_id = member_id
        self.id = f'{self.first_name}_{self.last_name}_{member_id}'

        self.middle_possibilities = list(re.sub(' +', ' ', p.strip()) for p in self._generate_middle_parts(0))

        self.aliases: Set[str] = set(self._generate_aliases())

        self.start_date: datetime = start
        self.end_date: datetime = end

    def _generate_aliases(self):
        for title in self.titles + ['']:
            for fn in ('', self.first_name[0], self.first_name[0] + '.', self.first_name):
                for mn in self.middle_possibilities:
                    if title:
                        yield re.sub(' +', ' ', f'{title + "."} {fn} {mn} {self.last_name}').strip(' ')
                    yield re.sub(' +', ' ', f'{title} {fn} {mn} {self.last_name}').strip(' ')

    def _generate_middle_parts(self, i):
        if i >= len(self.middle_names):
            yield ''
            return

        a = self.middle_names[i][0] + ' '
        b = self.middle_names[i][0] + '.' + ' '
        c = self.middle_names[i] + ' '

        for p in self._generate_middle_parts(i + 1):
            yield p
            yield a + p
            yield b + p
            yield c + p

    def matches(self, speaker_name: str, speech_date: datetime, cleanse=True):
        if not self.start_date <= speech_date <= self.end_date:
            return False

        if cleanse:
            speaker_name = cleanse_string(speaker_name)

        return speaker_name in self.aliases

    def __repr__(self):
        return f'SpeakerReplacement({self.id}, {self.start_date}, {self.end_date})'


class Office:
    STOPWORDS = {'of', 'the', 'to'}

    def __init__(self, office_id, office_name):
        self.id = office_id
        self.name = office_name

        self.words = cleanse_string(office_name).split()

        self.aliases = set(self._generate_parts(0))

    def _generate_parts(self, i):
        if i >= len(self.words):
            yield ''
            return

        word = self.words[i]

        for p in self._generate_parts(i + 1):
            if word in Office.STOPWORDS:
                yield p
            if p:
                yield word + ' ' + p
            else:
                yield word

    def matches(self, target, cleanse=True):
        if cleanse:
            target = cleanse_string(target)
        return target in self.aliases


class OfficeHolding:
    # TODO: check start-end dates for 19th century

    def __init__(self, holding_id, member_id, office_id, start_date, end_date, office):
        self.holding_id = holding_id
        self.member_id = member_id
        self.office_id = office_id
        self.start_date = start_date
        self.end_date = end_date
        self.office = office

    def matches(self, office_name: str, speech_date: datetime, cleanse=True):
        if not self.start_date <= speech_date <= self.end_date:
            return False

        return self.office.matches(office_name, cleanse=cleanse)

    @property
    def speaker(self) -> SpeakerReplacement:
        return speaker_dict[self.member_id]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cores', nargs=1, default=1, type=int, help='Number of cores to use.')
    args = parser.parse_args()
    cores = args.cores[0]
    if cores < 0 or cores > cpu_count():
        raise ValueError('Invalid core number specified.')

    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logging.basicConfig(filename='logs/{:%y%m%d_%H%M%S}.log'.format(datetime.now()), format='%(asctime)s|%(levelname)s|%(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)

    # Uncomment to log to stdout as well.
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.debug('Initializing...\n')

    logging.debug(f'Utilizing {cores} cores...')

    logging.debug('Loading misspellings...')
    misspellings: pd.DataFrame = pd.read_csv('misspellings_dictionary.csv', sep=',', encoding='ISO-8859-1')
    misspellings['correct'] = misspellings['correct'].fillna('')
    misspellings_dict = {k.lower(): v for k, v in zip(misspellings['incorrect'], misspellings['correct'])}

    ocr_title_errs: pd.DataFrame = pd.read_csv('common_OCR_errors_titles.csv', sep=',')
    ocr_title_errs['CORRECT'] = ocr_title_errs['CORRECT'].fillna('')
    ocr_err_dict = {k.lower(): v for k, v in zip(ocr_title_errs['INCORRECT'], ocr_title_errs['CORRECT'])}
    misspellings_dict.update(ocr_err_dict)

    speakers = []
    speaker_dict: Dict[str, SpeakerReplacement] = {}
    office_dict: Dict[str, Office] = {}
    full_alias_dict: Dict[str, List[SpeakerReplacement]] = {}
    holdings = []

    logging.debug('Reading mps.csv...')
    mps: pd.DataFrame = pd.read_csv('mps.csv', sep=',')

    malformed_mp_date = 0
    malformed_mp_name = 0
    missing_fn_name = 0
    missing_sn_name = 0

    logging.debug('Parsing mps.csv...')
    for index, row in mps.iterrows():
        try:
            dob = datetime.strptime(row['mp.dob'], DATE_FORMAT)
        except TypeError:
            malformed_mp_date += 1
            logging.debug(f'Invalid date at row: {index}. DOB is {row["mp.dob"]}. DOD is {row["mp.dod"]}')
            continue

        try:
            dod = datetime.strptime(row['mp.dod'], DATE_FORMAT)
        except TypeError:
            # Assume that the speaker is still alive.
            dod = datetime.now()
            continue

        fullname, firstname, surname = row['mp.name'], row['mp.fname'], row['mp.sname']

        if type(firstname) != str:
            missing_fn_name += 1
            logging.debug(f'Missing first name at row: {index}. Fullname is {row["mp.name"]}. Surname is {row["mp.sname"]}.')
            continue
        elif type(surname) != str:
            missing_sn_name += 1
            logging.debug(f'Missing surname at row: {index}. Fullname is {row["mp.name"]}. First name is {row["mp.fname"]}.')
            continue

        defined_aliases = []
        for alias in MP_ALIAS_PATTERN.finditer(fullname):
            defined_aliases.append(alias.group(1))

        MP_ALIAS_PATTERN.sub('', fullname)

        # if '(' in row['mp.name']:
        #     malformed_mp_name += 1
        #     logging.debug(f'Unhandled character at row: {index}. Fullname is {row["mp.name"]}.')
        #     continue

        try:
            speaker = SpeakerReplacement(fullname, firstname, surname, row['member.id'], dob, dod)
            speakers.append(speaker)
            speaker_dict[speaker.member_id] = speaker

            for alias in speaker.aliases:
                full_alias_dict.setdefault(alias, []).append(speaker)

            for alias in defined_aliases:
                full_alias_dict.setdefault(alias, []).append(speaker)

        except FirstNameMissingError:
            continue
        except LastNameMissingError:
            continue

    logging.info(f'{malformed_mp_date} speakers with malformed dates', )
    logging.info(f'{malformed_mp_name} speakers with malformed fullnames', )
    logging.info(f'{missing_fn_name} speakers with malformed first names', )
    logging.info(f'{missing_sn_name} speakers with malformed surnames', )
    logging.info(f'{len(speakers)} speakers sucessfully loaded out of {len(mps)} rows.')

    logging.info('Loading offices...')
    offices_df = pd.read_csv('offices.csv', sep=',')
    for index, row in offices_df.iterrows():
        office = Office(row['office_id'], row['name'])
        office_dict[office.id] = office

    logging.info('Loading office holdings...')
    holdings_df = pd.read_csv('officeholdings.csv', sep=',')
    unknown_members = 0
    unknown_offices = 0
    invalid_office_dates = 0
    for index, row in holdings_df.iterrows():
        # oh_id,member_id,office_id,start_date,end_date
        try:
            holding_start = datetime.strptime(row['start_date'], DATE_FORMAT)

            if type(row['end_date']) == float:
                holding_end = datetime.now()
            else:
                holding_end = datetime.strptime(row['end_date'], DATE_FORMAT)

        except TypeError:
            logging.debug(f'Invalid office holding date in row {index}. start_date is {row["start_date"]}')
            invalid_office_dates += 1
            continue

        if row['member_id'] not in speaker_dict:
            logging.debug(f'Member with id {row["member_id"]} not found for office holding at row {index}')
            unknown_members += 1
            continue

        if row['office_id'] not in office_dict:
            logging.debug(f'Office holding at row {index} linked to invalid office id: {row["office_id"]}')
            unknown_offices += 1
            continue

        holding = OfficeHolding(row['oh_id'], row['member_id'], row['office_id'], holding_start, holding_end,
                                office_dict[row['office_id']])
        holdings.append(holding)

    logging.debug(f'{unknown_members} office holding rows had unknown members.')
    logging.debug(f'{unknown_offices} office holding rows had unknown offices.')
    logging.debug(f'{len(holdings)} office holdings successfully loaded out of {len(holdings_df)} rows.')

    exchaequer_df = pd.read_csv('chancellor_of_the_exchequer.csv', sep=',')
    exchaequer_df['started_service'] = pd.to_datetime(exchaequer_df['started_service'], format=DATE_FORMAT2)
    exchaequer_df['ended_service'] = pd.to_datetime(exchaequer_df['ended_service'], format=DATE_FORMAT2)

    pm_df = pd.read_csv('prime_ministers.csv', sep=',')
    pm_df['started_service'] = pd.to_datetime(pm_df['started_service'], format=DATE_FORMAT2)
    pm_df['ended_service'] = pd.to_datetime(pm_df['ended_service'], format=DATE_FORMAT2)

    hit = 0
    ambiguities = 0
    numrows = 0
    index = 0

    from speakerfinder import worker_function

    inq = Queue()
    outq = Queue()

    logging.info('Loading processes...')

    processes = [Process(target=worker_function, args=(inq, outq, holdings, full_alias_dict, misspellings_dict, exchaequer_df, pm_df)) for _ in range(cores)]

    for p in processes:
        p.start()

    missed_df = pd.DataFrame()
    ambiguities_df = pd.DataFrame()

    missed_indexes = []
    ambiguities_indexes = []

    logging.info('Loading text...')

    for chunk in pd.read_csv(DATA_FILE, sep=',', chunksize=CHUNK_SIZE):
        t0 = time.time()
        for index, row in chunk.iterrows():
            target = row['speaker'].lower()
            speechdate = datetime.strptime(row['speechdate'], '%Y-%m-%d')

            inq.put((index, target, speechdate))

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
