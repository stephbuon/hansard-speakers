library(data.table)
library(tidytext)
library(tidyverse)

hansard <- fread("/home/steph/Downloads/hansard_c19_improved_speaker_names_2.csv") %>%
  select(speaker, new_speaker, text, speechdate) %>%
  mutate(year = year(speechdate)) %>%
  mutate(decade = year - year %% 10) %>%
  select(-year, -speechdate)

hansard <- hansard %>%
  unnest_tokens(word, text)

words_per_day <- hansard %>%
  group_by(decade, speaker) %>%
  summarize(words_per_decade = n())

words_per_day <- words_per_day %>%
  group_by(decade) %>%
  mutate(sp_ranking_decade = rank(desc(words_per_decade)))

top_speakers <- words_per_day %>%
  filter(sp_ranking_decade <= 5)

write_csv(top_speakers, "/home/steph/Downloads/top_speakers_eval.csv")

hansard <- hansard %>%
  filter(!str_detect(new_speaker, "^$"))

words_per_day <- hansard %>%
  group_by(decade, new_speaker) %>%
  summarize(words_per_decade = n())

words_per_day <- words_per_day %>%
  group_by(decade) %>%
  mutate(sp_ranking_decade = rank(desc(words_per_day)))

top_speakers <- words_per_day %>%
  filter(sp_ranking_decade <= 5)

write_csv(top_speakers, "/home/steph/Downloads/top_new_speakers_eval.csv")
