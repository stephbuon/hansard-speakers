# William Gladstone's top words before and after disambiugation. 

library(tidyverse)
library(tidytext)
library(data.table)

hansard <- fread("~/data/hansard_c19_improved_speaker_names_2.csv")

sw <- read_csv("/home/stephbuon/Downloads/stopwords.csv") %>%
  rename(word = stop_word)


gladstone_orig <- hansard %>%
  select(text, speaker) %>%
  filter(speaker == "Mr. Gladstone") %>%
  unnest_tokens(word, text) %>%
  count(word) %>%
  anti_join(sw) %>%
  filter(!str_detect(word, regex("[:digit:]"))) %>%
  mutate(category = paste0("original"))

gladstone_orig <- gladstone_orig %>%
  arrange(desc(n)) %>%
  slice(1:20)

gladstone_orig$word <- str_to_title(gladstone_orig$word)

ggplot(gladstone_orig,
       aes(x = n,
           y = reorder(word, n))) +
  geom_bar(stat = "identity",
           fill = "steel blue") + 
  labs(x = "Total Word Count",
       y = "Word") +
  ggtitle("William Gladstone's Top Words in the Hansard Debates",
          subtitle = "Using the Original Speaker Field") 

ggsave("~/projects/hansard-speakers/evaluation/evalutaion-images/gladstone_top_words_before.png", width = 6, height = 6, dpi = 500)


gladstone_disambig <- hansard %>%
  select(text, new_speaker) %>%
  filter(new_speaker == "william_gladstone_3104") %>%
  unnest_tokens(word, text) %>%
  count(word) %>%
  anti_join(sw) %>%
  filter(!str_detect(word, regex("[:digit:]"))) %>%
  mutate(category = paste0("disambig"))

gladstone_disambig <- gladstone_disambig %>%
  arrange(desc(n)) %>%
  slice(1:20) 

gladstone_disambig$word <- str_to_title(gladstone_disambig$word )

ggplot(gladstone_disambig,
       aes(x = n,
           y = reorder(word, n))) +
  geom_bar(stat = "identity",
           fill = "steel blue") + 
  labs(x = "Total Word Count",
       y = "Word") +
  ggtitle("William Gladstone's Top Words in the Hansard Debates",
          subtitle = "Using the Disambiguated Speaker Field")


ggsave("~/projects/hansard-speakers/evaluation/evalutaion-images/gladstone_top_words_after.png", width = 6, height = 6, dpi = 500)

# gladstone <- bind_rows(gladstone_orig, gladstone_disambig)
# 
# ggplot(gladstone, 
#        aes(x = n,
#            y = reorder(word, n))) +
#   geom_bar(stat = "identity") +
#   facet_wrap(vars(category))

#ggsave("~/projects/hansard-speakers/evaluation/evalutaion-images/gladstone_top_words_after.png", width = 20, height = 15, dpi = 500)

