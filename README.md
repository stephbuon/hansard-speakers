# hansard-speakers

The purpose of this repository is to 

share speaker-name data 
the 19th-century British Parliamentary debates (also known as Hansard) 


For replicability, this repository shows the code
as well as the speaker-name dictionaries 


### Speaker Name Dictionaries 




Preparing the Hansard data is done in multiple phases: 

1) Stage I (ENTER RE stuff). 

Imports the Hansard data: https://github.com/stephbuon/import_hansard_data

2) Stage II (ENTER) 

This repository is dedicated to Stage II, cleaning the Hansard speaker names. 

Stage I outputs a data set (enter description)

Stage II performs the following tasks: 

They 

for text mining. 

We identify (X) major issues in speaker name disambiguation: 

1) Prolific members of parliament often held several office positions throughout their time in Parliament. Consider William Ewart Gladstone who acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. (from the default UK data, could not differentiate between which Parliamentary was holding office at a particular time). 

2) A single name might have several permutations within the debate text. Consider again William Ewart Gladstone who might have been called William Gladstone, W. Gladstone, W. E. Gladstone, William E. Gladstone, and so forth. 


he could have been called by his office title or a permutation of his name. 


3) Several Parliamentarians shared the exact same name, like __Sir Robert Peel__--a name assigned to three different Parliamentarians, or speakers might share elements of thier name. __Mr. Gladstone__ or __Mr. W. Gladstone__, for instance, might refer to __William Ewart Gladstone__ or __William Henry Gladstone__. 



The purpose of our project is to thus: 
a) disambiguate between the different MPs who have held a single office title 
b) detect the permuations of a single name (so that permutations are counted as the same MP)




We disambiguate by: 



dates of birth and death (as provided by the DILPAD and spirling data) 

and in some cases the dates of activity 


## Compared to Existing data sets


largest known data sets for Parliamentary speaker name data 

We obtained our original set (the set before our collection and algorithm) of speaker name data from two major sources: 

- An XML file derived from the Digging into Linked Parliamentary Data (DiLPD) project, located [here](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml). 
- The Andy Eggers and Arthur Spirling database, which lists the MPs associated with (enter), located here. 

While these impressive and comprehensive data sets offer a wealth of information about Parliamentary speakers, scraped from (enter), they lack don't have the identification required for text mining. 




Before

using 

Note that we hit less than 30 % even after I added permutations. Talk about that progression. 

