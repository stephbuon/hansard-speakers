#!/bin/bash
#SBATCH --job-name=hansard_speakers
#SBATCH -p standard-mem-s,standard-mem-m,standard-mem-l,medium-mem-1-s,medium-mem-1-m,medium-mem-2
#SBATCH --mem=48G
#SBATCH --exclusive
#SBATCH --mail-user="<your email here>"
#SBATCH --mail-type=ALL
#SBATCH --ntasks-per-node=16
#SBATCH --time=120

module purge
module load python/3

cd $HOME

if [ -d hansard-speakers ]; then
  cd hansard-speakers
  git reset --hard
  git pull
else
  git clone https://<access token here>@github.com/stephbuon/hansard-speakers.git
  cd hansard-speakers
fi

python3 run.py --cores ${SLURM_NTASKS}
