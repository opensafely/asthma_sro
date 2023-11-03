from datetime import datetime
from ehrql import Dataset, years, months, weeks, case, when, Measures, INTERVAL
from ehrql.tables.beta.tpp import (
    patients,
    medications,
    clinical_events,
    addresses,
    practice_registrations
)
import ehrql_codelists_ast
import ehrql_codelists_demographic


############################
# set intervals + dates

def calculate_num_intervals(start_date):
    """
    Calculate the number of intervals between the start date and the start of the latest full month
    Args:
        start_date: the start date of the study period
    Returns:
        num_intervals (int): the number of intervals between the start date and the start of the latest full month
    """
    now = datetime.now()
    start_of_latest_full_month = datetime(now.year, now.month, 1)

    num_intervals = (start_of_latest_full_month.year - datetime.strptime(start_date, "%Y-%m-%d").year) * 12 + (start_of_latest_full_month.month - datetime.strptime(start_date, "%Y-%m-%d").month)

    return num_intervals

start_date = "2019-03-31"
num_intervals = calculate_num_intervals(start_date)
intervals = months(num_intervals).starting_on(start_date)


############################

population = (
    (patients.age_on(INTERVAL.start_date + years(1)) >= 6)
    & ((patients.sex == "male") | (patients.sex == "female"))
    & (patients.date_of_death.is_after(INTERVALS.start_date) | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on(index_date).exists_for_patient())
)


###########################
# define asthma variables #

asthma_diag = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.ast_cod))
               .where(clinical_events.date.is_on_or_before(INTERVAL.start_date+years(1)))
               .exists_for_patient()
               )

asthma_trt = (medications.where(medications.dmd_code.is_in(ehrql_codelists_ast.asttrt_cod))
              .where(medications.date.is_on_or_between(INTERVAL.start_date, INTERVAL.start_date + years(1)))
              .exists_for_patient()
              )

latest_asthma_diag = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.ast_cod))
                      .where(clinical_events.date.is_on_or_before(INTERVAL.start_date+years(1)))
                      .date
                      .maximum_for_patient()
                      )

asthma_res = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.astres_cod))
              .sort_by(clinical_events.date)
              .where(clinical_events.date.is_after(latest_asthma_diag))
              .last_for_patient()
              .exists_for_patient()
              )

# create asthma register
asthma_register = case(
    when((asthma_diag == True) & (asthma_trt == True)
         & (asthma_res == False)).then(1),
    default=0,
)

##############################
# define population varables #

# demographic variables #

# age bands
age_band = case(
    when((patients.age_on(INTERVAL.start_date) >= 6) & (
        patients.age_on(INTERVAL.start_date) < 20)).then("6-19"),
    when((patients.age_on(INTERVAL.start_date) >= 20) & (
        patients.age_on(INTERVAL.start_date) < 30)).then("20-29"),
    when((patients.age_on(INTERVAL.start_date) >= 30) & (
        patients.age_on(INTERVAL.start_date) < 40)).then("30-39"),
    when((patients.age_on(INTERVAL.start_date) >= 40) & (
        patients.age_on(INTERVAL.start_date) < 50)).then("40-49"),
    when((patients.age_on(INTERVAL.start_date) >= 50) & (
        patients.age_on(INTERVAL.start_date) < 60)).then("50-59"),
    when((patients.age_on(INTERVAL.start_date) >= 60) & (
        patients.age_on(INTERVAL.start_date) < 70)).then("60-69"),
    when((patients.age_on(INTERVAL.start_date) >= 70) & (
        patients.age_on(INTERVAL.start_date) < 80)).then("70-79"),
    when((patients.age_on(INTERVAL.start_date) >= 80)).then("80+"),
    default="NULL"
)

# sex
sex = patients.sex

# region
region = practice_registrations.for_patient_on(
    INTERVAL.start_date).practice_nuts1_region_name

# IMD decile
imd_value = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
imd10 = case(
    when((imd_value >= 0) & (imd_value < int(32844 * 1 / 10))).then("1 (most deprived)"),
    when(imd_value < int(32844 * 2 / 10)).then("2"),
    when(imd_value < int(32844 * 3 / 10)).then("3"),
    when(imd_value < int(32844 * 4 / 10)).then("4"),
    when(imd_value < int(32844 * 5 / 10)).then("5"),
    when(imd_value < int(32844 * 6 / 10)).then("6"),
    when(imd_value < int(32844 * 7 / 10)).then("7"),
    when(imd_value < int(32844 * 8 / 10)).then("8"),
    when(imd_value < int(32844 * 9 / 10)).then("9"),
    when(imd_value >= int(32844 * 9 / 10)).then("10 (least deprived)"),
    default="unknown"
)

# ethnicity (6 groups)
ethnicitycode = clinical_events.where(clinical_events.snomedct_code.is_in(
    ehrql_codelists_demographic.ethnicity_codes_6)).sort_by(clinical_events.date).last_for_patient().snomedct_code.to_category(ehrql_codelists_demographic.ethnicity_codes_6)
ethnicity = case(
    when(ethnicitycode == "1").then("White"),
    when(ethnicitycode == "2").then("Mixed"),
    when(ethnicitycode == "3").then("South Asian"),
    when(ethnicitycode == "4").then("Black"),
    when(ethnicitycode == "5").then("Other"),
    when(ethnicitycode == "6").then("Not stated"),
    default="Unknown"
)
# practice
practice = practice_registrations.for_patient_on(
    INTERVAL.start_date).practice_pseudo_id

# learning disability
learning_disability = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_demographic.learning_disability_codes))
                               .where(clinical_events.date.is_on_or_before(INTERVAL.start_date))
                               .exists_for_patient()
                               )
# care home
care_home = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_demographic.nhse_care_homes_codes))
                     .where(clinical_events.date.is_on_or_before(INTERVAL.start_date))
                     .exists_for_patient()
                     )

###########################
# define measures #

measures = Measures()

measures.define_defaults(denominator=population, intervals=months(num_intervals).starting_on(start_date))

measures.define_measure(
    name="ast_reg_total_rate",
    numerator=asthma_register,
)

measures.define_measure(
    name="ast_reg_practice_rate",
    numerator=asthma_register,
    group_by={"practice": practice}
)

measures.define_measure(
    name="ast_reg_age_band_rate",
    numerator=asthma_register,
    group_by={"age_band": age_band}
)

measures.define_measure(
    name="ast_reg_sex_rate",
    numerator=asthma_register,
    group_by={"sex": sex}
)

measures.define_measure(
    name="ast_reg_imd_rate",
    numerator=asthma_register,
    group_by={"imd": imd10}
)

measures.define_measure(
    name="ast_reg_region_rate",
    numerator=asthma_register,
    group_by={"region": region}
)

measures.define_measure(
    name="ast_reg_ethnicity_rate",
    numerator=asthma_register,
    group_by={"ethnicity": ethnicity}
)

measures.define_measure(
    name="ast_reg_learning_disability_rate",
    numerator=asthma_register,
    group_by={"learning_disability": learning_disability}
)

measures.define_measure(
    name="ast_reg_care_home_rate",
    numerator=asthma_register,
    group_by={"care_home": care_home}
)
