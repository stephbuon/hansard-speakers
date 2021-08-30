import pandas as pd
from hansard import DATE_FORMAT
from datetime import datetime

mps: pd.DataFrame = pd.read_csv('data/mps.csv', sep=',')
mps.set_index('member.id', inplace=True)

is_missing_info = mps['mp.dob'].isnull() | mps['mp.dod'].isnull() | mps['mp.fname'].isnull() | mps['mp.sname'].isnull() | mps['mp.name'].isnull()


def is_malformed(row):
    fullname = row['mp.name'].lower().strip()
    firstname = row['mp.fname'].lower().strip()
    surname = row['mp.sname'].lower().strip()

    nameparts = fullname.split()

    if '(' in fullname or '(' in firstname or '(' in surname:
        return 'PARENTHESIS'

    if firstname not in nameparts:
        if ' ' in firstname:
            return 'SPACE_IN_FIRSTNAME'
        return 'MISSING_FIRSTNAME'

    if surname not in nameparts:
        if ' ' in surname:
            return 'SPACE_IN_SURNAME'
        return 'MISSING_SURNAME'

    if nameparts.index(firstname) > 1:
        # Title more than two words
        return 'TITLE_TOO_LONG'

    return None


missing_df = mps[is_missing_info]
missing_df.to_csv('missing_info_mps.csv', sep=',')
print(f'{len(missing_df)} rows missing information.')

mps = mps[~mps['mp.fname'].isnull() & ~mps['mp.sname'].isnull() & ~mps['mp.name'].isnull()]
mps['malformed'] = mps.apply(is_malformed, axis=1)
malformed_df = mps[~mps['malformed'].isnull()]
malformed_df.to_csv('malformed_mps.csv', sep=',')
print(f'{len(malformed_df)} rows with malformed information.')


from hansard import DATE_FORMAT2


exchequer_df = pd.read_csv('data/chancellor_of_the_exchequer.csv', sep=',')
try:
    exchequer_df['started_service'] = pd.to_datetime(exchequer_df['started_service'], format=DATE_FORMAT2)
    exchequer_df['ended_service'] = pd.to_datetime(exchequer_df['ended_service'], format=DATE_FORMAT2)
except ValueError as e:
    print('Exchequer dataset has invalid dates.')
    raise e
finally:
    invalid_entries = exchequer_df[~exchequer_df['corresponding_id'].isin(mps.index)]
    if len(invalid_entries):
        print('Exchequer dataset has invalid ids.')
        for v in invalid_entries.itertuples():
            print(v)

pm_df = pd.read_csv('data/prime_ministers.csv', sep=',')
try:
    pm_df['started_service'] = pd.to_datetime(pm_df['started_service'], format=DATE_FORMAT2)
    pm_df['ended_service'] = pd.to_datetime(pm_df['ended_service'], format=DATE_FORMAT2)
except ValueError as e:
    print('prime minister dataset has invalid dates.')
    raise e
finally:
    invalid_entries = pm_df[~pm_df['corresponding_id'].isin(mps.index)]
    if len(invalid_entries):
        print('prime minister dataset has invalid ids.')
        for v in invalid_entries.itertuples():
            print(v)

try:
    lord_chance_df = pd.read_csv('data/lord_chancellors.csv', sep=',')
    lord_chance_df['started_service'] = pd.to_datetime(lord_chance_df['started_service'], format=DATE_FORMAT2)
    lord_chance_df['ended_service'] = pd.to_datetime(lord_chance_df['ended_service'], format=DATE_FORMAT2)
except ValueError as e:
    print('lord chancellor dataset has invalid dates.')
    raise e
finally:
    invalid_entries = lord_chance_df[~lord_chance_df['corresponding_id'].isin(mps.index)]
    if len(invalid_entries):
        print('lord chancellor dataset has invalid ids.')
        for v in invalid_entries.itertuples():
            print(v)
