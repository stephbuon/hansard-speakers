# Hansard Speaker Name Disambiguation

Digital methods are becoming increasingly important in the interpretation of the 19th-century Parliamentary debates, also known as Hansard. Some analyses of Hansard, however, can be thwarted by messy data. For this reason we present a preprocessing pipeline that produces the cleanest version of the Hansard data.

Preprocessing the Hansard data is done in two major phases: 

- During phase I we scrape the Hansard data hosted by UK Parliament, transforming the raw XML files into a TSV file. We chose TSV because of it is a popular file format used in applications from text mining to data base construction. While scrapin gthe Hansard data, our team discovered systematic issues in the XML tags (describe). For code the applies to phase I, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).

- During phase II we disambiguate speakers. Even after correcting for systemtic issues in the data, some 

such as 
analyses having to do with speaker names 
 
- This repository documents the problems associated with ambiguous speaker names and presents our pipeline for (enter). 

### Issues that Cause Ambiguous Speaker Names

We identify 5 major issues that cause ambiguities in speaker names: 

1) Prolific members of parliament often held several office positions. Hansard usually does not specify the name of the MP who held the position, refering to the MP as just their office title. In cases where a single MP held numerous offices, this problem becomes more tangled. William Ewart Gladstone, for example, acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. The original XML usually does not specify the name of the MP who held the position, it just tags the position title (i.e. Prime Minister) as the full name of the speaker. 

2) A single name has several permutations. For example, William Ewart Gladstone might have been called William Gladstone, W. Gladstone, W. E. Gladstone, Wiliam E. Gladstone, and so forth. 

3) Several MPs shared the exact same name. For example, three different Parliamentarians were named Sir Robert Peel. In cases like this, metadata was collected to try and make distinctions betweent the different speakers. Metadata may include the start and end dates of the diferent Sir Robert Peels. Another example might be that some speakers share elements of their name. Mr Gladstone or Mr. W. Gladstone might refer to William Ewart Gladstone or Willaim Henry Gladstone. 

4) Many names have OCR errors. 

greater detail below. 

5) spelling inconsistencies (campbell-bannerman) 

To address the above issues, we have developed (enter). 

### About the Hansard Speaker Disambiguation Algorithm

The algorithm works by (describe pipeline): 

We disambiguate by: 

The purpose of our project is to thus: 
a) disambiguate between the different MPs who have held a single office title 
b) detect the permuations of a single name (so that permutations are counted as the same MP)

We use edit distance carefully applied to different subsections: 
1) last names and whatever else  
2) maybe office titles 


Thus we: 

generated permutations

Note that we hit less than 30 % (get exact number) even after I added permutations. Talk about that progression. 



### About the Data 

We also collected additional data to 

(data) to match with and replace speaker names, which will be addresssed in greater detail in About the Data. The data we used (enter) can be downloaded here: 


We obtained our original data sets from the DiLPD project, located [here](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml), and the Andy Eggers and Arthur Spirling database, located here. While these impressive and comprehensive data sets offer insight into Parliamentary speakers, they did not have the (standardization or identification) required for text mining speaker names. 

collected additional data from various online sources 
from sources like Hansard People, etc. 

### Comparison of our Data 







Speaker Name Inferences
Much of the metadata we use to match speaker was dilligently and painstakingly hand collected. 

Too many 
for example, even after

over 100,000 instances 

half a million 
too much for a human interpreter. 


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





