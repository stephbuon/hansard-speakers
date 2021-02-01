import multiprocessing
from queue import Empty
from hansard.loader import DataStruct
from datetime import datetime
import pandas as pd


def match_term(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    return df[(date >= df['started_service']) & (date < df['ended_service'])]


# This function will run per core.
def worker_function(inq: multiprocessing.Queue,
                    outq: multiprocessing.Queue,
                    data: DataStruct):
    from . import cleanse_string

    misspellings_dict = data.corrections
    holdings = data.holdings
    alias_dict = data.alias_dict
    terms_df = data.term_df
    speaker_dict = data.speaker_dict

    exchaequer_df = data.exchequer_df
    pm_df = data.pm_df
    lord_chance_df = data.lord_chance_df
    ag_df = data.attorney_general_df

    hitcount = 0
    missed_indexes = []
    ambiguities_indexes = []

    while True:
        try:
            chunk: pd.DataFrame = inq.get(block=True)
        except Empty:
            continue
        else:
            if chunk is None:
                # This is our signal that we are done here. Every other worker thread will get a similar signal.
                break
            
            for i, speechdate, target in chunk.itertuples():
                match = None
                ambiguity: bool = False
                target = cleanse_string(target)
                possibles = []
                query = None

                for misspell in misspellings_dict:
                    if misspell in target:
                        target = target.replace(misspell, misspellings_dict[misspell])

                target = cleanse_string(target)

                if 'exchequer' in target:
                    query = match_term(exchaequer_df, speechdate)
                elif 'prime minister' in target:
                    query = match_term(pm_df, speechdate)
                elif 'lord chancellor' in target:
                    query = match_term(lord_chance_df, speechdate)
                elif 'attorney general' in target:
                    query = match_term(ag_df, speechdate)

                if query is not None:
                    if len(query) == 1:
                        speaker_id = query.iloc[0]['corresponding_id']
                        if speaker_id != 'N/A':
                            # TODO: setup logging to keep track of when == n/a
                            # TODO: fix IDs missing due to being malformed entries in mps.csv
                            # match = speaker_dict[int(speaker_id)]
                            # for now use speaker_id to ensure this counts as a match
                            match = speaker_id
                    elif len(query) > 1:
                        ambiguity = True

                # can we get ambiguities with office names?
                if not match:
                    for holding in holdings:
                        if holding.matches(target, speechdate, cleanse=False):
                            match = holding
                            break

                if not match:
                    possibles = alias_dict.get(target)
                    if possibles is not None:
                        possibles = [speaker for speaker in possibles if speaker.matches(target, speechdate, cleanse=False)]
                        if len(possibles) == 1:
                            match = possibles[0]
                        else:
                            ambiguity = True

                if ambiguity and possibles:
                    speaker_ids = {speaker.id for speaker in possibles}

                    query = terms_df[(terms_df['member.id'].isin(speaker_ids)) &
                                     (terms_df['start_term'] <= speechdate) &
                                     (speechdate <= terms_df['end_term'])]
                    if len(query) == 1:
                        ambiguity = False
                        match = query.iloc[0]['fullname'].lower()

                if match is not None:
                    hitcount += 1
                elif ambiguity:
                    ambiguities_indexes.append(i)
                else:
                    missed_indexes.append(i)

            outq.put((hitcount, chunk.loc[missed_indexes, :], chunk.loc[ambiguities_indexes, :]))
            hitcount = 0
            del missed_indexes[:]
            del ambiguities_indexes[:]
