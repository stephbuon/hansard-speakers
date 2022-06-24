# Hansard Speaker Name Disambiguation

`hansard-speakers` is a data processing pipeline that disambiguates speaker names in the 19th-century British Parliamentary debates, also known as Hansard. The final dataset produced by this pipeline can be downloaded [here]().

Steps: 
1. Download the speaker name data from our GitHub [repository](https://github.com/stephbuon/hansard-speakers/tree/main/data) or from ENTER. 

2. Start the disambiguation process.

Over terminal do:
- `cythonize -3 -i util/*.pyx`
- `python3 run.py --cores <n>` where "n" must be a minimum of three cores. 

Or, if using SLRUM do:
- `sbatch job.sbatch` 

Requirements:
Our disambiguation process uses lower-level processing for computational speed and efficency. To run `hansard-speakers`, users must have [Cython](https://pypi.org/project/Cython/) installed. 
