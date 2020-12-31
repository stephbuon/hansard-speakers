from datetime import datetime
import multiprocessing
from queue import Empty
import re


# This function will run per core.
def worker_function(inq: multiprocessing.Queue, outq: multiprocessing.Queue, holdings, full_alias_dict, misspellings_dict,
                    exchaequer_df, pm_df):
    from . import cleanse_string

    while True:
        try:
            i, target, speechdate = inq.get(block=True)
        except Empty:
            continue
        else:
            match = None
            ambiguity = False
            possibles = None

            target = cleanse_string(target)

            for misspell in misspellings_dict:
                if misspell in target:
                    target = target.replace(misspell, misspellings_dict[misspell])

            target = cleanse_string(target)

            if 'exchequer' in target:
                query = exchaequer_df[(speechdate >= exchaequer_df['started_service']) & (speechdate < exchaequer_df['ended_service'])]
                if len(query) >= 1:
                    target = query.iloc[0]['real_name'].lower()
            elif target == 'prime minister':
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

            outq.put((match is not None, ambiguity, i))
