library(tidyverse)
library(data.table)
library(plotly)
library(ggrepel)
library(scales)

top_speakers <- fread("~/projects/hansard-speakers/evaluation-data/top_speakers_eval.csv")

top_speakers$label <- paste0(top_speakers$speaker, ", ", top_speakers$words_per_decade)

ggplot(top_speakers,
       aes(decade,
           words_per_decade,
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) +
  scale_y_continuous(labels = comma)

top_new_speakers <- fread("~/projects/hansard-speakers/evaluation-data/top_new_speakers_eval.csv")

top_new_speakers$label <- paste0(top_new_speakers$new_speaker, ", ", top_new_speakers$words_per_decade)

ggplot(top_new_speakers,
       aes(decade,
           words_per_decade,
           label = label)) +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) +
  scale_y_continuous(labels = comma)
