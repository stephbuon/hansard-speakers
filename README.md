# Hansard Speaker Name Disambiguation

Text mining methods such as topic modeling, collocate extraction, or word embeddings, have become increasingly important for interpreting the 19th-century British Parliamentary debates, also known as Hansard (Blaxill 2013, Guldi 2018). Some analyses of Hansard, however, can be thwarted by messy data. The analysis of Parliamentary speakers, for example, has been inhibited by rampent inconsistencies in speaker names. A single member of Parliament (MP) might be called by many titles, different honorifics, or their name might be recorded as any combination of their first name, middle name(s), and last name(s). Speaker names are rife with OCR errors, and it may be difficult to distinguish between multiple speakers who share the same last name. The ability to perform analytics on speakers, however, is important to the advancement of our understandings of the debates and to history. 

Democracy Lab thus presents a preprocessing pipeline that produces the cleanest known version of the Hansard data including the disambiguation of speakers. The final dataset produced by this pipeline can be downloaded [here](). 

Preprocessing the Hansard data is performed in two major phases: 

- During phase I we scrape the Hansard data hosted by UK Parliament, transforming the raw XML files into a TSV file. We chose TSV because it is a popular file format used in computation generally, and within the digital humanities specifically. It can be easily imported into R or pandas. 
 
  While scraping the data, we discovered systematic issues in the XML tags. Debate text, for example, might be tagged as a debate title, while other sections might be missing tags in their entirety. In result (thought missing). For code that corrects these systematic issues and exports a clean TSV file, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).

- During phase II we disambiguate speakers. Even after correcting for systemtic issues in the data, accurate analysis of speakers was not possible because of ambiguities and inconsistencies in the names of MPs. This repository documents the problems associated with identifying the speakers of each sentence, and presents a pipeline for disambiguating speaker names by assigning a unique name, comprised of a standardized name and unique ID, to each speaker of a sentence. 

### About the Problems Causing Ambiguous Speakers
We identify and correct for 5 major issues that cause ambiguities in speaker names: 

1) Prolific members of parliament often held several office positions and the name of the MP holding the position is usually not mentioned. The XML hosted by the [historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html) often only tags the position title (i.e., Prime Minister) as the full name of the speaker. This problem is especially pronounced in cases where a single MP held numerous offices. William Ewart Gladstone, for example, acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. Determining which instances a title can be accredited to William Ewart Gladstone is paramount for accurate analyses of speakers. 

2) A single name has several permutations. During a debate, William Ewart Gladstone might have been called William Gladstone, W. Gladstone, W. E. Gladstone, Wiliam E. Gladstone, and so forth. Without detecting and replacing each permutation with a distinct, standardized name, the pervasiveness of permutations can be misleading for analysis. 

3) Several MPs shared the same name. Three different Parliamentarians, for example, were named Sir Robert Peel. In cases like this, metadata was collected to help make distinctions betweent the different speakers. Metadata may include the start and end dates of the different speakers with a shared name. In other cases, some speakers share elements of their name, causing ambiguity. Mr Gladstone or Mr. W. Gladstone, for example, might refer to William Ewart Gladstone or Willaim Henry Gladstone. 

4) Many MP names have OCR errors. The original debates were hand-recorded with inkwell pens (check). Handwriting can pose challenges for digitization efforts. The technologies used to parse and tag the original, hand recorded debates developed over time, and many of the earlier 19th-century debates were digitized and tagged using now outdated technologies from the 1980s. While these early digitization efforts were important milestones for the production of the Hansard data, the output from these early technologies are prone to error. The number of distinct errors can be exacerbated by the permutations of speaker names, where each form of a name can contain OCR errors. 

5) Many MP names have inconsistent spellings. "Sir Henry Campbell-Bannerman," for example, might be transcribed as "Campbell Bannerman," or "Campbell - Bannerman." While each spelling can be considered correct, these differences can erranously register as different speakers. 

To address the above issues we have developed a speaker disambiguation pipeline that assigns a unique name, comprised of a standardized name and unique ID, to each speaker of a sentence. 

### Organization of the Data

(Enter things like description of speaker column here)

### About the Hansard Speaker Disambiguation Pipeline
Our speaker disambiguation efforts include: a) collecting extensive metadata about MPs, b) adding missing MPs to existing data sets, and c) implementing our `hansard-speakers` disambiguation algorithm, which will be described in greater detail in the section, "Algorithm." 

