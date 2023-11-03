from ehrql import Dataset, years, months, weeks, case, when, Measures, INTERVAL
from ehrql.tables.beta.tpp import (
    patients,
    medications,
    clinical_events,
    addresses,
    practice_registrations
)

import ehrql_codelists_demographic

from ehrql_dataset_definition import make_dataset_asthma


# create dataset #

index_date = "2019-03-01"
end_date = "2023-08-01"

dataset = make_dataset_asthma(index_date="2019-03-31", end_date="2023-04-01")

# define population #
dataset.define_population(
    (patients.age_on(index_date + years(1)) >= 6)
    & ((patients.sex == "male") | (patients.sex == "female"))
    & (patients.date_of_death.is_after(end_date) | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on(index_date).exists_for_patient())
)

# demographic variables #

# age bands
dataset.age_band = case(
    when((patients.age_on(index_date) >= 6) & (
        patients.age_on(index_date) < 20)).then("6-19"),
    when((patients.age_on(index_date) >= 20) & (
        patients.age_on(index_date) < 30)).then("20-29"),
    when((patients.age_on(index_date) >= 30) & (
        patients.age_on(index_date) < 40)).then("30-39"),
    when((patients.age_on(index_date) >= 40) & (
        patients.age_on(index_date) < 50)).then("40-49"),
    when((patients.age_on(index_date) >= 50) & (
        patients.age_on(index_date) < 60)).then("50-59"),
    when((patients.age_on(index_date) >= 60) & (
        patients.age_on(index_date) < 70)).then("60-69"),
    when((patients.age_on(index_date) >= 70) & (
        patients.age_on(index_date) < 80)).then("70-79"),
    when((patients.age_on(index_date) >= 80)).then("80+"),
    default="NULL"
)

# sex
dataset.sex = patients.sex

# region
dataset.region = practice_registrations.for_patient_on(
    index_date).practice_nuts1_region_name

# IMD decile
imd = addresses.for_patient_on(index_date).imd_rounded
dataset.imd10 = case(
    when((imd >= 0) & (imd < int(32844 * 1 / 10))).then("1 (most deprived)"),
    when(imd < int(32844 * 2 / 10)).then("2"),
    when(imd < int(32844 * 3 / 10)).then("3"),
    when(imd < int(32844 * 4 / 10)).then("4"),
    when(imd < int(32844 * 5 / 10)).then("5"),
    when(imd < int(32844 * 6 / 10)).then("6"),
    when(imd < int(32844 * 7 / 10)).then("7"),
    when(imd < int(32844 * 8 / 10)).then("8"),
    when(imd < int(32844 * 9 / 10)).then("9"),
    when(imd >= int(32844 * 9 / 10)).then("10 (least deprived)"),
    default="unknown"
)

# ethnicity (6 groups)
ethnicity6 = clinical_events.where(clinical_events.snomedct_code.is_in(
    ehrql_codelists_demographic.ethnicity_codes_6)).sort_by(clinical_events.date).last_for_patient().snomedct_code.to_category(ehrql_codelists_demographic.ethnicity_codes_6)
dataset.ethnicity = case(
    when(ethnicity6 == "1").then("White"),
    when(ethnicity6 == "2").then("Mixed"),
    when(ethnicity6 == "3").then("South Asian"),
    when(ethnicity6 == "4").then("Black"),
    when(ethnicity6 == "5").then("Other"),
    when(ethnicity6 == "6").then("Not stated"),
    default="Unknown"
)
# practice
dataset.practice = practice_registrations.for_patient_on(
    index_date).practice_pseudo_id

# learning disability
dataset.learning_disability = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_demographic.learning_disability_codes))
                               .where(clinical_events.date.is_on_or_before(index_date))
                               .exists_for_patient()
                               )
# care home
dataset.care_home = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_demographic.nhse_care_homes_codes))
                     .where(clinical_events.date.is_on_or_before(index_date))
                     .exists_for_patient()
                     )
