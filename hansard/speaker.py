from datetime import datetime
from typing import Set
from .exceptions import *
from . import cleanse_string
import re


class SpeakerReplacement:
    def __init__(self, full_name, first_name, last_name, member_id, start, end):
        self.first_name = cleanse_string(first_name)
        self.last_name = cleanse_string(last_name)

        name_parts = cleanse_string(full_name).split()

        # TODO: properly handle situation where first name and title are equal (ex: Baron)
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

        # Add Mr title by default.
        if 'mr' not in self.titles:
            self.titles.append('mr')

        self.middle_names = name_parts[fn_index + 1:ln_index]

        self.member_id = member_id
        self.id = f'{self.first_name}_{self.last_name}_{member_id}'

        self.middle_possibilities = list(re.sub(' +', ' ', p.strip()) for p in self._generate_middle_parts(0))

        self.aliases: Set[str] = set(self._generate_aliases())

        self.start_date: datetime = start
        self.end_date: datetime = end

    def _generate_aliases(self):
        for title in self.titles + ['']:
            for fn in ('', self.first_name[0], self.first_name):
                for mn in self.middle_possibilities:
                    yield re.sub(' +', ' ', f'{title} {fn} {mn} {self.last_name}').strip(' ')

    def _generate_middle_parts(self, i):
        if i >= len(self.middle_names):
            yield ''
            return

        # First character of middle name part followed by space
        a = self.middle_names[i][0] + ' '

        # Middle name part followed by space
        c = self.middle_names[i] + ' '

        for p in self._generate_middle_parts(i + 1):
            yield p
            yield a + p
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