#### Data 
An important step in disambiguating speakers is collecting additional metadata about speakers. This metadata is used to match unique names with the names of speakers in the speaker column. The data used includes: a) existing data sets, b) new data sets aggregated by Democracy Lab's research assistants, and c) data generated by the Hansard speakers disambiguation algorithm. 

The existing data sets used by our pipeline were generously provided by: a) the [DiLPD project](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml), and b) the [Andy Eggers and Arthur Spirling database](http://andy.egge.rs/eggers_spirling_database.html). 

These impressive data sets are foundational to our work, providing speaker names and relevant metadata. On their own, however, these data sets do not contain the total information required to disambiguate speaker names. Therefore, RAs collected extensive metadata from various sources such as [the historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html), (enter), (enter). Our metadata can be downloaded as csv files [here]().

The metadata collected by RAs greatly improved the detection and disambiguation of speaker names. However, it does not help with the detection of the many permutations of a single MP name. The total number of permutations a single name might have is unknown. Therefore, the Hansard speakers disambiguation algorithm generates an exhaustive list of every possible permutation for each MP name.

#### Algorithm
The algorithm disambiguates speakers in (X) steps: 

- cleaning OCR errors in Mr. etc 
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

Lastly, we infer remaining speakers' true names. Even after collecting extensive amounts of metadata on MPs, resolving large amounts of OCR errors, and carefully reading the Hansard debates for information about speakers, (percent of conflicts) speakers could not by this stage be disambiguated because their recorded name matched another MP active during the same period. This problem was especially pronounced in cases where the MP was highly active in Parliament and had multiple family members who were also Parliamentarians, for example, Mr. Gladstone, Mr. Hume, Mr. Disraeli, and more. Some of these conflicts may occur from 5,000 up to 100,000 sentences per MP name, making the process of determining speaker by reading each sentence nearly impossible. Instead, the true names of these remaining speakers are infered using a carefully curated set of language-based assumptions derived from specialized domain knowledge of the Hansard data.

This step was applied last because of the inherent uncertainties in infering the true names of speakers as opposed to the relative certainly of the above mentioned methods. Becuase of the inherent uncertainty in infering speakers, we approach this problem with great care, adhering to our curated set of rules derived from domain knowledge of the Hansard data. The `hansard-speakers` Wiki documents each rule, and can be viewed [here](https://github.com/stephbuon/hansard-speakers/wiki/Hansard-Speaker-Names-Inferences). 

A report on conflicting speaker names that describes the reason was infered, as well as our resolution for handling each name, can be downloaded [here](). A full list of sentences where the speaker name was infered can be viewed on the Wiki [here](), or downloaded as CSV file [here](). 

### Comparing Results
Our pipeline significantly improves speaker recognition compared to existing data sets. The DiLPD data and the Eggers and Spirling data combined only matches with X% of the Hansard data. 

Hits: percentage of identified speakers
Misses: percentage of unidentified speakers 
Unidentified: percentage of speakers who are not MPs and are not identified by the present pipeline

REMMEBER TO CHANGE THIS SO IT DOESNT INCLUDE NAMES LIKE WITNESS AS MISSES
MAYBE HAVE TOTAL UNIDENIFIED SPEAKERS  
![before_comparison](https://github.com/stephbuon/hansard-speakers/blob/main/images/before_hansard_speakers.png)

(random sampling accuracy?)

#### Precision and Recall of Hansard Speaker Names


### About the Unidentified Speakers 
Our pipeline disambiguates and standardizes the names of MPs in Hansard. Subsequently, speakers who are not MPs are not identified, as this problem is beyond the scope of the present project. These speakers (enter), or might simply be called by the name of "witness" or "voice from the Irish benches." It is important to note that these unidentified speakers serve an important role in the debates and that record of these speakers is crucial to history. Those who spoke in Parliament, but are not MPs, might include women, people of color, and people of another nationality than British. 

A list of unidentified speakers (with their sentence ID, enter, enter) can be viewed [here](), or downloaded as a csv file [here]().


### Citations 

Blaxill 2013 Blaxill, L. “Quantifying the Language of British Politics, 1880–1910”, Historical Research, 86 (2013): 313-41.

Guldi 2018 Guldi, J. “Critical Search: A Procedure for Guided Reading in Large-Scale Textual Corpora”, Journal of Cultural Analytics (2018). doi: 10.31235/osf.io/g286e
