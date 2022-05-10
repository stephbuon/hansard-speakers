library(tidyverse)
library(data.table)
library(plotly)
library(ggrepel)
library(scales)

top_speakers <- fread("/home/steph/Downloads/top_speakers_eval.csv")

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



top_new_speakers <- fread("/home/steph/Downloads/top_new_speakers_eval.csv")

top_new_speakers$label <- paste0(top_new_speakers$speaker, ", ", top_new_speakers$words_per_day)


ggplot(top_new_speakers,
       aes(decade,
           words_per_day,
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) +
  scale_y_continuous(labels = comma)

top_new_speakers$label <- paste0(top_new_speakers$speaker, ", ", top_new_speakers$words_per_day)


ggplot(top_new_speakers, 
       aes(decade, 
           words_per_day, 
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) + 
  scale_y_continuous(labels = comma)
