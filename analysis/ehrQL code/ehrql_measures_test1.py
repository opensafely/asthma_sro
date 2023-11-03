from ehrql import Dataset, years, months, weeks, case, when, Measures, INTERVAL
from ehrql.tables.beta.tpp import (
        patients, 
        medications, 
        clinical_events,
        addresses,
        practice_registrations
)
from ehrql.codes import codelist_from_csv

from ehrql_dataset_definition import make_dataset_asthma
from ehrql_define_dataset_table import index_date, end_date, dataset

## define measures

measures = Measures()

intervals = months(12).starting_on(index_date)

index_date = INTERVAL.start_date

denominator = (
    (patients.age_on(index_date + years(1)) >=6) 
    & ((patients.sex == "male") | (patients.sex == "female"))
    & (patients.date_of_death.is_after(end_date) | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on(index_date + years(1)).exists_for_patient())
)



measures.define_defaults(denominator=denominator, intervals=intervals)

measures.define_measure(
    name="ast_reg_total_rate",
    numerator=dataset.asthma_register,
)

measures.define_measure(
    name="ast_reg_practice_rate",
    numerator=dataset.asthma_register,
    group_by={"practice":dataset.practice}
)

measures.define_measure(
    name="ast_reg_age_band_rate",
    numerator=dataset.asthma_register,
    group_by={"age_band":dataset.age_band}
)

measures.define_measure(
    name="ast_reg_sex_rate",
    numerator=dataset.asthma_register,
    group_by={"sex":dataset.sex}
)

measures.define_measure(
    name="ast_reg_imd_rate",
    numerator=dataset.asthma_register,
    group_by={"imd":dataset.imd10}
)

measures.define_measure(
    name="ast_reg_region_rate",
    numerator=dataset.asthma_register,
    group_by={"region":dataset.region}
)

measures.define_measure(
    name="ast_reg_ethnicity_rate",
    numerator=dataset.asthma_register,
    group_by={"ethnicity":dataset.ethnicity}
)

measures.define_measure(
    name="ast_reg_learning_disability_rate",
    numerator=dataset.asthma_register,
    group_by={"learning_disability":dataset.learning_disability}
)

measures.define_measure(
    name="ast_reg_care_home_rate",
    numerator=dataset.asthma_register,
    group_by={"care_home":dataset.care_home}
)