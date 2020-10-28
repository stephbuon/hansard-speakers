from datetime import datetime
import multiprocessing
from queue import Empty
import re


# This function will run per core.
def worker_function(inq: multiprocessing.Queue, outq: multiprocessing.Queue, holdings, full_alias_dict, misspellings_dict,
                    exchaequer_df):
    while True:
        try:
            i, target, speechdate = inq.get(block=True)
        except Empty:
            continue
        else:
            match = None
            ambiguity = False
            possibles = None

            target = target.lower().strip()
            # Change multiple whitespaces to single spaces.
            target = re.sub(r' +', ' ', target)

            for misspell in misspellings_dict:
                if misspell in target:
                    target = target.replace(misspell, misspellings_dict[misspell])

            target = target.lower()

            if 'exchequer' in target:
                query = exchaequer_df[(speechdate >= exchaequer_df['started_service']) & (speechdate < exchaequer_df['ended_service'])]
                if not query.empty and len(query) > 1:
                    target = query.loc[0, 'real_name'].lower()

            # can we get ambiguities with office names?
            for holding in holdings:
                if holding.matches(target, speechdate):
                    match = holding
                    break

            if not match:
                possibles = full_alias_dict.get(target)
                if possibles is not None:
                    possibles = [speaker for speaker in possibles if speaker.matches(target, speechdate)]
                    if len(possibles) == 1:
                        match = possibles[0]
                    else:
                        ambiguity = True

            outq.put((match is not None, ambiguity, i))
