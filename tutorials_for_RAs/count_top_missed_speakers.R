library("tidyverse")

setwd("/scratch/group/pract-txt-mine/")

hansard <- read_csv("missed_speakers.csv")

just_speaker_column <- hansard %>%
  select(speaker)

just_speaker_column <- just_speaker_column %>%
  count(speaker)

just_speaker_column <- just_speaker_column %>%
  arrange(desc(n))
