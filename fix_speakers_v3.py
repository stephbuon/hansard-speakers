import os

import pandas as pd
from datetime import datetime
from typing import Dict, List, Set, Union
import logging
import time
import re
import sys
from multiprocessing import Process, Queue, cpu_count


DATE_FORMAT = '%Y-%m-%d'

MP_ALIAS_PATTERN = re.compile(r'\(([^\)]+)\)')


class FirstNameMissingError(Exception):
    pass


class LastNameMissingError(Exception):
    pass


class SpeakerAmbiguityError(Exception):
    pass


class SpeakerReplacement:
    def __init__(self, full_name, first_name, last_name, member_id, start, end):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()

        name_parts = full_name.lower().split()

        try:
            fn_index = name_parts.index(self.first_name)
        except ValueError:
            raise FirstNameMissingError

        try:
            ln_index = name_parts.index(self.last_name)
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

    def matches(self, speaker_name: str, speech_date: datetime):
        if not self.start_date <= speech_date <= self.end_date:
            return False

        return speaker_name in self.aliases

    def __repr__(self):
        return f'SpeakerReplacement({self.id}, {self.start_date}, {self.end_date})'


class Office:
    def __init__(self, office_id, office_name):
        self.id = office_id
        self.name = office_name

        words = self.name.lower().split()
        for i, word in enumerate(words):
            if word in {'of', 'the', 'to'}:
                words[i] = f'(?: {word} | )?'

        pattern = ' '.join(words).replace(' (?:', '(?:').replace(')? ', ')?')
        self.pattern = re.compile(pattern)


class OfficeHolding:
    # TODO: check start-end dates for 19th century

    def __init__(self, holding_id, member_id, office_id, start_date, end_date, office):
        self.holding_id = holding_id
        self.member_id = member_id
        self.office_id = office_id
        self.start_date = start_date
        self.end_date = end_date
        self.office = office

    def matches(self, office_name: str, speech_date: datetime):
        office_name = office_name.strip().lower()

        if not self.start_date <= speech_date <= self.end_date:
            return False

        return self.office.pattern.match(office_name) is not None

    @property
    def speaker(self) -> SpeakerReplacement:
        return speaker_dict[self.member_id]


if __name__ == '__main__':
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logging.basicConfig(filename='logs/{:%y%m%d_%H%M%S}.log'.format(datetime.now()), format='%(asctime)s|%(levelname)s|%(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)

    # Uncomment to log to stdout as well.
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.debug('Initializing...\n')

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

    logging.info('Loading text...')

    hit = 0
    ambiguities = 0
    chunksize = 10 ** 6
    numrows = 0
    index = 0

    from speakerfinder import worker_function

    inq = Queue()
    outq = Queue()

    cores = max(cpu_count() - 1, 1)
    logging.debug(f'Utilizing {cores} cores...')
    processes = [Process(target=worker_function, args=(inq, outq, holdings, full_alias_dict)) for _ in range(cores)]

    for p in processes:
        p.start()

    missed_df = pd.DataFrame()

    missed_indexes = []

    for chunk in pd.read_csv('hansard_justnine_12192019.csv', sep=',', chunksize=chunksize):
        t0 = time.time()
        for index, row in chunk.iterrows():
            target = ' '.join(row['speaker'].split()).lower()
            speechdate = datetime.strptime(row['speechdate'], '%Y-%m-%d')
            inq.put((index, target, speechdate))

        for i in range(len(chunk)):
            if i % 1000 == 0:
                logging.debug(f'Chunk Progress: {i}/{len(chunk)}')
            is_hit, is_ambig, missed_i = outq.get()
            if is_hit:
                hit += 1
            elif is_ambig:
                ambiguities += 1
            else:
                missed_indexes.append(missed_i)

        missed_df = missed_df.append(chunk.loc[missed_indexes, :])
        del missed_indexes[:]

        numrows += len(chunk.index)
        logging.info(f'{len(chunk.index)} processed in {int((time.time() - t0) * 100) / 100} seconds')
        logging.info(f'Processed {numrows} rows so far.')

        # Uncomment break to process only 1 chunk.
        # break

    missed_df.to_csv('missed_speakers.csv')

    logging.info('Complete.')

    for process in processes:
        process.terminate()

    logging.info(f'{hit} hits')
    logging.info(f'{ambiguities} ambiguities')
    logging.info(f'{index} rows parsed')
    logging.info('Exiting...')

# TODO: aliases from mps.csv
# TODO: find_replce implementation
# TODO: send list of aliases from mps
# TODO: account for OCR errors
