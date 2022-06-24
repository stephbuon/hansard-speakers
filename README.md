# Hansard Speaker Name Disambiguation

Democracy Lab thus presents a preprocessing pipeline that produces the cleanest known version of the Hansard data which includes disambiguated speaker names. The final dataset produced by this pipeline can be downloaded [here]().

Steps: 
1. Downlood the speaker name data. 

2. Initialize the disambiguation process. Over terminal do:

Terminal: 
- `cythonize -3 -i util/*.pyx`
- `python3 run.py --cores 3`

SLURM: 
- `sbatch job.sbatch` 

Must have a minimum of three cores. 
Must have cython installed 
