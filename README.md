# Hansard Speaker Name Disambiguation

Text mining methods such as topic modeling, collocate extraction, or word embeddings, have become increasingly important for interpreting the 19th-century British Parliamentary debates, also known as Hansard (Blaxill 2013, Guldi 2018). Some analyses of Hansard, however, can be thwarted by messy data. The analysis of Parliamentary speakers, for example, has been inhibited by ambiguities in speaker names. Distinguishing between multiple speakers who share the same name is no easy matter. To make disambiguation more challenging yet, a single member of Parliament (MP) might be called by many titles, different honorifics, or their name might be recorded as any combination of their first name, middle name(s), and last name(s). The regularity of OCR errors can also obscure a speaker’s true name. The ability to perform analysis on speakers, however, is important to the advancement of historical understandings of the Hansard debates. 

Democracy Lab thus presents a preprocessing pipeline that produces the cleanest known version of the Hansard data which includes disambiguated speaker names. The final dataset produced by this pipeline can be downloaded [here]().

Preprocessing the Hansard data is performed in two major phases:

- During phase I we scrape the Hansard data hosted by the UK Parliament, transforming the raw XML files into a TSV file. We chose TSV because it is a popular file format used in computation generally, and within the digital humanities specifically. It can be easily imported into R or pandas.
 
  While scraping the data, we discovered systematic issues in the XML tags. Debate text, for example, might be tagged as a debate title, while other sections might be missing tags in their entirety. In result (thought missing). For code that corrects these systematic issues and exports a clean TSV file, see [Bulk Import and Cleaning of Hansard XML Data](https://github.com/stephbuon/import_hansard_data).

- During phase II we disambiguate speakers. Even after correcting for systemic issues in the data, accurate analysis of speakers was not possible because of ambiguities and inconsistencies in the names of MPs. This repository documents the problems associated with identifying the speakers of each sentence, and presents a pipeline for disambiguating speaker names by assigning a unique name, consisting of a standardized name and unique ID, to each speaker of a sentence.

### About the Problems Causing Ambiguous Speakers
We identify and correct for 5 major issues that cause ambiguities in speaker names:

1) Prolific members of parliament often held several office positions and the name of the MP holding the position is usually not mentioned. The XML hosted by the [historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html) often only tags the position title (i.e., Prime Minister) as the full name of the speaker. This problem is especially pronounced in cases where a single MP held numerous offices. William Ewart Gladstone, for example, acted as Prime Minister four times, Chancellor of the Exchequer four times, Secretary of State for War and the Colonies, and President of the Board of Trade. Determining which instances a title can be accredited to William Ewart Gladstone is paramount for accurate analyses of speakers.

2) A single name has several permutations. During a debate, William Ewart Gladstone might have been called William Gladstone, W. Gladstone, W. E. Gladstone, Wiliam E. Gladstone, and so forth. Without detecting and replacing each permutation with a distinct, standardized name, the pervasiveness of permutations can be misleading for analysis.

3) Several MPs shared the same name. Three different Parliamentarians, for example, were named Sir Robert Peel. In cases like this, metadata was collected to help make distinctions between the different speakers. Metadata may include the start and end dates of the different speakers with a shared name. In other cases, some speakers share elements of their name, causing ambiguity. Mr Gladstone or Mr. W. Gladstone, for example, might refer to William Ewart Gladstone or Willaim Henry Gladstone.

4) Many MP names have OCR errors. The original debates were hand-recorded with inkwell pens (check). Handwriting can pose challenges for digitization efforts. The technologies used to parse and tag the original, hand recorded debates developed over time, and many of the earlier 19th-century debates were digitized and tagged using now outdated technologies from the 1980s. While these early digitization efforts were important milestones for the production of the Hansard data, the output from these early technologies are prone to error. The number of distinct errors can be exacerbated by the permutations of speaker names, where each form of a name can contain OCR errors.

5) Many MP names have inconsistent spellings. "Sir Henry Campbell-Bannerman," for example, might be transcribed as "Campbell Bannerman," or "Campbell - Bannerman." While each spelling can be considered correct, these differences can erroneously register as different speakers.

To address the above issues we have developed a speaker disambiguation pipeline that assigns a unique name, consisting of a standardized name and unique ID, to each speaker of a sentence.

### About the Hansard Speaker Disambiguation Pipeline
Our speaker disambiguation efforts include: a) collecting extensive metadata about MPs, b) adding missing MPs to existing data sets, and c) implementing our hansard speakers disambiguation algorithm, which will be described in greater detail in the section, "Algorithm."

#### Data
A key step in disambiguating speakers was collecting additional metadata about speakers. This metadata is used to match unique names with the names of MPs in the speaker column. The metadata includes: a) existing data sets, b) new data sets aggregated by Democracy Lab's research assistants, and c) data generated by the Hansard speakers disambiguation algorithm.

