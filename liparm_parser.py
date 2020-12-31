from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from dataclasses import dataclass

from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd


@dataclass
class Member:
    fullname: str
    first_name: str
    surname: str
    id: int
    title: str = ''
    start_term: str = ''
    end_term: str = ''
    dob: str = ''
    dod: str = ''
    location: str = ''


tree = ElementTree.parse('westminster-members.xml')

xml_namespace = '{http://www.loc.gov/mads/v2}'


def tagname(name):
    return f'{xml_namespace}{name}'


root: Element = tree.getroot()
assert str(root.tag) == tagname('madsCollection')


def parse_name(e_authority: Element) -> Tuple[str, str, str]:
    title = []
    first_name = []
    last_name = []

    e_name: Element = e_authority.find(tagname('name'))

    for e_namepart in e_name.iterfind(tagname('namePart')):
        if e_namepart.attrib['type'] == 'family':
            last_name.append(e_namepart.text)
        elif e_namepart.attrib['type'] == 'given':
            first_name.append(e_namepart.text)
        elif e_namepart.attrib['type'] == 'termsOfAddress':
            if e_namepart.text is not None:
                title.append(e_namepart.text)
        elif e_namepart.attrib['type'] == 'date':
            pass
        else:
            raise ValueError

    return ' '.join(title), ' '.join(first_name), ' '.join(last_name)


MEMBERS = []


ids = set()


for mad in root:  # type: Element
    authority: Optional[Element] = None
    variants: List[Element] = []
    identifier: Optional[Element] = None
    extension: Optional[Element] = None

    for element in mad:
        if element.tag == tagname('authority'):
            assert authority is None
            authority = element
        elif element.tag == tagname('variant'):
            variants.append(element)
        elif element.tag == tagname('identifier'):
            assert identifier is None
            identifier = element
        elif element.tag == tagname('extension'):
            assert extension is None
            extension = element

    assert identifier.attrib['type'] == 'Rush Individual ID'
    member_id = int(identifier.text)
    title, first_name, last_name = parse_name(authority)
    fullname = ' '.join([title, first_name, last_name])

    s_dob = ''
    s_dod = ''

    if extension.find(tagname('dateOfBirth')) is not None:
        s_dob = extension.find(tagname('dateOfBirth')).text
    if extension.find(tagname('dateOfDeath')) is not None:
        s_dod = extension.find(tagname('dateOfDeath')).text

    dob = datetime.strptime(s_dob, '%Y-%m-%d') if s_dob else None
    dod = datetime.strptime(s_dod, '%Y-%m-%d') if s_dod else None

    if dob and dob.year >= 1900:
        continue

    e_constituency = extension.find(tagname('constituency'))

    start_term = None
    end_term = None
    location = None

    if e_constituency is not None:
        start_term = e_constituency.attrib['dateOfElection']
        end_term = e_constituency.attrib.get('dateOfExit', None)
        location = e_constituency.text

        if start_term.startswith('19') or start_term.startswith('20'):
            continue

    if member_id in ids:
        raise KeyError('duplicate id: %d' % member_id)

    ids.add(member_id)

    member = Member(
        fullname=fullname,
        first_name=first_name,
        surname=last_name,
        id=member_id,
        title=title,
        start_term=start_term,
        end_term=end_term,
        dob=s_dob,
        dod=s_dod,
        location=location,
    )

    MEMBERS.append(member.__dict__)


df = pd.DataFrame(
    MEMBERS,
    columns=['fullname', 'title', 'first_name', 'surname', 'id', 'start_term', 'end_term', 'dob', 'dod', 'location']
)
df.set_index('id', inplace=True)
df.to_csv('data/liparm_members.csv', sep=',')
