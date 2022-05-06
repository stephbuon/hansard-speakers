library(tidyverse)
library(lubridate)
library(data.table)
library(plotly)

hansard <- fread("/home/stephbuon/data/hansard_c19_improved_speaker_names_2.csv")%>%
  select(sentence_id, speaker, new_speaker, speechdate) %>%
  mutate(year = year(speechdate)) %>%
  mutate(decade = year - year %% 10) %>%
  select(-year, -speechdate)

disambig_speaker_count <- hansard %>%
  select(decade, new_speaker) %>%
  distinct() %>%
  group_by(decade) %>%
  summarise(sum = n())

disambig_speaker_count %>%
  plot_ly(x = ~decade, 
          y = ~sum, 
          type = 'bar') %>%
  layout(xaxis = list(title = "Decade", tickvals= ~decade, ticktext = ~decade),
         yaxis = list(title = "Number of Unique Speaker Names")) %>%
  add_text(x = ~decade, y = ~sum , text = ~sum, textposition="top") %>%
  config(displayModeBar = F)

speaker_count <- hansard %>%
  select(decade, speaker) %>%
  distinct() %>%
  group_by(decade) %>%
  summarise(sum = n())

speaker_count %>%
  plot_ly(x = ~decade, 
          y = ~sum, 
          type = 'bar') %>%
  layout(xaxis = list(title = "Decade", tickvals= ~decade, ticktext = ~decade),
         yaxis = list(title = "Number of Unique Speaker Names")) %>%
  add_text(x = ~decade, y = ~sum , text = ~sum, textposition="top") %>%
  config(displayModeBar = F) 
