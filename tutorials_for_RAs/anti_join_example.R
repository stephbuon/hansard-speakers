library(tidyverse) # load the required library
setwd("/scratch/group/pract-txt-mine") # set your directory

top_words_in_hansard <- read_csv("top_1grams_c20_hansard.csv")  #load the data

concerns <- read_csv("concerns.csv") # load the data you want to use for the anti_join()

concerns <- concerns %>%
rename(ngrams = concerns) # rename the column to ngrams so anti_join() works easily

top_words_in_hansard_without_conerns <- top_words_in_hansard %>% # anti_join() (remove) words that are in both data sets
anti_join(concerns, by = "ngrams")
