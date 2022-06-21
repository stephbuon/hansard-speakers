library(tidyverse)
library(data.table)
library(lubridate)

hansard <- fread("~/data/hansard_c19_improved_speaker_names_2.csv") %>%
  mutate(year = year(speechdate)) %>%
  select(speaker, new_speaker, year, text, debate) %>%
  mutate(len = str_count(new_speaker)) %>%
  filter(len == 0)

hansard_unique <- unique(hansard)

remove <- "CHAIRMAN|^dr\\.|^col|baron|lord|duke|Marquis|earl |Colonel|viscount|PRESIDENT|SECRETARY|mr\\. |mr |GENERAL|sir |hon\\. |Admiral|CAPTAIN|BISHOP|MARQUESS"

preliminary_search <- hansard_unique %>%
  filter(!str_detect(speaker, regex(remove, ignore_case = T)))

find <- "labour member|nationalist member|unionist member|voice|welsh member|irish member|opposition member|honourable member|tenant|messenger|prisoner|conservative member|several member|witness|yeoman"
  
search_for_unidentified <- hansard_unique %>%
  filter(str_detect(speaker, regex(find, ignore_case = T)))

women <- "^mrs|^ms|^miss"

search_for_women <- hansard_unique %>%
  filter(str_detect(speaker, regex("Ms. Cunninghame Graham", ignore_case = T)))


check_debates_w_women <- hansard_unique %>%
  filter(str_detect(debate, regex("COMMITTEE", ignore_case = T)))




  