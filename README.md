# Hansard Speaker Disambiguation

(intro to the problem)
the 19th-century British Parliamentary debates (also known as Hansard) 

Pre-processing the Hansard data for text mining is done in two major phases: 
  1) During phase I we scrape and correct the Hansard data provided by UK Parliament as raw XML files. We then export the corrected data as a TSV file for accessible text mining. For code the applies to phase I, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).
  5) During phase II we disambiguate speakers. 

This respository serves to a) document the problems associated with speaker name disambiguation, and b) provide our disambiguation pipeline. We also collected (data) to match with and replace speaker names, which will be addresssed in greater detail below. The data we used (enter) can be downloaded here: 


### Issues 



The algorithm works by (describe pipeline): 
a) 
b) 
c) 




### Issues in Speaker Name Disambiguation

We identify (X) major issues in speaker name disambiguation: 

1) Prolific members of parliament often held several office positions, and Hansard usually does not specify the name of the MP who held the position. 
  - Consider William Ewart Gladstone who acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. The original UK XML usually does not specify the name of the MP who held the position, it just tags the position title (i.e. Prime Minister) as the full name of the speaker. 

2) A single name has several permutations. 
  - Consider again William Ewart Gladstone who might have been called William Gladstone, W. Gladstone, W. E. Gladstone, William E. Gladstone, and so forth. 

3) Several Parliamentarians shared the exact same name.
  - Consider __Sir Robert Peel__--a name assigned to three different Parliamentarians. For cases like this, additional data was collected to determine the start and end dates of the different Sir Robert Peels. 
  - Consider, also, how some speakers share elements of their name. __Mr. Gladstone__ or __Mr. W. Gladstone__ might refer to __William Ewart Gladstone__ or __William Henry Gladstone__. 

4) OCR ERRORS 



### About the Hansard Speaker Disambiguation Algorithm

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




We use edit distance carefully applied to different subsections: 
1) last names and whatever else Alexander said 
2) maybe office titles 


Before

using 

Note that we hit less than 30 % even after I added permutations. Talk about that progression. 

