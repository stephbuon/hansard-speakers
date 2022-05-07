library(data.table)
library(tidytext)
library(tidyverse)

hansard <- fread("/scratch/group/pract-txt-mine/hansard_c19_improved_speaker_names_2.csv") %>%
  select(speaker, new_speaker, text, speechdate) %>%
  mutate(year = year(speechdate)) %>%
  mutate(decade = year - year %% 10) %>%
  select(-year, -speechdate)

tokenized_hansard <- hansard %>%
  unnest_tokens(word, text)



words_per_day <- tokenized_hansard %>%
  group_by(decade, speaker) %>%
  summarize(words_per_decade = n())

words_per_day <- words_per_day %>%
  group_by(decade) %>%
  mutate(sp_ranking_decade = rank(desc(words_per_day)))

top_speakers <- words_per_day %>%
  filter(sp_ranking_decade <= 5)

write_csv(top_speakers, "top_speakers_eval.csv")

tokenized_hansard_2 <- tokenized_hansard %>%
filter(!str_detect(new_speaker, "^NA$")) 

words_per_day <- tokenized_hansard_2 %>%
  group_by(decade, new_speaker) %>%
  summarize(words_per_decade = n())

words_per_day <- words_per_day %>%
  group_by(decade) %>%
  mutate(sp_ranking_decade = rank(desc(words_per_day)))

top_speakers <- words_per_day %>%
  filter(sp_ranking_decade <= 5)

write_csv(top_speakers, "top_new_speakers_eval.csv")


library(tidyverse)
library(data.table)
library(plotly)
library(ggrepel)
library(scales)

top_speakers <- fread("/home/stephbuon/projects/hansard-speakers/evaluation-data/top_speakers_eval.csv")

top_speakers$label <- paste0(top_speakers$speaker, ", ", top_speakers$words_per_day)

# it's actually words per decade
ggplot(top_speakers, 
       aes(decade, 
           words_per_day, 
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) + 
  scale_y_continuous(labels = comma)



top_new_speakers <- fread("/home/stephbuon/projects/hansard-speakers/evaluation-data/top_new_speakers_eval.csv")

top_new_speakers$label <- paste0(top_new_speakers$speaker, ", ", top_new_speakers$words_per_day)


ggplot(top_new_speakers, 
       aes(decade, 
           words_per_day, 
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) + 
  scale_y_continuous(labels = comma)
