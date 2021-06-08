# Hansard Speaker Name Disambiguation

Text mnining methods, such as topic modeling, collocate extraction, or word embeddings, are becoming increasingly important for interpreting the 19th-century British Parliamentary debates, also known as Hansard. Analyses of Hansard, however, can be thwarted by messy data. We present a preprocessing pipeline that produces the cleanest known version of the Hansard data. The final dataset produced by this pipeline can be downloaded [here](). 

Preprocessing the Hansard data is performed in two major phases: 

- During phase I we scrape the Hansard data hosted by UK Parliament, transforming the raw XML files into a TSV file. We chose TSV because it is a popular file format used in computation and within the digital humanities. While scraping the data, we discovered systematic issues in the XML tags. Debate text, for example, might be tagged as a debate title, while other sections might be missing tags in their entirety. In result (thought missing). For code that corrects these systematic issues and exports a clean TSV file, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).

- During phase II we disambiguate speakers. Even after correcting for systemtic issues in the data, accurate analysis of speakers was not possible because of ambiguities and inconsistencies in the names of members of Parliament (MPs). This repository documents the problems associated with identifying the speakers of each sentence, and presents a pipeline for disambiguating speaker names by assigning a unique name, comprised of a standardized name and unique ID, to each speaker of a sentence. 

### About the Problems Causing Ambiguous Speakers
We identify and correct for 5 major issues that cause ambiguities in speaker names: 

1) Prolific members of parliament often held several office positions and the name of the MP holding the position is usually not mentioned. The XML hosted by the [historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html) often only tags the position title (i.e., Prime Minister) as the full name of the speaker. This problem is especially pronounced in cases where a single MP held numerous offices. William Ewart Gladstone, for example, acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. Determining which instances a title can be accredited to William Ewart Gladstone is paramount for accurate analyses of speakers. 

2) A single name has several permutations. During a debate, William Ewart Gladstone might have been called William Gladstone, W. Gladstone, W. E. Gladstone, Wiliam E. Gladstone, and so forth. Without detecting and replacing each permutation with a distinct, standardized name, the pervasiveness of permutations can be misleading for analysis. 

3) Several MPs shared the same name. Three different Parliamentarians, for example, were named Sir Robert Peel. In cases like this, metadata was collected to help make distinctions betweent the different speakers. Metadata may include the start and end dates of the different speakers with a shared name. In other cases, some speakers share elements of their name, causing ambiguity. Mr Gladstone or Mr. W. Gladstone, for example, might refer to William Ewart Gladstone or Willaim Henry Gladstone. 

4) Many MP names have OCR errors. The original debates were hand-recorded with inkwell pens (check). Handwriting can pose challenges for digitization efforts. The technologies used to parse and tag the original, hand recorded debates developed over time, and many of the earlier 19th-century debates were digitized and tagged using now outdated technologies from the 1980s. While these early digitization efforts were important milestones for the production of the Hansard data, the output from these early technologies are prone to error. The number of distinct errors can be exacerbated by the permutations of speaker names, where each form of a name can contain OCR errors. 

5) Many MP names have inconsistent spellings. "Sir Henry Campbell-Bannerman," for example, might be transcribed as "Campbell Bannerman," or "Campbell - Bannerman." While each spelling can be considered correct, these differences can erranously register as different speakers. 

To address the above issues we have developed a speaker disambiguation pipeline that assigns a unique name, comprised of a standardized name and unique ID, to each speaker of a sentence. 

### About the Hansard Speaker Disambiguation Pipeline
Our speaker disambiguation efforts include: a) collecting extensive metadata about MPs, b) adding missing MPs to existing data sets, and c) implementing our `hansard-speakers` algorithm, which will be described in greater detail in the following section. 

#### Data 
An important step in disambiguating speakers is collecting additional metadata about speakers. This metadata is called used to match unique names with the names of speakers. The data our pipeline identifies speakers with includes: a) existing data sets, b) new data sets aggregated by Democracy Lab's research assistants, and c) data generated by the Hansard speakers disambiguation algorithm. 

