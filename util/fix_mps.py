import pandas as pd
from hansard import DATE_FORMAT
from datetime import datetime
import re


mps: pd.DataFrame = pd.read_csv('mps.csv', sep=',')

mps['mp.dob'] = pd.to_datetime(mps['mp.dob'], format=DATE_FORMAT)

# Exclude anyone born after 1900. Keep any without DOB.
mps = mps[mps['mp.dob'].isna() | (mps['mp.dob'] < datetime(year=1900, month=1, day=1))]
mps.set_index('member.id', inplace=True)


TITLES = [
    'Marquess',
    'Earl',
    'Viscount',
    'Lord',
    'Viscountess',
    'Sir',
    'Mr',
    'The',
    'Duke',
    'Duchess',
    'Master',
    'Rt.',
    'Baron',
    'Baroness',
    'Countess'
]

# Join titles with OR followed by any number of characters.
titles_pattern = '|'.join((f'(?:^ ?{title} .+)'for title in TITLES))

# Find names without a first name and an alias.
missing_fn = mps[mps['mp.fname'].isnull()]
missing_fn_alias = missing_fn[missing_fn['mp.name'].str.contains(r'\)')]
missing_fn_alias = missing_fn_alias[missing_fn_alias['mp.name'].str.match(titles_pattern)]


def fix1(name):
    matches = re.findall(r'\(([^()]+)\)', name)
    if len(matches) == 1:
        if re.match(matches[0], titles_pattern) is not None:
            # There is a title within the parenthesis. Ignore it.
            return name
        else:
            # Replace with what is in the parenthesis.
            return matches[0]
    else:
        # Unexpected, don't modify the name.
        return name


missing_fn_alias['mp.name'] = missing_fn_alias['mp.name'].apply(fix1)
mps.update(missing_fn_alias, overwrite=True)

missing_fn = mps[mps['mp.fname'].isnull()]


def fix2(row):
    name = row['mp.name']

    # If we have an alias, leave it so we can manually fix it.
    if '(' in name:
        return row

    # Special case:
    if name.startswith('Baron Baron'):
        row['mp.fname'] = 'Baron'
        return row

    words = name.split()
    first_name = None

    # Find the first non-title word and set it as the first name
    for word in words:
        if word not in TITLES and word != 'of':
            first_name = word
            break

    if first_name is not None:
        row['mp.fname'] = first_name

    return row


mps.update(missing_fn.apply(fix2, axis=1), overwrite=True)
mps['mp.dob_approximate'] = mps['mp.dob_approximate'].fillna(0.0).astype(int)
mps['mp.dod_approximate'] = mps['mp.dod_approximate'].fillna(0.0).astype(int)

# Export any that still do not have a first name or DOB.
missing_fn = mps[mps['mp.fname'].isnull()]
missing_fn.to_csv('missing_fn.csv')

missing_dob = mps[mps['mp.dob'].isnull()]
missing_dob.to_csv('missing_dob.csv')

mps['mp.dob_approximate'] = mps['mp.dob_approximate'].fillna(0.0).astype(int)
mps['mp.dod_approximate'] = mps['mp.dod_approximate'].fillna(0.0).astype(int)
mps.to_csv('mps.csv')
