# Hansard Speaker Name Disambiguation

Digital methods are becoming increasingly important in the interpretation of the 19th-century British Parliamentary debates, also known as Hansard. Analyses of Hansard, however, can be thwarted by messy data. For this reason we present a preprocessing pipeline that produces the cleanest known version of the Hansard data. The final dataset produced by this pipeline can be downloaded [here](). 

Preprocessing the Hansard data is done in two major phases: 

- During phase I we scrape the Hansard data hosted by UK Parliament, transforming the raw XML files into a TSV file. We chose TSV because it is a popular file format used in computation. While scraping the Hansard data, our team discovered systematic issues in the XML tags. Debate text, for example, might be tagged as a debate title, while other sections might be missing tags in their entirety. For code that corrects these systematic issues and exports a cleaned TSV file, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).

- During phase II we disambiguate speakers. Even after correcting for systemtic issues in the data, accurate analyses of speakers were not possible because of ambiguities and inconsistencies in speaker names. This repository documents the problems associated with speaker names and presents our pipeline for disambiguation. 

### Issues that Cause Ambiguous Speaker Names

We identify and correct 5 major issues that cause ambiguities in speaker names: 

1) Prolific members of parliament often held several office positions, and the name of the MP who held the position is usually not mentioned. This problem becomes more pronounced in cases where a single MP held numerous offices. William Ewart Gladstone, for example, acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. The original XML usually just tags the position title (i.e. Prime Minister) as the full name of the speaker. 

2) A single name has several permutations. During a debate, William Ewart Gladstone might have been called William Gladstone, W. Gladstone, W. E. Gladstone, Wiliam E. Gladstone, and so forth. 

3) Several MPs shared the same name. Three different Parliamentarians, for example, were named Sir Robert Peel. In cases like this, metadata was collected to help make distinctions betweent the different speakers. Metadata may include the start and end dates of the diferent Sir Robert Peels. Another example might be that some speakers share elements of their name. Mr Gladstone or Mr. W. Gladstone might refer to William Ewart Gladstone or Willaim Henry Gladstone. 

4) Many MP names have OCR errors. The original debates were hand-recorded with inkwell pens (check). (present challenges for digitization). Many early debates were digitized and tagged using technology from the 1980s. (while important milestone, enter). 

5) Many MP names have inconsistent spelling. Sir Henry Campbell-Bannerman, for example, might be transcribed as "Campbell Bannerman," or "Campbell - Bannerman."

To address the above issues, we have developed a speaker disambiguation pipeline (enter). 

### About the Hansard Speaker Disambiguation Pipeline

(enter).

#### About the Algorithm

The algorithm works by (describe pipeline): 

- cleaning ocr errors in the mr etc. 
- removing certain types of titles
- generating permutations of speaker names 
- matching speakers (mention about corresponding ids) 
- using levenshtein distance to enter -- carefully and delibrerately applied to different subsections -- last names, office titles 




Thus we: 

generated permutations

Note that we hit less than 30 % (get exact number) even after I added permutations. Talk about that progression. 



#### About the Data 

Our pipeline calls data from existing sets as well as o

(produces own -- generates permuataions and collect metadata). 

The existing data sets our pipeline uses are from: a) the [DiLPD project](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml), and b) the [Andy Eggers and Arthur Spirling database](). 

These impressive and comprehensive data sets were foundational to (enter). However, they did not have the (standardization or identification) required for text mining speaker names. Therefore, we: a) generated permuations of speaker names within algorithm amd b) collected metadata to help disambiguate speaker names, such as metadata on (enter). (sources like Hansard People, etc.) Our metadata can be downloaded [here](). 

### Comparison of our Data 






Speaker Name Inferences 

Even after collecting extensive metadata on (enter), (enter). (enter) a high number of conflicts where a 




Too many 
for example, even after

over 100,000 instances 

half a million 
too much for a human interpreter. 

These conflicts make up (enter)% of our data. 


Therefore, we developed a set of assumptions 


The full list of sentence IDs belonging to inferred speakers can be found here. 


Sometimes speakers 



No I believe it is due to the position Gladstone had made for himself so he earned it out of respect I just checked and there does not seem to be any specific reason why a person is called right honorable. (So not synonymous with a position like prime minister)
3:59
He did not have a title so I guess in a way they gave him respect by adressing him like that
3:59
He is the only Gladstone who is called right honourable
:+1:
1

4:00
The only gladstone who has a title is Viscount Gladstone





