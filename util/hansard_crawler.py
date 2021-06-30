import calendar
import random
import string
import time
from typing import Tuple, NamedTuple, Optional, List

from bs4 import BeautifulSoup

import requests

import re

from multiprocessing import Pool
import os

from datetime import datetime

WORKER_COUNT = 4


class Person(NamedTuple):
    prefix: str
    first_name: str
    last_name: str
    dob: str
    dod: str
    lord_memberships: List[str]
    alternative_names: List[str]
    alternative_titles: List[str]


def search_people(letter: str):
    print('Beginning letter: ', letter)

    try:
        page = requests.get(f'http://api.parliament.uk/historic-hansard/people/{letter}')
    except requests.exceptions.ConnectionError:
        time.sleep(random.uniform(1, 3))
        print('Retrying fetch for letter:', letter)
        return search_people(letter)

    soup = BeautifulSoup(page.content, 'html.parser')
    people_ol = soup.find('ol')
    if not people_ol:
        print('Could not find people for letter:', letter)
        return []

    people = people_ol.find_all('a')
    hrefs = [person['href'] for person in people]
    print('href count for letter ', letter, ':', len(hrefs))
    with Pool(WORKER_COUNT) as p:
        people = p.map(crawl_person, hrefs)
    return [p for p in people if p is not None]


DATE_REGEX = r'(?:(January +|February +|March +|April +|May +|June +|July +|August +|September +|October +|November +|December +)([0-9]?[0-9],? ))?([0-9]{4})'

FULL_DATE_REGEX = re.compile(f'{DATE_REGEX} - {DATE_REGEX}')


def crawl_person(href):
    print('Crawling href: ', href)
    try:
        page = requests.get(f'http://api.parliament.uk/historic-hansard/people/{href}')
    except requests.exceptions.ConnectionError:
        time.sleep(random.uniform(1, 3))
        print('Retrying href: ', href)
        return crawl_person(href)

    soup = BeautifulSoup(page.content, 'html.parser')

    page_content = soup.find('div', {'class': 'page'})

    name_h1 = soup.find('h1', {'class': 'vcard'})
    prefix = name_h1.find('span', {'class': 'honorific-prefix'})
    given_name = name_h1.find('span', {'class': 'given-name'})
    family_name = name_h1.find('span', {'class': 'family-name'})

    date = page_content.contents[2].strip().replace(',', '')
    if date.startswith('-'):
        dob = None
        dod = date[1:]
    elif date.endswith('-'):
        dob = date[:-1]
        dod = None
    else:
        dob, dod = date.split('-')

    if dob is not None:
        dob = re.sub(' +', ' ', dob)

        if re.search('19[0-9][0-9]', dob) is not None:
            # Ignore MPs born after 1900
            return None
        if re.search('1[789][0-9][0-9]', dob) is None:
            # Ignore MPs born before 1700
            return None

    if dod is not None:
        dod = re.sub(' +', ' ', dod)

    lord_memberships = soup.find_all('li', {'class': 'lords-membership'})
    alternative_names = soup.find_all('li', {'class': 'alternative-name'})
    alternative_titles = soup.find_all('li', {'class': 'alternative-title'})

    return Person(
        prefix=prefix.text if prefix else 'N/A',
        first_name=given_name.text if given_name else 'N/A',
        last_name=family_name.text if family_name else 'N/A',
        dob=dob.strip() if dob else 'N/A',
        dod=dod.strip() if dod else 'N/A',
        lord_memberships=[t.text.replace(',', '') for t in lord_memberships],
        alternative_names=[t.text.replace(',', '') for t in alternative_names],
        alternative_titles=[t.text.replace(',', '') for t in alternative_titles]
    )


MONTHS = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


def parse_title(title):
    match = re.search(FULL_DATE_REGEX, title)

    if match is None:
        raise Exception('Could not find date in string: %s' % title)

    span = match.span()
    title = title[:span[0]].strip()

    start_month, start_day, start_year, end_month, end_day, end_year = match.groups()

    if start_year is None:
        start_day = 1700
    else:
        start_year = int(start_year)

    if start_month is None:
        start_month = 'January'

    start_month = MONTHS[start_month.strip()]

    if start_day is None:
        start_day = 1
    else:
        start_day = int(start_day)

    if end_year is None:
        end_year = 2000
    else:
        end_year = int(end_year)

    if end_month is None:
        end_month = 'December'

    end_month = MONTHS[end_month.strip()]

    if end_day is None:
        end_day = calendar.monthrange(end_year, end_month)[1]
    else:
        end_day = int(end_day)

    start = f'{start_year}-{start_month:02}-{start_day:02}'
    end = f'{end_year}-{end_month:02}-{end_day:02}'

    return title, start, end


def parse_date_string(dob, is_start):
    try:
        date = datetime.strptime(dob, '%B %d %Y')
        return date.strftime('%Y-%m-%d')
    except ValueError:
        year = int(dob)
        if is_start:
            month = 1
            day = 1
        else:
            month = 12
            day = calendar.monthrange(year, month)[1]

        return f'{year}-{month:02}-{day:02}'


def main():
    outfile = open('hansard_titles.csv', 'w+')
    outfile.write('prefix,firstname,surname,dob,dod,alias_type,alias,start,end\n')

    for letter in string.ascii_lowercase:
        for person in search_people(letter):
            if person.dob != 'N/A':
                dob = parse_date_string(person.dob, is_start=True)
            else:
                dob = person.dob
            if person.dod != 'N/A':
                dod = parse_date_string(person.dod, is_start=False)
            else:
                dod = person.dod
            temp = f'{person.prefix},{person.first_name},{person.last_name},{dob},{dod}'

            for lord_title in person.lord_memberships:
                lord_title, start, end = parse_title(lord_title)
                line = f'{temp},lord_membership,{lord_title},{start},{end}\n'
                outfile.write(line)

            for alt_name in person.alternative_names:
                alt_name, start, end = parse_title(alt_name)
                line = f'{temp},alternative_name,{alt_name},{start},{end}\n'
                outfile.write(line)

            for alt_title in person.alternative_titles:
                alt_title, start, end = parse_title(alt_title)
                line = f'{temp},alternative_title,{alt_title},{start},{end}\n'
                outfile.write(line)

    outfile.close()


if __name__ == '__main__':
    main()