The existing data sets used by our pipeline were generously provided by: a) the [DiLPD project](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml), and b) the [Andy Eggers and Arthur Spirling database](http://andy.egge.rs/eggers_spirling_database.html). 

These impressive data sets are foundational to our work, providing speaker names and relevant metadata. On their own, however, these data sets do not contain the total information required to disambiguate speaker names. Therefore, RAs collected extensive metadata from various sources such as [the historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html), (enter), (enter). Our metadata can be downloaded as csv files [here]().

This metadata greatly improved the detection and disambiguation of speaker names, but it does not help detect the many permutations of a single MP name. The total number of permutations a single name might have is unknown. Therefore, the Hansard speakers disambiguation algorithm generates an exhaustive list of every possible permutation for each MP name. 




and exhaustive list of every possible permutation for each MP name. 


data is generated by the Hansard speakers disambiguation algorithm 



is outlined 





#### Algorithm

The algorithm works by (describe pipeline): 

- cleaning ocr errors in the mr etc. 


- removing certain types of titles
- generating permutations of speaker names to include: enter 


Permutations are generated by 


Therefore, a name with four items can have X permutations: 

Example: 

```

William Heald Ludlow Bruges

Mr. Bruges
William Bruges
W. Bruges
W. H. Bruges
W. H. L. Bruges
William H. Bruges
William H. L. Bruges
William Heald L. Bruges
William H. Ludlow Bruges


```

with and without periods


Names with (enter) are (enter). 

George de la Poer Beresford

In any case 



- matching speakers (mention corresponding ids) 

After enter, we apply levenshtein distance 

- using levenshtein distance to fuzzy match -- carefully and delibrerately applied to different subsections -- last names, office titles 



We do not fuzzy match permutations of names with initials because  

based on dates? 


- using inference. 

Lastly, we infer remaining speakers' true names. Even after collecting extensive amounts of metadata on MPs, (percent of conflicts) speakers could not, at this stage, be disambiguated. Either this was because (enter). This issue was especially pronounced in cases where the MP was highly active in Parliament and had multiple family members who were also Parliamentarians, MPs such as Mr. Gladstone, Mr. Hume, Mr. Disraeli, and more. Therefore (we disambiguate). These conflicts may occur up to 100,000 times per speaker, making determining the speaker by reading each debate nearly impossible. Instead, the true names of these remaining speakers are infered.

This step was applied last because of the inherent uncertainties in infering the true names of speakers as opposed to the (relative certainty of the other methods). (with great care). 

The `hansard-speakers` Wiki documents (enter). The rules and assumptions for infering speakers can be found [here](https://github.com/stephbuon/hansard-speakers/wiki/Hansard-Speaker-Names-Inferences). A full list of sentence IDs where the speaker was infered can be found on the Wiki [here](), or downloaded as a csv file [here](). 

(random sampling accuracy?)

### Comparing Results
Our pipeline significantly improves speaker recognition compared to existing data sets. The DiLPD data and the Eggers and Spirling data combined only matches with X% of the Hansard data. 

Hits: percentage of speakers
Misses: 
Unidentified: percentage of speakers who are not MPs and are not identified by the present pipeline. 

REMMEBER TO CHANGE THIS SO IT DOESNT INCLUDE NAMES LIKE WITNESS AS MISSES
MAYBE HAVE TOTAL UNIDENIFIED SPEAKERS  
![before_comparison](https://github.com/stephbuon/hansard-speakers/blob/main/images/before_hansard_speakers.png)



#### Precision and Recall of Hansard Speaker Names


#### About the Unidentified Speakers 
Our pipeline disambiguates and standardizes the names of MPs in Hansard. Subsequently, speakers who are not MPs are not identified, as this problem is beyond the scope of the present project. These speakers (enter), or might simply be called by the name of "witness." It is important to note that these unidentified speakers serve an important role in the debates and that record of these speakers is crucial to history. Those who spoke in Parliament, but are not MPs, might include women, people of color, and people of another nationality than British. 

A list of unidentified speakers (with their sentence ID, enter, enter) can be viewed [here](), or downloaded as a csv file [here]().

