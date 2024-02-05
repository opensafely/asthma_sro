# Define common variables needed across indicators here
# See https://docs.opensafely.org/study-def-tricks/

import pandas as pd
from config import start_date, end_date
from cohortextractor import patients
from codelists_ast import (
    ast_cod,
    asttrt_cod,
    astres_cod,
)

# Define dictionary of variables needed for asthma register:
# Patients with an unresolved diagnosis of asthma
ast_reg_variables = dict(
  
# Asthma specific variables    
    had_asthma=patients.with_these_clinical_events(
            ast_cod,
            on_or_before="last_day_of_month(index_date)",
            returning='binary_flag',
            return_expectations={"incidence": 0.9}
    ),

    had_asthma_drug_treatment=patients.with_these_medications(
            asttrt_cod,
            between =["last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning='binary_flag',
            return_expectations={"incidence": 0.9}
    ),

    latest_asthma_diag_date=patients.with_these_clinical_events(
            ast_cod,
            on_or_before="last_day_of_month(index_date)",
            returning="date",
            date_format="YYYY-MM-DD",
            find_last_match_in_period=True
    ),
       
    had_asthma_resolve=patients.with_these_clinical_events(
            astres_cod,
            on_or_after="latest_asthma_diag_date",
            returning="binary_flag",
            return_expectations={"incidence": 0.01}
    ),
# age_as_of function defaults to providing age at the beginning of the month specified. To 
# get the age at the end of the month (actually 1 day after), add 1 day to the value to push to the next month
    age_ast_reg = patients.age_as_of(
        "last_day_of_month(index_date) + 1 day",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

# population restrictions will already be applied to this cohort using the special variable 'population'
    asthma=patients.satisfying(
        """
        # Asthma register rule 1
        had_asthma AND
        had_asthma_drug_treatment AND
        # Asthma register rule 2
        NOT had_asthma_resolve AND
        # Asthma register rule 3
        age_ast_reg >= 6
        """
    ),
)