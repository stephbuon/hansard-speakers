library(tidyverse)

hansard <- read_csv("/home/stephbuon/data/hansard_speakers.csv") %>%
  select(-ignored, -sentence_id)

out <- hansard %>%
  filter(fuzzy_matched == 1,
         ambiguous == 0)

out <- out %>%
  sample_n(1000)

write_csv(out, "~/hansard_1000_names.csv")
