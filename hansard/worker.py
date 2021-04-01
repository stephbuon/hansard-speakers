import multiprocessing
from queue import Empty
from typing import Tuple, Optional

from hansard.loader import DataStruct
from datetime import datetime
import pandas as pd
import re

from util.edit_distance import within_distance_four, within_distance_two, is_distance_one


compile_regex = lambda x: (re.compile(x[0]), x[1])


REGEX_PRE_CORRECTIONS = [
    (r'(?:\([^()]+\))', ''),  # Remove all text within parenthesis, including parenthesis    
]

REGEX_PRE_CORRECTIONS = list(map(compile_regex, REGEX_PRE_CORRECTIONS))

REGEX_POST_CORRECTIONS = [

    # Regex for misspelled leading the
    ('^this +', 'the '),
    ('^thr +', 'the '),
    ('^then +', 'the '),
    ('^tee +', 'the '),
    ('^thh +', 'the '),
    ('^tue +', 'the '),
    ('^tmk +', 'the '),
    ('^tub +', 'the '),
    ('^he +', 'the '),
    ('^tim +', 'the '),
    ('^tme +', 'the '),
    ('^tihe +', 'the '),
    ('^thk +', 'the '),
    ('^thb +', 'the '),
    ('^tre +', 'the '),

    ('^the +', ''),  # Remove leading "the"

    ('^me +', 'mr '),  # Leading me -> mr
    ('^mb +', 'mr '),
    ('^mer +', 'mr '),
    ('^mh +', 'mr '),
    ('^mil +', 'mr '),
    ('^mk +', 'mr '),
    ('^mp +', 'mr '),
    ('^ma +', 'mr '),
    ('^mi +', 'mr '),
    
    ('^marquis +', 'marquess '),
    ('^mauquess +', 'marquess '),
    ('^manquess +', 'marquess '),
    ('^marguess +', 'marquess '),
    ('^marquees +', 'marquess '),
    ('^marques +', 'marquess '),
    ('^marquese +', 'marquess '),
    ('^marquese +', 'marquess '),
    ('^marquesss +', 'marquess '),
    ('^mabquess +', 'marquess '),
    ('^maeqttess +', 'marquess '),
    ('^maequess +', 'marquess '),
    ('^marqdess +', 'marquess '),
    ('^marqiess +', 'marquess '),
    ('^marqtjess +', 'marquess '),
    
    ('^vicount +', 'viscount '),
    ('^vicsount +', 'viscount '),
    ('^vis- count +', 'viscount '),
    ('^viscocnt +', 'viscount '),
    ('^viscodnt +', 'viscount '),
    ('^viscolunt +', 'viscount '),
    ('^viscotint +', 'viscount '),
    ('^viscotjnt +', 'viscount '),
    ('^viscouint +', 'viscount '),
    ('^viscoun +', 'viscount '),
    ('^viscouxt +', 'viscount '),
    ('^viscwnt +', 'viscount '),
    ('^visoount +', 'viscount '),
    ('^vtscount +', 'viscount '),
    ('^viscuont +', 'viscount '),
    ('^viscoust +', 'viscount '),
    ('^viscounty +', 'viscount '),
    ('^visct +', 'viscount '),
    ('^lord viscount +', 'viscount '),

    ('^lerd +', 'lord '),
    ('^lobd +', 'lord '),
    ('^loan +', 'lord '),
    ('^load +', 'lord '),
    ('^lokd +', 'lord '),
    ('^lold +', 'lord '),
    ('^lore +', 'lord '),
    ('^lorn +', 'lord '),
    ('^lorrd +', 'lord '),
    ('^lors +', 'lord '),
    ('^losd +', 'lord '),
    ('^lose +', 'lord '),
    ('^lour +', 'lord '),
    ('^lrd +', 'lord '),
    ('^ord +', 'lord '),

    ('^earb +', 'earl '),
    ('^ear +', 'earl '),

    ('^dike +', 'duke '),

    # Fix leading Sir
    ('^sib +', 'sir '),
    ('^sin +', 'sir '),
    ('^sit +', 'sir '),
    ('^sip +', 'sir '),
    ('^siu +', 'sir '),
    ('^sik +', 'sir '),
    ('^sat +', 'sir '),
    ('^sie +', 'sir '),
    ('^silt +', 'sir '),
    ('^sri +', 'sir '),
    ('^sr +', 'sir '),
    ('^str +', 'sir '),
    ('^air +', 'sir '),
    ('^si +', 'sir '),
    ('^sdi +', 'sir '),
    
    ('^abmiral +', 'admiral '),
    ('^admtral +', 'admiral '),
    ('^admieal +', 'admiral '),
    ('^abmiral +', 'admiral '),
    ('^admiraj +', 'admiral '),
    
    ('^cafiain +', 'captain '),
    ('^caftain +', 'captain '),
    ('^caitain +', 'captain '),
    ('^capain +', 'captain '),
    ('^capatain +', 'captain '),
    ('^capiain +', 'captain '),
    ('^capt +', 'captain '),
    
    ('^col +', 'colonel '),
    ('^colconel +', 'colonel '),
    ('^coionel +', 'colonel '),
    ('^colnel +', 'colonel '),
    ('^colokel +', 'colonel '),
    ('^colonal +', 'colonel '),
    ('^colonbl +', 'colonel '),
    
    ('^eirst +', 'first '),
    ('^fiest +', 'first '),
    
    ('^bistiop +', 'bishop '),
    ('^bisliop +', 'bishop '),
    ('^bisiiop +', 'bishop '),
    ('^bistiop +', 'bishop '),
    ('^lord bishop +', 'bishop '),
    
    ('^ge neral  +', 'general '),
    ('^gen  +', 'general '),
    ('^genebal  +', 'general '),
    ('^generai  +', 'general '),
    ('^genekal  +', 'general '),
    ('^genenal  +', 'general '),
    ('^genera  +', 'general '),
    
    ('chancellor of the e xciiequer', 'chancellor of the exchequer'),
    ('chancellor of the exchequer-chequer', 'chancellor of the exchequer'),
    ('changellor of the exche-quer', 'chancellor of the exchequer'),
    ('chancellor the exchequee', 'chancellor of the exchequer'),
    ('chancellor of theexche-quer', 'chancellor of the exchequer'),
    ('chancellor of we exchequer', 'chancellor of the exchequer'),
    ('cbancellor of the exche-quer', 'chancellor of the exchequer'),
    ('\bchan of the exchequer\b', 'chancellor of the exchequer'),
    ('\bchancellor the exchequee\b', 'chancellor of the exchequer'),
    ('\bchanc of the excheq\b', 'chancellor of the exchequer'),
    ('\bchancellok of the exche-quek\b', 'chancellor of the exchequer'),
    ('\bchancellor of the exchequerchequer\b', 'chancellor of the exchequer'),
    ('\bchanc of the exchequer\b', 'chancellor of the exchequer'),
    ('\bchanc of the exchequer\b', 'chancellor of the exchequer'),
    ('\bchancelloe of the exche-quer\b', 'chancellor of the exchequer'),
    ('\bchanc of tie excheq\b', 'chancellor of the exchequer'),
    ('\bchanckllor of the exchequer\b', 'chancellor of the exchequer'),
    ('\bchancellor of file exchequer\b', 'chancellor of the exchequer'),
    ('\bchancelloerof the exche-quer\b', 'chancellor of the exchequer'),
    ('\bchancelloe of the ex-chequee\b', 'chancellor of the exchequer'),
    ('\bchancelloe of the exchequer\b', 'chancellor of the exchequer'),
    
    ('memberconstituencymemberconstituency', ''), # is this necessary? Seems this pattern has been removed elsewhere. Check with Alexander. 
    
    ('^a +', ''),
    ('^and +', ''),
    ('^answered by +', ''),
    ('^another +', ''),
    ('^both +', ''),
    ('^by +', ''),
    ('^here +', ''),
    
    (' on$', ''),
    (' said$', ''),
    (' ampc$', ''),
    (' i$', ''),
    (' replied$', ''),
    (' continued$', ''),
    (' presumed$', ''),
    (' resumed$', ''),
    (' resuming$', ''),
    (' also$', ''),
    (' felt$', ''),
    
    ('irelandland', 'ireland'),
    
    (' tiie ', ' the '),
    (' tile ', ' the '),
]

