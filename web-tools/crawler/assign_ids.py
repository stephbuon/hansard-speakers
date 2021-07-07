import pandas as pd
import numpy as np


DATE_FORMAT = '%Y-%m-%d'

if __name__ == '__main__':
    df = pd.read_csv('hansard_titles.csv')
    df['dob'] = pd.to_datetime(df['dob'], format=DATE_FORMAT)
    df['dod'] = pd.to_datetime(df['dod'], format=DATE_FORMAT)
    df['start'] = pd.to_datetime(df['start'], format=DATE_FORMAT)
    df['end'] = pd.to_datetime(df['end'], format=DATE_FORMAT)
    df['corresponding_id'] = np.nan

    from hansard.loader import DataStruct
    data = DataStruct()
    data.load()

    matches = 0
    misses = 0
    ambig = 0

    indexes = []

    for row in df.itertuples():
        i = row[0]
        if pd.isna(row.prefix) and pd.isna(row.firstname):
            name = f'{row.surname}'
        elif pd.isna(row.firstname):
            name = f'{row.prefix} {row.surname}'
        else:
            name = f'{row.firstname} {row.surname}'
        possible_speakers = [speaker for speaker in data.speakers if speaker.matches(name, row.start)]

        if len(possible_speakers) == 1:
            df.loc[i, 'corresponding_id'] = int(possible_speakers[0].member_id)
            matches += 1
        elif len(possible_speakers) == 0:
            indexes.append(i)
            misses += 1
        else:
            indexes.append(i)
            ambig += 1

    # missed_df = df.loc[indexes, :]
    # missed_df.to_csv('missed_titles.csv', index=False)

    df.to_csv('hansard_titles2.csv', index=False)
