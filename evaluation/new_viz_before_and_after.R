# I created this so that I could make a high rez before and after disambiguation viz. 
library(ggplot2)
library(dplyr)
library(tidyr)


# Create the dataframe
data <- data.frame(
  decade = c("1800", "1810", "1820", "1830", "1840", "1850", "1860", "1870", "1880", "1890", "1900", "1910"),
  original_speaker = c(1316, 1691, 1751, 3776, 3936, 3173, 3320, 3998, 9079, 12999, 14806, 1956),
  disambiguated_speaker = c(239, 368, 370, 863, 725, 820, 877, 812, 1153, 1117, 1134, 634) # Assuming same numbers as placeholder
)


# Reshaping your data to a long format for easier plotting with ggplot
data_long <- data %>%
  gather(key = "type", value = "count", original_speaker, disambiguated_speaker) %>%
  mutate(type = ifelse(type == "original_speaker", "Unique Speaker Names in Original Data", "Unique Speaker Names after Disambiguation"))



# Unique Speaker Names Before and After Disambiguation 

plot <- ggplot(data_long, aes(x = decade, y = count, fill = type)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7), width = 0.6) +
  labs(x = "Decade",
       y = "Number of Unique Speaker Names") +
  theme_minimal() +
  geom_text(aes(label = paste(count)), position = position_dodge(width = 0.7), vjust = -0.5,
            angle = 0, size = 4) + # hjust = 0.1
  theme(legend.title = element_blank(),
        legend.position = "top",
        legend.text = element_text(size = 12),
        axis.title.x = element_text(size = 12),
        axis.title.y = element_text(size = 12),
        plot.margin = unit(c(1, 1, 0.5, 1), "cm")) # Adjust margins (top, right, bottom, left)

print(plot)

ggsave(filename = "unique_speaker_names.png", plot = plot, width = 10, height = 5, dpi = 500)

