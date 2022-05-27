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
  count(decade, new_speaker) %>%
  select(-new_speaker) %>%
  group_by(decade) %>%
  summarise(disambig_speaker = n()) 

original_speaker_count <- hansard %>%
  count(decade, speaker) %>%
  select(-speaker) %>%
  group_by(decade) %>%
  summarise(original_speaker = n()) 

all_data <- left_join(original_speaker_count, disambig_speaker_count, by = "decade")

plot_ly(data = all_data, 
        x = ~decade, 
        y = ~original_speaker, 
        name = "Original Speakers",
        type = 'bar',
        text = ~original_speaker, textposition = 'top',
        marker = list(color = 'rgb(49,130,189)')) %>%
  add_trace(y = ~disambig_speaker,
            name = "Disambiguated Speakers",
            text = ~disambig_speaker, textposition = 'top',
            marker = list(color = 'rgb(204,204,204)')) %>%
  layout(xaxis = list(title = "Decade", tickvals= ~decade, ticktext = ~decade),
         yaxis = list(title = "Number of Unique Speaker Names")) %>%
  config(displayModeBar = F)
  

# 
# disambig_speaker_count %>%
#   plot_ly(x = ~decade, 
#           y = ~sum, 
#           type = 'bar') %>%
#   layout(xaxis = list(title = "Decade", tickvals= ~decade, ticktext = ~decade),
#          yaxis = list(title = "Number of Unique Speaker Names")) %>%
#   add_text(x = ~decade, y = ~sum , text = ~sum, textposition="top") %>%
#   config(displayModeBar = F)
# 
# 
# speaker_count %>%
#   plot_ly(x = ~decade, 
#           y = ~sum, 
#           type = 'bar') %>%
#   layout(xaxis = list(title = "Decade", tickvals= ~decade, ticktext = ~decade),
#          yaxis = list(title = "Number of Unique Speaker Names")) %>%
#   add_text(x = ~decade, y = ~sum , text = ~sum, textposition="top") %>%
#   config(displayModeBar = F) 