REGEX_POST_CORRECTIONS = list(map(compile_regex, REGEX_POST_CORRECTIONS))


def match_term(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    return df[(date >= df['started_service']) & (date < df['ended_service'])]


def match_edit_distance_df(target: str,  date: datetime, df: pd.DataFrame,
                           columns: Tuple[str, str, str]) -> Tuple[Optional[str], bool]:
    start_col, end_col, search_col = columns

    match = None
    ambiguity = False

    condition = (date >= df[start_col]) & (date < df[end_col])
    query = df[condition]

    for alias in query[search_col]:
        if within_distance_two(target, alias, False):
            if match:
                match = None
                ambiguity = True
                break
            else:
                match = alias

    return match, ambiguity


# This function will run per core.
def worker_function(inq: multiprocessing.Queue,
                    outq: multiprocessing.Queue,
                    data: DataStruct):
    from . import cleanse_string

    # Lookup optimization
    misspellings_dict = data.corrections
    holdings = data.holdings
    alias_dict = data.alias_dict
    terms_df = data.term_df
    speaker_dict = data.speaker_dict
    honorary_title_df = data.honorary_titles_df
    office_title_dfs = data.office_position_dfs
    lord_titles_df = data.lord_titles_df
    aliases_df = data.aliases_df

    hitcount = 0
    missed_indexes = []
    ambiguities_indexes = []

    MATCH_CACHE = {}
    MISS_CACHE = set()
    AMBIG_CACHE = set()

    edit_distance_dict = {}  # alias -> list[speaker id's]

    for speaker in data.speakers:
        for alias in speaker.generate_edit_distance_aliases():
            edit_distance_dict.setdefault(alias, []).append(speaker.member_id)

    def postprocess(string_val: str) -> str:
        for k, v in REGEX_POST_CORRECTIONS:
            string_val = re.sub(k, v, string_val)
        return string_val.strip()

    def preprocess(string_val: str) -> str:
        for k, v in REGEX_PRE_CORRECTIONS:
            string_val = re.sub(k, v, string_val)

        string_val = cleanse_string(string_val)
        for misspell in misspellings_dict:
            string_val = string_val.replace(misspell, misspellings_dict[misspell])
        string_val = cleanse_string(string_val)
        return postprocess(string_val)

    while True:
        try:
            chunk: pd.DataFrame = inq.get(block=True)
        except Empty:
            continue
        else:
            if chunk is None:
                # This is our signal that we are done here. Every other worker thread will get a similar signal.
                return

            chunk['speaker_modified'] = chunk['speaker'].map(preprocess)

            for i, speechdate, unmodified_target, target in chunk.itertuples():
                if (target, speechdate) in MISS_CACHE:
                    missed_indexes.append(i)
                    continue
                elif (target, speechdate) in AMBIG_CACHE:
                    ambiguities_indexes.append(i)
                    continue

                match = MATCH_CACHE.get((target, speechdate), None)
                ambiguity: bool = False
                possibles = []
                query = []

                if not match and not len(query):
                    # Try honorary title
                    condition = (speechdate >= honorary_title_df['started_service']) &\
                                (speechdate < honorary_title_df['ended_service']) &\
                                (honorary_title_df['honorary_title'].str.contains(target, regex=False))
                    query = honorary_title_df[condition]

                if not match and not len(query):
                    # try lord/viscount/earl aliases.
                    condition = (speechdate >= lord_titles_df['start']) &\
                                (speechdate < lord_titles_df['end']) &\
                                (lord_titles_df['alias'].str.contains(target, regex=False))
                    query = lord_titles_df[condition]

                if not match and not len(query):
                    # try name aliases.
                    condition = (speechdate >= aliases_df['start']) &\
                                (speechdate < aliases_df['end']) &\
                                (aliases_df['alias'].str.contains(target, regex=False))
                    query = aliases_df[condition]

                if not match and not len(query):
                    # Try office position
                    for position in office_title_dfs:
                        if position in target or within_distance_four(position, target, True):
                            query = match_term(office_title_dfs[position], speechdate)
                            break

                if not match:
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

                # Try edit distance with lord titles.
                if not match and not ambiguity:
                    match, ambiguity = match_edit_distance_df(target, speechdate, lord_titles_df,
                                                              ('start', 'end', 'alias'))

                # Try edit distance with honorary titles.
                if not match and not ambiguity:
                    match, ambiguity = match_edit_distance_df(target, speechdate, honorary_title_df,
                                                              ('started_service', 'ended_service', 'honorary_title'))

                # Try edit distance with MP name permutations.
                if not match and not ambiguity:
                    possibles = []
                    for alias in edit_distance_dict:
                        if len(possibles) > 1:
                            break
                        if is_distance_one(target, alias):
                            for speaker_id in edit_distance_dict[alias]:
                                speaker = speaker_dict[speaker_id]
                                if speaker.start_date <= speechdate <= speaker.end_date:
                                    possibles.append(speaker)

                    if len(possibles) == 1:
                        match = possibles[0]
                    elif len(possibles) > 1:
                        ambiguity = True

                if ambiguity and possibles:
                    speaker_ids = {speaker.member_id for speaker in possibles}

                    query = terms_df[(terms_df['member.id'].isin(speaker_ids)) &
                                     (terms_df['start_term'] <= speechdate) &
                                     (speechdate <= terms_df['end_term'])]
                    if len(query) == 1:
                        ambiguity = False
                        match = query.iloc[0]['fullname'].lower()

                if match is not None:
                    hitcount += 1
                    MATCH_CACHE[(target, speechdate)] = match
                elif ambiguity:
                    AMBIG_CACHE.add((target, speechdate))
                    ambiguities_indexes.append(i)
                else:
                    MISS_CACHE.add((target, speechdate))
                    missed_indexes.append(i)

            outq.put((hitcount, chunk.loc[missed_indexes, :], chunk.loc[ambiguities_indexes, :]))
            hitcount = 0
            del missed_indexes[:]
            del ambiguities_indexes[:]
