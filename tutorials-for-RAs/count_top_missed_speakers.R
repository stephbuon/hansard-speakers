library("tidyverse")

setwd("/scratch/group/pract-txt-mine/")

hansard <- read_csv("missed_speakers.csv")

just_speaker_column <- hansard %>%
  select(speaker)

just_speaker_column <- just_speaker_column %>%
  count(speaker)

just_speaker_column <- just_speaker_column %>%
  arrange(desc(n))

### or from the speaker_modified column: 

library("tidyverse")

setwd("/scratch/group/pract-txt-mine/")

hansard <- read_csv("missed_speakers.csv")

just_speaker_column <- hansard %>%
  select(speaker_modified) 

just_speaker_column$speaker_modified <- just_speaker_column$speaker_modified %>%
  tolower()

just_speaker_column <- just_speaker_column %>%
  count(speaker_modified)


#test <- just_speaker_column %>%
#  filter(str_detect(speaker_modified, "\\("))


#just_speaker_column <- just_speaker_column %>%
#  filter(n > 50)

just_speaker_column <- just_speaker_column %>%
  arrange(desc(n))
