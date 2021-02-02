from typing import Dict, List, Optional
import pandas as pd
from hansard import DATE_FORMAT, DATE_FORMAT2, MP_ALIAS_PATTERN
from hansard.speaker import SpeakerReplacement, OfficeHolding, Office
from hansard.exceptions import *
from datetime import datetime
import logging
import calendar


def fix_estimated_date(date_str, start=True):
    date = date_str.split('/')

    if len(date) == 3:
        # No changes as its already Year-Month-Day
        return date_str
    elif len(date) == 1:
        # Year only estimate.
        if start:
            return f'{date_str}/1/1'
        else:
            return f'{date_str}/12/31'
    elif len(date) == 2:
        # Year-Month estimate.
        if start:
            return f'{date_str}/1'
        else:
            year, month = map(int, date)
            # calendar.monthrange(year, month)[1] gives us the last day of the month, takes leap years into account.
            return f'{date_str}/{calendar.monthrange(year, month)[1]}'


class DataStruct:
    def __init__(self):
        self.speakers: List[SpeakerReplacement] = []
        self.speaker_dict: Dict[int, SpeakerReplacement] = {}
        self.alias_dict: Dict[str, List[SpeakerReplacement]] = {}

        self.corrections: Dict[str, str] = {}
        self.regex_corrections: Dict[str, str] = {}

        self.office_dict: Dict[int, Office] = {}
        self.holdings: List[OfficeHolding] = []

        self.term_df: Optional[pd.DataFrame] = None

        self.exchequer_df: Optional[pd.DataFrame] = None
        self.pm_df: Optional[pd.DataFrame] = None
        self.lord_chance_df: Optional[pd.DataFrame] = None
        self.attorney_general_df: Optional[pd.DataFrame] = None
        self.honorary_titles_df: Optional[pd.DataFrame] = None

    def load(self):
        self._load_speakers()
        self._load_term_metadata()
        self._load_corrections()

    def _load_speakers(self):
        mps: pd.DataFrame = pd.read_csv('data/mps.csv', sep=',')
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
                # TODO: fix members without DOB
                continue

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

    def _load_corrections(self):
        misspellings = pd.read_csv('data/misspellings_dictionary.csv', sep=',', encoding='ISO-8859-1')
        misspellings['correct'] = misspellings['correct'].fillna('')
        misspellings_dict = {k.lower(): v for k, v in zip(misspellings['incorrect'], misspellings['correct'])}
        self.corrections.update(misspellings_dict)

        misspellings2 = pd.read_csv('data/misspelled_given_names.tsv', sep='\t', encoding='ISO-8859-1')
        self.corrections.update({k.lower(): v for k, v in zip(misspellings2['misspelled_name'], misspellings2['correct_name'])})

        ocr_title_errs: pd.DataFrame = pd.read_csv('data/common_OCR_errors_titles.csv', sep=',')
        ocr_title_errs['CORRECT'] = ocr_title_errs['CORRECT'].fillna('')
        ocr_err_dict = {k.lower(): v for k, v in zip(ocr_title_errs['INCORRECT'], ocr_title_errs['CORRECT'])}
        self.corrections.update(ocr_err_dict)

    @staticmethod
    def _load_office_position(filename: str) -> pd.DataFrame:
        df = pd.read_csv(f'data/{filename}')

        start_column = 'started_service'
        end_column = 'ended_service'

        df[start_column] = df[start_column].map(lambda x: fix_estimated_date(x, start=True))
        df[start_column] = pd.to_datetime(df[start_column], format=DATE_FORMAT2)

        df[end_column] = df[end_column].map(lambda x: fix_estimated_date(x, start=False))
        df[end_column] = pd.to_datetime(df[end_column], format=DATE_FORMAT2)
        return df

    def _load_term_metadata(self):
        speaker_dict = self.speaker_dict
        office_dict = self.office_dict
        holdings = self.holdings

        logging.info('Loading offices...')
        offices_df = pd.read_csv('data/offices.csv', sep=',')
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

        self.term_df = pd.read_csv('data/liparm_members.csv', sep=',')
        self.term_df['start_term'] = pd.to_datetime(self.term_df['start_term'], format=DATE_FORMAT)
        self.term_df['end_term'] = pd.to_datetime(self.term_df['end_term'], format=DATE_FORMAT)

        self.exchequer_df = self._load_office_position('chancellor_of_the_exchequer.csv')
        self.pm_df = self._load_office_position('prime_ministers.csv')
        self.lord_chance_df = self._load_office_position('lord_chancellors.csv')
        self.attorney_general_df = self._load_office_position('attorney_generals.csv')
        self.chief_sec_df = self._load_office_position('chief_secretary_ireland.csv')

        office_title_dfs = [self.exchequer_df, self.pm_df, self.lord_chance_df,
                            self.attorney_general_df, self.chief_sec_df]

        temp_df = pd.concat(df[['corresponding_id', 'honorary_title', 'started_service', 'ended_service']]
                            for df in office_title_dfs)
        temp_df = temp_df[~(temp_df['honorary_title'].isna()) & ~(temp_df['corresponding_id'].isna())]
        temp_df['honorary_title'] = temp_df['honorary_title'].str.lower()
        temp_df['honorary_title'] = temp_df['honorary_title'].str.replace(r'[^a-zA-Z\- ]', '')
        self.honorary_titles_df = temp_df.copy()
