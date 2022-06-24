import os
from typing import Dict, List, Optional, Tuple, Set

import numpy
import pandas as pd
from hansard import DATE_FORMAT, DATE_FORMAT2, MP_ALIAS_PATTERN, cleanse_string
from hansard.speaker import SpeakerReplacement, OfficeHolding, Office, OfficeTerm
from hansard.exceptions import *
from datetime import datetime
import logging
import calendar
import re


def fix_estimated_date(date_str, start=True, splitchr='/'):
    if type(date_str) == int:
        date = [str(date_str, )]
    else:
        date = date_str.split(splitchr)

    if len(date) == 3:
        # No changes as its already Year-Month-Day
        return date_str
    elif len(date) == 1:
        # Year only estimate.
        if start:
            return f'{date_str}{splitchr}1{splitchr}1'
        else:
            return f'{date_str}{splitchr}12{splitchr}31'
    elif len(date) == 2:
        # Year-Month estimate.
        if start:
            return f'{date_str}{splitchr}1'
        else:
            year, month = map(int, date)
            # calendar.monthrange(year, month)[1] gives us the last day of the month, takes leap years into account.
            return f'{date_str}{splitchr}{calendar.monthrange(year, month)[1]}'
    elif not len(date):
        raise ValueError('invalid date string')


