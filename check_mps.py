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
        return 'MISSING_FIRSTNAME'

    if surname not in nameparts:
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
