# Hansard Speaker Name Disambiguation

`hansard-speakers` is a data processing pipeline for disambiguating speaker names in the 19th-century British Parliamentary debates, also known as Hansard. The final dataset produced by this pipeline can be downloaded [here]() (coming soon). An article describing our disambiguation efforts can be read [here]() (coming soon).

## Steps: 
1. Clone the repo and `cd` into `hansard-speakers`
2. Start the disambiguation process. 

   Over terminal:
  `cythonize -3 -i util/*.pyx`
  `python3 run.py --cores <n>` where "n" must be a minimum of three cores

   Over SLURM:
  `sbatch job.sbatch` 

## Requirements:
Our disambiguation process uses lower-level processing for computational speed and efficency. To run `hansard-speakers`, users must have [Cython](https://pypi.org/project/Cython/) installed as well as Python.
