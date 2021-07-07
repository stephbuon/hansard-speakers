# Google search missed speakers and see whether "Hansard People" or "Hansard Offices" is returned.
# If these URLs are not returned, the name is exported as a possible non-MP for an RA to validate.
# export_dir = '/home/stephbuon/projects/speaker-search/possible_non_mps/'


import os
import re
import sys
import pandas as pd
from googlesearch import search # from the google package

export_dir = '/scratch/group/pract-txt-mine/possible_non_mps/'

def import_data(input_file):
    print('Importing data...')

    missed_speakers = pd.read_csv(input_file)
    missed_speakers =  missed_speakers[missed_speakers['n'] > 50] 

    missed_speakers['speaker_name_length'] = missed_speakers['speaker_modified'].str.len()
    missed_speakers = missed_speakers[missed_speakers['speaker_name_length'] < 25]
    
    remove_pattern = ' [a-z] '
    filter = missed_speakers['speaker_modified'].str.contains(remove_pattern)
    missed_speakers = missed_speakers[~filter]
    
    return missed_speakers


def speaker_search(missed_speakers):
    print('Searching ' + str(len(missed_speakers.index)) + ' names...')
    
    address = re.compile('.*api.parliament.uk/historic-hansard/people/.*|.*api.parliament.uk/historic-hansard/offices/.*')
    
    misses = []
    cycle = 0
    
    for name in missed_speakers['speaker_modified']:
        cycle = cycle + 1
        print('Cycle: ' + str(cycle))
        
        url_list = []
        for url in search('hansard ' + name, tld='co.uk', num=7, stop=7, pause=2):
            url_list.append(url)
            
        if any(address.match(n) for n in url_list):
            pass
        else:
            misses.append(name)

    export = pd.DataFrame(misses)
    export.to_csv(export_dir + 'possible_non_mps.csv', index = False)


if __name__ == '__main__':
    try:
        input_file = sys.argv[1]
    except IndexError:
        exit('No file named ' + sys.argv[1])

    export_folder = export_dir

    if not os.path.exists(export_folder):
        os.mkdir(export_folder)

    missed_speakers = import_data(input_file)
    speaker_search(missed_speakers)
