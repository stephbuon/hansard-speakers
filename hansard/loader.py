from typing import Dict, List, Optional
import pandas as pd
from hansard import DATE_FORMAT, DATE_FORMAT2, MP_ALIAS_PATTERN
from hansard.speaker import SpeakerReplacement, OfficeHolding, Office
from hansard.exceptions import *
from datetime import datetime
import logging


class DataStruct:
    def __init__(self):
        self.speakers: List[SpeakerReplacement] = []
        self.speaker_dict: Dict[int, SpeakerReplacement] = {}
        self.alias_dict: Dict[str, List[SpeakerReplacement]] = {}

        self.corrections: Dict[str, str] = {}

        self.office_dict: Dict[int, Office] = {}
        self.holdings: List[OfficeHolding] = []

        self.exchequer_df: Optional[pd.DataFrame] = None
        self.pm_df: Optional[pd.DataFrame] = None
        self.term_df: Optional[pd.DataFrame] = None

    def load(self):
        self._load_speakers()
        self._load_offices()
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

        ocr_title_errs: pd.DataFrame = pd.read_csv('data/common_OCR_errors_titles.csv', sep=',')
        ocr_title_errs['CORRECT'] = ocr_title_errs['CORRECT'].fillna('')
        ocr_err_dict = {k.lower(): v for k, v in zip(ocr_title_errs['INCORRECT'], ocr_title_errs['CORRECT'])}
        self.corrections.update(ocr_err_dict)

    def _load_offices(self):
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

        self.exchequer_df = pd.read_csv('data/chancellor_of_the_exchequer.csv', sep=',')
        self.exchequer_df['started_service'] = pd.to_datetime(self.exchequer_df['started_service'], format=DATE_FORMAT2)
        self.exchequer_df['ended_service'] = pd.to_datetime(self.exchequer_df['ended_service'], format=DATE_FORMAT2)

        self.pm_df = pd.read_csv('data/prime_ministers.csv', sep=',')
        self.pm_df['started_service'] = pd.to_datetime(self.pm_df['started_service'], format=DATE_FORMAT2)
        self.pm_df['ended_service'] = pd.to_datetime(self.pm_df['ended_service'], format=DATE_FORMAT2)

        self.term_df = pd.read_csv('data/liparm_members.csv', sep=',')
        self.term_df['start_term'] = pd.to_datetime(self.term_df['start_term'], format=DATE_FORMAT)
        self.term_df['end_term'] = pd.to_datetime(self.term_df['end_term'], format=DATE_FORMAT)
