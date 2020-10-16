from datetime import datetime
import multiprocessing
from queue import Empty


# This function will run per core.
def worker_function(inq: multiprocessing.Queue, outq: multiprocessing.Queue, holdings, full_alias_dict):
    while True:
        try:
            i, target, speechdate = inq.get(block=True)
        except Empty:
            continue
        else:
            match = None
            ambiguity = False
            possibles = None

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
