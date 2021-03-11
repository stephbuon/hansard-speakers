# Problems I noticed: 
# 1. sometimes names are preceded with *. For example: *THE EARL OF LEITRIM
# 2. sometimes names are preceded with: the hon.
# 3. sometimes speakers have - in their names, for example: (enter example)

library(tidyverse) # load library (like import in Python)

setwd("/scratch/group/pract-txt-mine/") # set working directory

speaker_names_data <- read_csv("missed_speakers_sb.csv") # read list of missed speakers

speakers_w_grenville <- speaker_names_data %>% # filter for speaker with last name "Grenville"
  filter(str_detect(speaker, "Grenville"))

test_baron_grenville <- speakers_w_grenville %>% # from the DF of speakers with last name "Grenville," filter for just those with the title "Baron"
  filter(str_detect(speaker, "Baron"))

just_speaker_names <- speakers_w_grenville %>% # select just the speaker column
  select(speaker) 

unique_names <- distinct(just_speaker_names) # filter for distinct rows
