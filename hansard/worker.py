from datetime import datetime
import multiprocessing
from queue import Empty
import re
from .speaker import SpeakerReplacement, OfficeHolding
from typing import Dict, List
import pandas as pd


# This function will run per core.
def worker_function(inq: multiprocessing.Queue,
                    outq: multiprocessing.Queue,
                    holdings: List[OfficeHolding],
                    full_alias_dict: Dict[str, List[SpeakerReplacement]],
                    misspellings_dict: Dict[str, str],
                    exchaequer_df: pd.DataFrame,
                    pm_df: pd.DataFrame,
                    terms_df: pd.DataFrame):
    from . import cleanse_string

    while True:
        try:
            i, speechdate, target = inq.get(block=True)
        except Empty:
            continue
        else:
            match = None
            ambiguity = False
            target = cleanse_string(target)
            possibles = []
            query = None

            for misspell in misspellings_dict:
                if misspell in target:
                    target = target.replace(misspell, misspellings_dict[misspell])

            target = cleanse_string(target)

            if 'exchequer' in target:
                query = exchaequer_df[(speechdate >= exchaequer_df['started_service']) & (speechdate < exchaequer_df['ended_service'])]
                if len(query) >= 1:
                    target = query.iloc[0]['real_name'].lower()
            elif 'prime minister' in target:
                query = pm_df[(speechdate >= pm_df['started_service']) & (speechdate < pm_df['ended_service'])]
                if len(query) >= 1:
                    target = query.iloc[0]['real_name'].lower()

            # can we get ambiguities with office names?
            for holding in holdings:
                if holding.matches(target, speechdate, cleanse=False):
                    match = holding
                    break

            if not match:
                possibles = full_alias_dict.get(target)
                if possibles is not None:
                    possibles = [speaker for speaker in possibles if speaker.matches(target, speechdate, cleanse=False)]
                    if len(possibles) == 1:
                        match = possibles[0]
                    else:
                        ambiguity = True

            if ambiguity:
                speaker_ids = {speaker.id for speaker in possibles}

                query = terms_df[(terms_df['member.id'].isin(speaker_ids)) &
                                 (terms_df['start_term'] <= speechdate) &
                                 (speechdate <= terms_df['end_term'])]
                if len(query) == 1:
                    ambiguity = False
                    match = query.iloc[0]['fullname'].lower()

            outq.put((match is not None, ambiguity, i))
