from datetime import datetime
from typing import List

import pandas as pd
import sys
from multiprocessing import Pool

from hansard import DATE_FORMAT
from hansard.speaker import OfficeTerm

CHUNK_SIZE = 2**15


from typing import NamedTuple


class TargetSpeaker(NamedTuple):
    id: int
    aliases: List[str]
    keywords: List[str]
    terms: List[OfficeTerm]
    dob: datetime
    dod: datetime


term_df = pd.read_csv('data/liparm_members.csv', sep=',')
additions = pd.read_csv('data/liparm_additions.csv', sep=',')
term_df = term_df.append(additions)

term_df['start_term'] = pd.to_datetime(term_df['start_term'], format=DATE_FORMAT)
term_df['end_term'] = pd.to_datetime(term_df['end_term'], format=DATE_FORMAT)
query = (~term_df['member_id'].isnull()) & (term_df['member_id'] != -1)


term_dict = {}
for row in term_df[query].itertuples(index=False):
    term_dict.setdefault(int(row.member_id), []).append(OfficeTerm(row.start_term, row.end_term))

WILLIAM_E_GLADSTONE = TargetSpeaker(id=3104, aliases=['gladstone', ], keywords=['right hon.', 'prime minister'],
                                    terms=term_dict[3104],
                                    dob=datetime(year=1809, month=12, day=29), dod=datetime(year=1898, month=5, day=19))


def process_debate(df, debate_id, target):
    found = False

    within_term = False
    for term in target.terms:
        if within_term:
            break

        for date in df['speechdate']:
            if term.contains(date):
                within_term = True
                break

    if not within_term:
        return None

    for keyword in target.keywords:
        if df['text'].str.contains(keyword).any():
            found = True
            break

    if found:
        return {'debate_id': debate_id, 'speaker_id': target.id}
    else:
        return None


def main(target_speeches_filepath, hansard_filepath, output_filepath):
    target = WILLIAM_E_GLADSTONE
    print('Reading speeches...')
    speeches_df = pd.read_csv(target_speeches_filepath)
    debate_ids = set(speeches_df['debate_id'].unique())

    print('Debate count:', len(debate_ids))

    chunks = []

    print('Reading main dataset...')
    for chunk in pd.read_csv(hansard_filepath,
                             sep=',',
                             chunksize=CHUNK_SIZE,
                             usecols=['speechdate', 'speaker', 'text', 'debate_id']):  # type: pd.DataFrame
        chunk = chunk[chunk['debate_id'].isin(debate_ids)]
        chunk['speechdate'] = pd.to_datetime(chunk['speechdate'], format=DATE_FORMAT)

        if len(chunk):
            chunks.append(chunk)

    print('Preprocessing...')
    df = pd.concat(chunks)
    df['speaker'] = df['speaker'].str.lower()
    df['text'] = df['text'].str.lower()

    query = df['speaker'].notna()
    for alias in target.aliases:
        query &= ~df['speaker'].str.contains(alias)

    df = df[query]

    with Pool(4) as p:
        rows = p.starmap(process_debate, [(df[df['debate_id'] == debate_id], debate_id, target) for debate_id in debate_ids])

    rows = [row for row in rows if row]

    print('accuracy:', len(rows) / len(debate_ids))

    print('Exporting...')

    # df.to_csv('gladstone_debates.csv', index=False)

    results_df = pd.DataFrame(rows)
    results_df.to_csv('results.csv', index=False)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        target_speeches, hansard, output = sys.argv[1:]
        main(target_speeches, hansard, output)
    else:
        exit('Invalid number of arguments.\nUsage:<speeches_csv> <hansard_csv> <output_csv>')
