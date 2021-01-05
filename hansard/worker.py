import multiprocessing
from queue import Empty
from hansard.loader import DataStruct


# This function will run per core.
def worker_function(inq: multiprocessing.Queue,
                    outq: multiprocessing.Queue,
                    data: DataStruct):
    from . import cleanse_string

    misspellings_dict = data.corrections
    exchaequer_df = data.exchequer_df
    pm_df = data.pm_df
    holdings = data.holdings
    alias_dict = data.alias_dict
    terms_df = data.term_df

    while True:
        try:
            i, speechdate, target = inq.get(block=True)
        except Empty:
            continue
        else:
            match = None
            ambiguity: bool = False
            target = cleanse_string(target)
            possibles = []
            query = None

            for misspell in misspellings_dict:
                if misspell in target:
                    target = target.replace(misspell, misspellings_dict[misspell])

            target = cleanse_string(target)

            # Don't count these as ambigious for now
            # TODO: need to add MP id to the CSV's.
            if 'exchequer' in target:
                query = exchaequer_df[(speechdate >= exchaequer_df['started_service']) & (speechdate < exchaequer_df['ended_service'])]
                if len(query) == 1:
                    target = query.iloc[0]['real_name'].lower()
                    match = target
                elif len(query) > 1:
                    ambiguity = True

            elif 'prime minister' in target:
                query = pm_df[(speechdate >= pm_df['started_service']) & (speechdate < pm_df['ended_service'])]
                if len(query) == 1:
                    target = query.iloc[0]['real_name'].lower()
                    match = target
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

            if ambiguity:
                speaker_ids = {speaker.id for speaker in possibles}

                query = terms_df[(terms_df['member.id'].isin(speaker_ids)) &
                                 (terms_df['start_term'] <= speechdate) &
                                 (speechdate <= terms_df['end_term'])]
                if len(query) == 1:
                    ambiguity = False
                    match = query.iloc[0]['fullname'].lower()

            outq.put((match is not None, ambiguity, i))
