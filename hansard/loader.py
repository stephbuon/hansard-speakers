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
    elif type(date_str) == str and (not len(date_str) or date_str == 'nan'):
        if start:
            return f'1700{splitchr}01{splitchr}01'
        else:
            return f'1910{splitchr}01{splitchr}01'
    elif type(date_str) == float and numpy.isnan(date_str):
        if start:
            return f'1700{splitchr}01{splitchr}01'
        else:
            return f'1910{splitchr}01{splitchr}01'
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

        # self.title_df = pd.read_csv('data/hansard_titles.csv')
        # self.title_df = self.title_df[~self.title_df['corresponding_id'].isna()]
        # self.title_df = self.title_df.astype({'corresponding_id': int})
        # self.title_df['start_search'] = pd.to_datetime(self.title_df['start_search'], format=DATE_FORMAT)
        # self.title_df['end_search'] = pd.to_datetime(self.title_df['end_search'], format=DATE_FORMAT)
        # self.title_df['alias'] = self.title_df['alias'].str.lower().str.replace('\'', '', regex=False)

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
                df = self._check_date_estimates(df, 'start_search', 'end_search')
            except AttributeError:
                raise Exception(f'Invalid dates in file: {csv}')
            df = df[['corresponding_id', 'real_name', 'start_search', 'end_search', 'alias']]

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
        dfs = []
        for csv in os.listdir('data/mps/military-titles'):
            print('Loading name alias csv:', csv)
            df = pd.read_csv('data/mps/military-titles/' + csv, sep=',')
            dfs.append(df)
        self.aliases_df = pd.concat(dfs)
        self.aliases_df['real_name'] = self.aliases_df['real_name'].str.lower()
        self.aliases_df['alias'] = self.aliases_df['alias'].str.lower()
        self.aliases_df = self._check_date_estimates(self.aliases_df, 'start_search', 'end_search')
        self.aliases_df = self.aliases_df[['corresponding_id', 'real_name', 'start_search', 'end_search', 'alias']]
        self.aliases_df = self.aliases_df[~self.aliases_df['alias'].isnull()]

    def _load_speakers(self):
        self._load_name_aliases()

        mps: pd.DataFrame = pd.read_csv('data/mps/speakers-names/speakers.csv', sep=',')
        mps['dod'] = mps['dod'].fillna(datetime.now().strftime(DATE_FORMAT))
        mps['dob'] = pd.to_datetime(mps['dob'], format=DATE_FORMAT)
        mps['dod'] = pd.to_datetime(mps['dod'], format=DATE_FORMAT)
        mps = mps.astype({'corresponding_id': int})

        malformed_mp_date = 0
        malformed_mp_name = 0
        missing_fn_name = 0
        missing_sn_name = 0

        speakers = self.speakers
        speaker_dict = self.speaker_dict
        alias_dict = self.alias_dict

        for index, row in mps.iterrows():
            dob = row['dob']

            if pd.isna(dob):
                dob = datetime(day=1, month=1, year=1700)

            dod = row['dod']
            if pd.isna(dod):
                # Assume that the speaker is still alive.
                dod = datetime.now()

            fullname, firstname, surname = row['speaker_name'], row['first_name'], row['last_name']

            if type(firstname) != str:
                missing_fn_name += 1
                logging.debug(f'Missing first name at row: {index}. Fullname is {row["speaker_name"]}. Surname is {row["last_name"]}.')
                continue
            elif type(surname) != str:
                missing_sn_name += 1
                logging.debug(f'Missing surname at row: {index}. Fullname is {row["speaker_name"]}. First name is {row["first_name"]}.')
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
                speaker = SpeakerReplacement(fullname, firstname, surname, row['corresponding_id'], dob, dod)
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

        # self.corrections.update(
        #     DataStruct.load_correction_csv_as_dict(f'{folder}/misspellings_dictionary.csv', encoding='ISO-8859-1'))
        #
        # misspellings2 = pd.read_csv(f'{folder}/misspelled_given_names.tsv', sep='\t', encoding='ISO-8859-1')
        #
        # if misspellings2['correct_name'].isnull().sum():
        #     raise ValueError('misspelled_given_names.tsv has an invalid entry')
        #
        # self.corrections.update({k.lower(): v for k, v in zip(misspellings2['misspelled_name'], misspellings2['correct_name'])})

        # self.corrections.update(
        #     DataStruct.load_correction_csv_as_dict(f'{folder}/common_OCR_errors_titles.csv'))

    @staticmethod
    def _load_office_position(filename: str) -> pd.DataFrame:
        df = pd.read_csv(filename)
        df['start_search'] = df['start_search'].astype(str)
        df['end_search'] = df['end_search'].astype(str)

        if "honorary_title" not in df:
            df['honorary_title'] = None

        start_column = 'start_search'
        end_column = 'end_search'

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
        holdings_df = pd.read_csv('data/mps/office-holdings/office-holdings.csv', sep=',')
        old_length = len(holdings_df)
        holdings_df = self._check_date_estimates(holdings_df, 'start_search', 'end_search')
        holdings_df = holdings_df.astype({'office_id': int})
        holdings_df = holdings_df[holdings_df['corresponding_id'].isin(speaker_dict.keys())]
        holdings_df = holdings_df[holdings_df['office_id'].isin(office_dict.keys())]
        self.holdings_df = holdings_df

        logging.debug(f'{len(holdings_df)} office holdings successfully loaded out of {old_length} rows.')

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

        # self._load_office_positions()

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

        temp_df = pd.concat(df[['corresponding_id', 'honorary_title', 'start_search', 'end_search']]
                            for df in self.office_position_dfs.values())
        temp_df = temp_df[~(temp_df['honorary_title'].isna()) & ~(temp_df['corresponding_id'].isna())]
        temp_df['honorary_title'] = temp_df['honorary_title'].str.lower()
        temp_df['honorary_title'] = temp_df['honorary_title'].str.replace(r'[^a-zA-Z\- ]', '', regex=True)
        self.honorary_titles_df = temp_df.copy()
