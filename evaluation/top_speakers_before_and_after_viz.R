library(tidyverse)
library(data.table)
library(plotly)
library(ggrepel)
library(scales)

top_speakers <- fread("~/projects/hansard-speakers/evaluation-data/top_speakers_eval.csv")

x_axis_labels <- c(1800, 1810, 1820, 1830, 1840, 1850, 1860, 1870, 1880, 1890)

top_speakers$speaker = str_to_title(top_speakers$speaker)

# it's actually words per decade
ggplot(top_speakers,
       aes(decade,
           words_per_decade,
           label = paste0("Name: ", speaker, "\n",
                          "Word Count: ", words_per_decade))) +
  ylab("Word Count Per Decade") +
  xlab("Decade") +
  ggtitle("Top Speakers Per Decade and Their Word Counts",
          subtitle = "Using the Original Hansard Speaker Field") +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) +
  scale_y_continuous(labels = comma) + 
  scale_x_continuous(breaks = top_speakers$decade)



top_new_speakers <- fread("~/projects/hansard-speakers/evaluation-data/top_new_speakers_eval.csv")

top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "_", " ")
top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "_", "")
top_new_speakers$new_speaker <- str_replace(top_new_speakers$new_speaker, "[:digit:]+", " ")

top_new_speakers$new_speaker = str_to_title(top_new_speakers$new_speaker)

ggplot(top_new_speakers,
       aes(decade,
           words_per_decade,
           label = paste0("Name: ", new_speaker, "\n",
                          "Word Count: ", words_per_decade))) +
  ylab("Word Count Per Decade") +
  xlab("Decade") +
  ggtitle("Top Speakers Per Decade and Their Word Counts",
          subtitle = "Using the Disambiguated Speaker Field") +
  geom_text_repel(force = 1) +
  geom_point(color = "#4682b4") +
  theme_classic(base_size = 16) +
  scale_y_continuous(labels = comma) + 
  scale_x_continuous(breaks = top_speakers$decade)

