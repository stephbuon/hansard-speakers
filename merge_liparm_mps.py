from datetime import datetime

import pandas as pd

from fix_speakers_v3 import SpeakerReplacement, LastNameMissingError, FirstNameMissingError

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT2 = '%Y/%m/%d'


mps: pd.DataFrame = pd.read_csv('mps.csv', sep=',')
mps['mp.dob'] = pd.to_datetime(mps['mp.dob'], format=DATE_FORMAT)
mps['mp.dod'] = pd.to_datetime(mps['mp.dod'], format=DATE_FORMAT)
mps = mps[mps['mp.dob'].notnull() & mps['mp.dod'].notnull() & mps['mp.fname'].notnull() & mps['mp.sname'].notnull()]
total_mps = mps.shape[0]

members: pd.DataFrame = pd.read_csv('liparm_members.csv', sep=',')
members['first_name'] = members['first_name'].str.lower()
members['surname'] = members['surname'].str.lower()
members['fullname'] = members['fullname'].str.lower()
members['dob'] = pd.to_datetime(members['dob'], format=DATE_FORMAT)
members['dod'] = pd.to_datetime(members['dod'], format=DATE_FORMAT)
members['start_term'] = pd.to_datetime(members['start_term'], format=DATE_FORMAT)
members['end_term'] = pd.to_datetime(members['end_term'], format=DATE_FORMAT)


def first_last_query(fname, sname, dob, dod):
    return (members['first_name'] == fname) & \
           (members['surname'] == sname) & \
           (dob < members['start_term']) & \
           (members['end_term'] <= dod)


def alias_query(speaker: SpeakerReplacement, dob, dod):
    return (members['fullname'].isin(speaker.aliases)) & \
           (dob < members['start_term']) & \
           (members['end_term'] <= dod)


def lookup(row):
    fullname, firstname, surname = row['mp.name'].lower(), row['mp.fname'].lower(), row['mp.sname'].lower()

    # Currently, firstname from LIPARM includes middle names.
    firstname = firstname.split(' ')[0]

    dob, dod = row['mp.dob'], row['mp.dod']

    try:
        speaker = SpeakerReplacement(fullname, firstname, surname, row['member.id'], dob, dod)
    except LastNameMissingError:
        return
    except FirstNameMissingError:
        return

    result = members[alias_query(speaker, dob, dod)]

    if len(result):
        return result
    else:
        result = members[first_last_query(firstname, surname, dob, dod)]

        if len(result):
            return result


found = 0

for index, mp_row in mps.iterrows():
    if not (index % 100):
        print(f'Current progress: {index} / {total_mps}')
    if lookup(mp_row) is not None:
        found += 1

print(f'Matched {found}/{total_mps} mps')
