library(readr)
library(dplyr)
library(here)
library(tidyr)
library(stringr)
source(here::here("analysis", "funs_tidy_data.R"))

# Deciles tables ----
## Read csv
df_deciles_hyp <- read_csv(here("released_outputs/deciles/deciles_hyp_practice.csv"))

df_deciles_bp_1y <- read_csv(here("released_outputs/deciles/deciles_table_bp002_1y_achievem_practice_breakdown_rate.csv")) |>
  mutate(indicator = "bp002_1y") |>
  relocate(indicator)

df_deciles_bp_5y <- read_csv(here("released_outputs/deciles/deciles_table_bp002_5y_achievem_practice_breakdown_rate.csv")) |>
  mutate(indicator = "bp002_5y") |>
  relocate(indicator)

# Join csv
df_deciles_bp_hyp <- df_deciles_hyp |>
  bind_rows(df_deciles_bp_1y) |>
  bind_rows(df_deciles_bp_5y)

# Write csv
write_csv(df_deciles_bp_hyp, here("released_outputs/deciles/deciles_bp_hyp_practice.csv"))

# Measures files ----
## Read individual measures files
df_measures_bp002 <- read_csv(here("released_outputs/measures/measures_bp002_achievem.csv"))
df_measures_hyp001 <- read_csv(here("released_outputs/measures/measures_hyp001.csv"))
df_measures_hyp003 <- read_csv(here("released_outputs/measures/measures_hyp003.csv"))
df_measures_hyp007 <- read_csv(here("released_outputs/measures/measures_hyp007.csv"))
df_measures_bp002_hypreg <- read_csv(here("released_outputs/measures/measures_bp002_1y_hypreg.csv"))

df_measures_bp002 <- df_measures_bp002 |>
  mutate(category = case_when(
    group == "learning_disability" | group == "care_home" ~ as.character(as.logical(as.integer(category))),
    TRUE ~ category
  ))

# Read all measures files and pivot into indicatorentical structure
df_measures_bp002_long <- df_measures_bp002 |>
  rename(pct = value) |>
  pivot_longer(
    cols = c(bp002_numerator, bp002_denominator, population, pct),
    values_to = "value", names_to = "variable"
  ) |>
  mutate(
    indicator = paste0("bp002_", lookback),
    variable = str_remove(variable, "bp002_")
  ) |>
  relocate(indicator, date, variable, group, category, value) |>
  select(-lookback)

df_measures_bp002_hypreg_long <- df_measures_bp002_hypreg |>
  rename(pct = value) |>
  pivot_longer(
    cols = c(bp002_numerator, population, pct),
    values_to = "value", names_to = "variable"
  ) |>
  mutate(
    indicator = "bp002_1y_hypreg",
    variable = str_remove(variable, "bp002_")
  ) |>
  relocate(indicator, date, variable, group, category, value)

df_measures_hyp001_long <- df_measures_hyp001 |>
  rename(pct = value) |>
  pivot_longer(
    cols = c(hyp_reg, population, pct),
    values_to = "value", names_to = "variable"
  ) |>
  mutate(
    indicator = "hyp001",
    variable = case_when(
      variable == "hyp_reg" ~ "register",
      TRUE ~ variable
    )
  ) |>
  relocate(indicator, date, variable, group, category, value)

df_measures_hyp003_long <- df_measures_hyp003 |>
  rename(pct = value) |>
  pivot_longer(
    cols = c(hyp003_numerator, hyp003_denominator, population, pct),
    values_to = "value", names_to = "variable"
  ) |>
  mutate(
    indicator = "hyp003",
    variable = str_remove(variable, "hyp003_")
  ) |>
  relocate(indicator, date, variable, group, category, value)

df_measures_hyp007_long <- df_measures_hyp007 |>
  rename(pct = value) |>
  pivot_longer(
    cols = c(hyp007_numerator, hyp007_denominator, population, pct),
    values_to = "value", names_to = "variable"
  ) |>
  mutate(
    indicator = "hyp007",
    variable = str_remove(variable, "hyp007_")
  ) |>
  relocate(indicator, date, variable, group, category, value)

# Join measures files
df_measures_bp_hyp <- df_measures_bp002_long |>
  bind_rows(
    df_measures_hyp001_long,
    df_measures_hyp003_long,
    df_measures_hyp007_long,
    df_measures_bp002_hypreg_long,
  )

df_measures_bp_hyp <- df_measures_bp_hyp |>
  tidy_category_names(
    group = group,
    category = category,
    learning_disability = "learning_disability",
    imd = "imd_q5",
    sex = "sex",
    care_home = "care_home",
    population = "population",
    long_labels = TRUE,
    imd_explicit_na = FALSE
  )

# Improve naming of groups and categories
# This was confusing before, now clearer
df_measures_bp_hyp <- df_measures_bp_hyp |>
  rename(subgroup = category)

df_measures_bp_hyp <- df_measures_bp_hyp |>
  mutate(subgroup = case_when(is.na(subgroup) & group == "region" ~ "(Missing)",
  TRUE ~ subgroup))

# Write measures files
write_csv(df_measures_bp_hyp, here("released_outputs/measures/df_measures_bp_hyp.csv"))