The existing data sets used by our pipeline were generously provided by: a) the [DiLPD project](https://sas-space.sas.ac.uk/4315/16/westminster-members.xml), and b) the [Andy Eggers and Arthur Spirling database](http://andy.egge.rs/eggers_spirling_database.html). 

These impressive data sets are foundational to our work, providing speaker names and relevant metadata. On their own, however, these data sets do not contain the total information required to disambiguate speaker names. Therefore, RAs collected extensive metadata from various sources such as [the historic Hansard UK Parliament API](https://api.parliament.uk/historic-hansard/people/index.html), (enter), (enter). Data was standardized with four fields: a) `corresponding_ID`, a unique ID assigned to each MP; b) `alias`, another name the speaker went by; c) `start_date`, the first date a Parliamentarian served as MP; d) `end_date`, the last date a Parliamentarian served as MP during a consecutive sentence. MPs who served multiple times with intermittent breaks will have multiple entries for start and end dates. 

The total metadata includes: a) honorary titles; b) titles for “Lord,” “Viscount,” or “Earl;” c) name aliases; and d) office holdings The metadata can be downloaded as csv files [here](). 

The metadata greatly improved the detection and disambiguation of speaker names. It does not, however, account for the many permutations a single MP name might have. Because this number is unknown, the Hansard speakers disambiguation algorithm generates an exhaustive list of every possible permutation for each MP name, a process that will be described in detail in the “Algorithm” section.

#### Algorithm
The algorithm disambiguates speakers in (X) major steps:
Importing and validating metadata
Generating speaker name permutations
Mapping MPs to metadata about (service in Parliament) 
Enter rest 

First, speaker metadata is imported and validated. After importing speaker metadata, permutations of speaker names are generated. Any periods are discarded. Permutations account for possible combinations in full names and initials. A name with four items, for example, can have X permutations: 

```
William Heald Ludlow Bruges
Mr Bruges
William Bruges
W Bruges
W H Bruges
W H L Bruges
William H Bruges
William L Bruges
William H L Bruges
William Heald L Bruges
William H Ludlow Bruges
(add more
```

After generating permutations, office term and office position data is loaded, where office term includes (enter), and office data includes (enter). MP's corresponding IDs are mapped to office terms and office positions that have start and end dates. If the start date is missing a day or month, the start date will be assigned the first day of the year. If the end date is missing a day or month, it will be assigned the last date of the year.

At this point, the Hansard data is imported and chunked for parallel processing. Common OCR errors for words like “Mr.,” “the,” etc. For a full list, see (enter). All symbols, except hyphens, are discarded.

After cleaning the data, the speaker name disambiguation algorithm applies fuzzy matching to office titles (such as “Prime Minister,” or “Chancellor of the Exchequer”) and regular names (such as Mr. Gladstone or Mr. Hume), which were both rife with OCR errors. To match with errorful names, the fuzzy match performed by the present algorithm uses Levenshtein distances carefully and deliberately applied to different data subsections. If operating on office titles, a distance of 4 is used. If operating on full names or just last names, a distance of 2 is used. A distance of 2 is also used for names within Lord’s Titles, Honorary Titles, and the dictionary of name aliases. 

For the present project (where we were working with missing data and growing data for most of the development of the algorithm) we found Levenshtein distance to be more effective than other distance measures commonly used in fuzzy matching, such as Jaro distance, because Jaro distance too readily matched names, whereas the Levenshtein implementation is highly restricted, decreasing the possibility that names are incorrectly matched. 

We infer the remaining speakers' true names. Even after collecting extensive amounts of metadata on MPs, resolving large amounts of OCR errors, and carefully reading the Hansard debates for information about speakers, (percent of conflicts) speakers could not be disambiguated because their recorded name matched another MP active during the same period. This problem was especially pronounced in cases where the MP was highly active in Parliament and had multiple family members who were also Parliamentarians at the same time, for example, Mr. Gladstone, Mr. Hume, Mr. Disraeli, and more. Some of these conflicts may occur from 5,000 up to 100,000 sentences per MP name, making the process of determining speaker by reading each sentence nearly impossible. Instead, the true names of these remaining speakers are inferred using a carefully curated set of language-based assumptions derived from specialized domain knowledge of the Hansard data. 

These rules for inferring speakers are handled with great care, adhering to specialized domain knowledge of the Hansard data. The `hansard-speakers` Wiki documents each rule, and can be viewed [here](https://github.com/stephbuon/hansard-speakers/wiki/Hansard-Speaker-Names-Inferences).

A report on conflicting speaker names that describes why the name was inferred, as well as our resolution for handling each name, can be downloaded [here](). A full list of sentences where the speaker name was inferred can be viewed on the Wiki [here](), or downloaded as a CSV file [here]().

If the name is still ambiguous at this point, MP's ages are detected. If the MP is less than 20 years old at the time of the debate, the MP is rejected as too young.

### Comparing Results
Our pipeline significantly improves speaker recognition compared to existing data sets. The DiLPD data and the Eggers and Spirling data combined only match with X% of the Hansard data.
Speakers are assigned the status of “match,” if the 
“Ambiguous” if enter, and miss if enter. 

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
