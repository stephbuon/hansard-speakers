library(data.table)
library(tidytext)
library(tidyverse)
library(plotly)
library(ggrepel)
library(scales)

hansard <- fread("hansard_c19_improved_speaker_names_2.csv") %>%
  select(speaker, new_speaker, text, speechdate) %>%
  mutate(year = year(speechdate)) %>%
  mutate(decade = year - year %% 10) %>%
  select(-year, -speechdate)

hansard$speaker <- tolower(hansard$speaker)
hansard$new_speaker <- tolower(hansard$new_speaker)

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

write_csv(top_speakers, "top_speakers_eval.csv")

hansard <- hansard %>%
  filter(!str_detect(new_speaker, "^$"))

words_per_day <- hansard %>%
  group_by(decade, new_speaker) %>%
  summarize(words_per_decade = n())

words_per_day <- words_per_day %>%
  group_by(decade) %>%
  mutate(sp_ranking_decade = rank(desc(words_per_decade)))

top_speakers <- words_per_day %>%
  filter(sp_ranking_decade <= 5)

write_csv(top_speakers, "top_new_speakers_eval.csv")

#### Viz part

top_speakers <- fread("top_speakers_eval.csv") %>% 
  arrange(desc(words_per_decade)) %>%
  group_by(decade) %>% 
  slice(1:3)

x_axis_labels <- c(1800, 1810, 1820, 1830, 1840, 1850, 1860, 1870, 1880, 1890)

top_speakers$speaker = str_to_title(top_speakers$speaker)

# it's actually words per decade
ggplot(top_speakers,
       aes(x = decade,
           y = words_per_decade,
           label = paste0(speaker, "\n",
                          "Word Count: ", comma(words_per_decade)))) +
  geom_text_repel(size = 5, 
                  force = 1) +
  geom_point(size = 3, 
             color = "#4682b4") +
  scale_y_continuous(labels = comma) +
  scale_x_continuous(breaks = top_speakers$decade) +
  labs(y = "Word Count Per Decade",
       x = "Decade",
       title = "From the Original Hansard Speaker Field") +
  theme_gray(base_size = 16)

ggsave("top_speakers_before.png", width = 18, height = 13, dpi = 500)

top_new_speakers <- fread("top_new_speakers_eval.csv") %>%
  arrange(desc(words_per_decade)) %>%
  group_by(decade) %>% 
  slice(1:3)

top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "_", " ")
top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "_", "")
top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "[:digit:]+", " ")

top_new_speakers$new_speaker = str_to_title(top_new_speakers$new_speaker)

ggplot(top_new_speakers,
       aes(x = decade,
           y = words_per_decade,
           label = paste0("Name: ", new_speaker, "\n",
                          "Word Count: ", comma(words_per_decade)))) +
  geom_text_repel(size = 5, 
                  force = 1) +
  geom_point(size = 3, 
             color = "#4682b4") +
  scale_y_continuous(labels = comma) +
  scale_x_continuous(breaks = top_new_speakers$decade) +
  labs(y = "Word Count Per Decade",
       x = "Decade",
       title = "Word Counts",
       subtitle = "From the Disambiguated Speaker Field") +
  theme_gray(base_size = 16)

ggsave("top_speakers_after.png", width = 18, height = 13, dpi = 500)