from cohortextractor import StudyDefinition, patients, Measure

import json
import pandas as pd

from config import start_date, end_date
from codelists_ast import ast_cod, asttrt_cod, astres_cod

from dict_ast_variables import ast_reg_variables
from dict_demographic_variables import demographic_variables

study = StudyDefinition(
    index_date=start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },
    population=patients.satisfying(
        """
        # Define general population parameters
        (NOT died) AND
        # Define GMS registration status
        gms_reg_status AND
        # Asthma list size age restriction
        age >= 6
        """,
    ),
    # Include asthma variables
    **ast_reg_variables,
    # Include demographic variables
    **demographic_variables,
)

# Create default measures
measures = [
    Measure(
        id="ast_reg_population_rate",
        numerator="asthma",
        denominator="population",
        group_by=["population"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_practice_rate",
        numerator="asthma",
        denominator="population",
        group_by=["practice"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_age_rate",
        numerator="asthma",
        denominator="population",
        group_by=["age_band"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_sex_rate",
        numerator="asthma",
        denominator="population",
        group_by=["sex"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_imd_rate",
        numerator="asthma",
        denominator="population",
        group_by=["imd"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_region_rate",
        numerator="asthma",
        denominator="population",
        group_by=["region"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_ethnicity_rate",
        numerator="asthma",
        denominator="population",
        group_by=["ethnicity"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_learning_disability_rate",
        numerator="asthma",
        denominator="population",
        group_by=["learning_disability"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast_reg_care_home_rate",
        numerator="asthma",
        denominator="population",
        group_by=["care_home"],
        small_number_suppression=True,
    ),
]