class DataStruct:
    def __init__(self):
        self.speakers: List[SpeakerReplacement] = []
        self.speaker_dict: Dict[int, SpeakerReplacement] = {}
        self.alias_dict: Dict[str, List[SpeakerReplacement]] = {}

        self.corrections: Dict[str, str] = {}

        self.office_dict: Dict[int, Office] = {}
        self.holdings: List[OfficeHolding] = []

        self.term_df: Optional[pd.DataFrame] = None
        self.honorary_titles_df: Optional[pd.DataFrame] = None
        self.office_position_dfs: Dict[str, pd.DataFrame] = {}
        self.lord_titles_df: Optional[pd.DataFrame] = None
        self.aliases_df: Optional[pd.DataFrame] = None

        # Debate id -> member id
        self.inferences: Dict[int, int] = {}

        # title string -> member id
        self.title_df: Optional[pd.DataFrame] = None

        # ignored set of speaker names
        self.ignored_set: Set[str] = set()

    @staticmethod
    def _check_date_estimates(df, start_column, end_column):
        date_format = DATE_FORMAT2 if df[start_column].str.contains('/', regex=False).any() else DATE_FORMAT
        splitchr = '/' if date_format == DATE_FORMAT2 else '-'
        df[start_column] = df[start_column].map(lambda x: fix_estimated_date(x, start=True, splitchr=splitchr))
        df[start_column] = pd.to_datetime(df[start_column], format=date_format)

        date_format = DATE_FORMAT2 if df[end_column].str.contains('/', regex=False).any() else DATE_FORMAT
        splitchr = '/' if date_format == DATE_FORMAT2 else '-'
        df[end_column] = df[end_column].map(lambda x: fix_estimated_date(x, start=False, splitchr=splitchr))
        df[end_column] = pd.to_datetime(df[end_column], format=date_format)
        return df

    def load(self):
        self._load_speakers()
        self._load_lord_titles()
        self._load_term_metadata()
        self._load_corrections()

        self.ignored_set = set()
        for dirpath, _, filenames in os.walk('data/non-mps'):
            for fn in filenames:
                filepath = dirpath + "/" + fn
                self.ignored_set = self.ignored_set.union(set(pd.read_csv(filepath)['non_mps'].unique()))

        self.title_df = pd.read_csv('data/hansard_titles.csv')
        self.title_df = self.title_df[~self.title_df['corresponding_id'].isna()]
        self.title_df = self.title_df.astype({'corresponding_id': int})
        self.title_df['start'] = pd.to_datetime(self.title_df['start'], format=DATE_FORMAT)
        self.title_df['end'] = pd.to_datetime(self.title_df['end'], format=DATE_FORMAT)
        self.title_df['alias'] = self.title_df['alias'].str.lower().str.replace('\'', '', regex=False)

        infer_df = pd.read_csv('data/inferences.csv')
        self.inferences = dict(infer_df.itertuples(index=False))

    def _load_lord_titles(self):
        dfs = []
        for csv in os.listdir('data/mps/peerage-titles'):
            print('Loading lord title csv:', csv)
            df = pd.read_csv('data/mps/peerage-titles/' + csv, sep=',')

            df['real_name'] = df['real_name'].str.lower()
            df['alias'] = df['alias'].str.lower()
            try:
                df = self._check_date_estimates(df, 'start', 'end')
            except AttributeError:
                raise Exception(f'Invalid dates in file: {csv}')
            df = df[['corresponding_id', 'real_name', 'start', 'end', 'alias']]

            for sp_id in df['corresponding_id']:
                if numpy.isnan(sp_id):
                    continue
                if sp_id not in self.speaker_dict:
                    raise KeyError('Speaker %s not found. From file %s' % (sp_id, csv))

            df = df[~df['alias'].isnull()]

            dfs.append(df)

        self.lord_titles_df = pd.concat(dfs)

    def _load_name_aliases(self):
        self.aliases_df = pd.DataFrame()
        # dfs = []
        # for csv in os.listdir('data/name_aliases'):
        #     print('Loading name alias csv:', csv)
        #     df = pd.read_csv('data/name_aliases/' + csv, sep=',')
        #     dfs.append(df)
        # self.aliases_df = pd.concat(dfs)
        # self.aliases_df['real_name'] = self.aliases_df['real_name'].str.lower()
        # self.aliases_df['alias'] = self.aliases_df['alias'].str.lower()
        # self.aliases_df = self._check_date_estimates(self.aliases_df, 'start', 'end')
        # self.aliases_df = self.aliases_df[['corresponding_id', 'real_name', 'start', 'end', 'alias']]
        # self.aliases_df = self.aliases_df[~self.aliases_df['alias'].isnull()]

    def _load_speakers(self):
        self._load_name_aliases()

        mps: pd.DataFrame = pd.read_csv('data/mps/speakers-names/speakers.csv', sep=',')
        mps['mp.dod'] = mps['mp.dod'].fillna(datetime.now().strftime(DATE_FORMAT))
        mps['mp.dob'] = pd.to_datetime(mps['mp.dob'], format=DATE_FORMAT)
        mps['mp.dod'] = pd.to_datetime(mps['mp.dod'], format=DATE_FORMAT)
        mps = mps.astype({'member.id': int})

        malformed_mp_date = 0
        malformed_mp_name = 0
        missing_fn_name = 0
        missing_sn_name = 0

        speakers = self.speakers
        speaker_dict = self.speaker_dict
        alias_dict = self.alias_dict

        for index, row in mps.iterrows():
            dob = row['mp.dob']

            if pd.isna(dob):
                dob = datetime(day=1, month=1, year=1700)

            dod = row['mp.dod']
            if pd.isna(dod):
                # Assume that the speaker is still alive.
                dod = datetime.now()

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
                    alias_dict.setdefault(alias, []).append(speaker)

                for alias in defined_aliases:
                    alias_dict.setdefault(alias, []).append(speaker)

            except FirstNameMissingError:
                continue
            except LastNameMissingError:
                continue

        logging.info(f'{malformed_mp_date} speakers with malformed dates', )
        logging.info(f'{malformed_mp_name} speakers with malformed fullnames', )
        logging.info(f'{missing_fn_name} speakers with malformed first names', )
        logging.info(f'{missing_sn_name} speakers with malformed surnames', )
        logging.info(f'{len(speakers)} speakers sucessfully loaded out of {len(mps)} rows.')

    @staticmethod
    def load_correction_csv_as_dict(filepath: str, encoding=None) -> dict:
        misspellings = pd.read_csv(filepath, encoding=encoding)
        misspellings['CORRECT'] = misspellings['CORRECT'].fillna('')
        return {k.lower(): v for k, v in zip(misspellings['INCORRECT'], misspellings['CORRECT'])}

    @staticmethod
    def load_correction_regex_csv(filepath: str, encoding=None) -> list:
        misspellings = pd.read_csv(filepath, encoding=encoding)
        misspellings['CORRECT'] = misspellings['CORRECT'].fillna('')
        return [(re.compile(k), v) for k, v in zip(misspellings['INCORRECT'], misspellings['CORRECT'])]

    def _load_corrections(self):
        folder = 'data/pre_corrections'

        self.corrections.update(
            DataStruct.load_correction_csv_as_dict(f'{folder}/misspellings_dictionary.csv', encoding='ISO-8859-1'))

        misspellings2 = pd.read_csv(f'{folder}/misspelled_given_names.tsv', sep='\t', encoding='ISO-8859-1')

        if misspellings2['correct_name'].isnull().sum():
            raise ValueError('misspelled_given_names.tsv has an invalid entry')

        self.corrections.update({k.lower(): v for k, v in zip(misspellings2['misspelled_name'], misspellings2['correct_name'])})

        self.corrections.update(
            DataStruct.load_correction_csv_as_dict(f'{folder}/common_OCR_errors_titles.csv'))

    @staticmethod
    def _load_office_position(filename: str) -> pd.DataFrame:
        df = pd.read_csv(filename)
        df['start'] = df['start'].astype(str)
        df['end'] = df['end'].astype(str)

        if "honorary_title" not in df:
            df['honorary_title'] = None

        start_column = 'start'
        end_column = 'end'

        return DataStruct._check_date_estimates(df, start_column, end_column)

    def _load_term_metadata(self):
        speaker_dict = self.speaker_dict
        office_dict = self.office_dict
        holdings = self.holdings

        logging.info('Loading offices...')
        offices_df = pd.read_csv('data/titles/office_titles.csv', sep=',')
        offices_df = offices_df.astype({'office_id': int})
        for index, row in offices_df.iterrows():
            office = Office(row['office_id'], row['name'])
            self.office_dict[office.id] = office

        logging.info('Loading office holdings...')
        holdings_df = pd.read_csv('data/officeholdings.csv', sep=',')
        holdings_df = holdings_df.astype({'oh_id': int, 'member_id': int, 'office_id': int})
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

        self.term_df = pd.read_csv('data/mps/speakers-names/speakers_terms.csv', sep=',')
        self.term_df['start_term'] = pd.to_datetime(self.term_df['start_term'], format=DATE_FORMAT)
        self.term_df['end_term'] = pd.to_datetime(self.term_df['end_term'], format=DATE_FORMAT)

        for row in self.term_df[(~self.term_df['member_id'].isnull()) & (self.term_df['member_id'] != -1)].itertuples(index=False):
            try:
                speaker_dict[int(row.member_id)].terms.append(OfficeTerm(row.start_term, row.end_term))
            except KeyError as e:
                print('Invalid corresponding speaker id: %d' % row.member_id)
                print(row)
                raise e

        self._load_office_positions()

    def _load_office_positions(self):
        directory = 'data/mps/offices'

        self.office_position_dfs = {}

        for csv in os.listdir(directory):
            try:
                df = self._load_office_position(f'{directory}/{csv}')
                name = cleanse_string(df['alias'][0])
                self.office_position_dfs[name] = df

                for row in df[~df['corresponding_id'].isnull()].itertuples(index=False):
                    self.speaker_dict[int(row.corresponding_id)].terms.append(OfficeTerm(row.start, row.end))
            except Exception as e:
                print('Error while parsing file:', csv)
                raise e

            print('Loaded office position:', name)

        temp_df = pd.concat(df[['corresponding_id', 'honorary_title', 'start', 'end']]
                            for df in self.office_position_dfs.values())
        temp_df = temp_df[~(temp_df['honorary_title'].isna()) & ~(temp_df['corresponding_id'].isna())]
        temp_df['honorary_title'] = temp_df['honorary_title'].str.lower()
        temp_df['honorary_title'] = temp_df['honorary_title'].str.replace(r'[^a-zA-Z\- ]', '', regex=True)
        self.honorary_titles_df = temp_df.copy()
