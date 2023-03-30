# Load libraries ----
library(tidyverse)
library(lubridate)
library(here)
library(gt)

# Load data ----
df_measures_ast_reg <- read_csv(here("output/joined/summary/measure_register.csv"))
#test
# Filter data to only include dates needed for table 1
# filter(date == "2022-03-01") only includes financial year 2021/22
# filter(month(date) == 3) would include all march data, i.e., all NHS FYs
# the second option only makes sense if you want to present multiple NHS FYs in
# your table 1. This would require some code adaptations further down.
df_measures_ast_reg_date <- df_measures_ast_reg %>%
  filter(date == "2022-03-01")
# filter(month(date) == 3)

# Tidy up data ----
# Here we add a new variable for the 'indicator' (not relevant at the moment but)
# this would become important if you want to add more indicators. We also change
# the date to a string that indicates the NHS financial year. This only works
# correctly if we filter for month march before. Next, we change the groups and
# categories to be more readable for the presentation in table 1.
df_measures_ast_reg_tidy <- df_measures_ast_reg_date %>%
  mutate(indicator = "ast005") %>%
  mutate(date = paste0("fy", str_sub(year(date) - 1, -2, -1), str_sub(year(date), -2, -1))) %>%
  mutate(
    group = case_when(
      category == "population" ~ "",
      category == "sex" & group == "F" ~ "Female",
      category == "sex" & group == "M" ~ "Male",
      category == "sex" & group == "" ~ "(Missing)",
      category == "age_band" & group == "missing" ~ "(Missing)",
      category == "ethnicity" & is.na(group) ~ "(Missing)",
      category == "learning_disability" & group == "1" ~ "Yes",
      category == "learning_disability" & group == "0" ~ "No",
      category == "care_home" & group == "1" ~ "Yes",
      category == "care_home" & group == "0" ~ "No",
      category == "imd" & group == "1" ~ "1 - Most deprived",
      category == "imd" & group == "5" ~ "5 - Least deprived",
      category == "imd" & group == "missing" ~ "(Missing)",
      TRUE ~ group
    ),
    category = factor(category,
      levels = c("population", "sex", "age_band", "ethnicity", "imd", "region", "care_home", "learning_disability"),
      labels = c("Population", "Sex", "Age band", "Ethnicity", "IMD", "Region", "Care home status", "Record of learning disability")
    )
  ) %>%
  arrange(factor(group, levels = c("6-19","20-29","30-39","40-49","50-59","60-69","70-79","80+","1 - Most deprived","2","3","4","5 - Least deprived",
        "Black", "Mixed", "Other", "South Asian", "White", "(Missing)"))) %>%
  select(indicator, date, numerator, denominator, pct = value, category, group)

# Prepare data for creating table ----
# Some changes to the format of the data to make it easier to create the table
# This is not really needed for only one year and one indicator but would be
# important if we add more FYs or indicators.
df_measures_ast_reg_tidy_tab <- df_measures_ast_reg_tidy %>%
  pivot_longer(cols = c("numerator", "denominator", "pct"), names_to = "variable") %>%
  pivot_wider(
    id_cols = c("category", "group"),
    names_from = c("indicator", "date", "variable"),
    values_from = c("value")
  )

# head(df_measures_ast_reg_tidy[df_measures_ast_reg_tidy$category == "Ethnicity"])
# head(df_measures_ast_reg_tidy)
 head(df_measures_ast_reg_tidy_tab)
# head(gt_tab1_ast005_fy2122)


# Create table ----
gt_tab1_ast005_fy2122 <- df_measures_ast_reg_tidy_tab %>%
  gt(
    rowname_col = "group",
    groupname_col = "category"
  ) %>%
  row_group_order(groups = c("Population", "Sex", "Age band", "Ethnicity", "IMD", "Region", "Care home status", "Record of learning disability")) %>%
  tab_spanner(
    label = "AST005 (Age >= 6)",
    columns = c("ast005_fy2122_numerator", "ast005_fy2122_denominator", "ast005_fy2122_pct")
  ) %>%
  cols_label(
    ast005_fy2122_numerator = "Register",
    ast005_fy2122_denominator = "List size",
    ast005_fy2122_pct = "Prevalence"
  ) %>%
  fmt_number(
    columns = c("ast005_fy2122_numerator", "ast005_fy2122_denominator"),
    decimals = 0,
    use_seps = TRUE
  ) %>%
  fmt_percent(
    columns = c("ast005_fy2122_pct"),
    decimals = 2,
    use_seps = TRUE
  ) %>%
  text_transform(
    locations = cells_body(
      columns = c(ast005_fy2122_numerator, ast005_fy2122_denominator, ast005_fy2122_pct)),
    fn = function(x){
      case_when(x == "NA" ~ "-",
                TRUE ~ x)
    }
  )

# Write table as html file ----
gtsave(gt_tab1_ast005_fy2122, here("output", "joined", "summary", "tab1_ast005_fy2122.html"))
