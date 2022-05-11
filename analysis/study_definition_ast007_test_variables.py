
# Import functions
import json
from ssl import ALERT_DESCRIPTION_DECODE_ERROR
from xmlrpc.server import resolve_dotted_attribute
import pandas as pd

from cohortextractor import (
    StudyDefinition, 
    patients, 
    codelist, 
    Measure
)

# Import codelists
from codelists import *

from config import start_date, end_date, codelist_path, demographics

codelist_df = pd.read_csv(codelist_path)
codelist_expectation_codes = codelist_df['code'].unique()


# Specify study definition

study = StudyDefinition(
    index_date=start_date,
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "exponential_increase",
        "incidence": 0.1,
    },
    
    # Define population parameters and denominator rules for:
    # Business Rules for Quality and Outcomes Framework (QOF) 2021/22 - Asthma

    # Resources
    # Web: https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-collections/quality-and-outcomes-framework-qof/quality-and-outcome-framework-qof-business-rules/qof-business-rules-v46.0-2021-2022-baseline-release
    # Reference document: Asthma_v46.0.docx

    # Indicator ID: AST007
    # Description: The percentage of patients with asthma, on the register, who have had an asthma review in the preceding 12 months that 
    # includes an assessment of asthma control using a validated asthma control questionnaire, a recording of the number of exacerbations, 
    # an assessment of inhaler technique and a written personalised asthma plan.
    
    registered=patients.registered_as_of(
            "last_day_of_month(index_date)",
            return_expectations={"incidence": 0.9},
        ),

    died=patients.died_from_any_cause(
            on_or_before="last_day_of_month(index_date)",
            returning="binary_flag",
            return_expectations={"incidence": 0.1}
        ),
        
    had_asthma=patients.with_these_clinical_events(
            ast_cod,
            on_or_before="last_day_of_month(index_date)",
            returning='binary_flag',
            return_expectations={"incidence": 0.9},
            include_date_of_match=True,
            date_format="YYYY-MM-DD",
            find_last_match_in_period=True,
        ),

    had_asthma_drug_treatment=patients.with_these_medications(
            asttrt_cod,
            between =["last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning='binary_flag',
            return_expectations={"incidence": 0.9}
        ),

    event_code=patients.with_these_medications(
            asttrt_cod,
            between =["last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning='code',
            return_expectations={"category": {
            "ratios": {x: 1/len(codelist_expectation_codes) for x in codelist_expectation_codes}}, }
        ),
       
    had_asthma_resolve=patients.with_these_clinical_events(
            astres_cod,
            on_or_after="had_asthma_date",
            returning="binary_flag",
            return_expectations={"incidence": 0.01}
       ),
# age_as_of function defaults to providing age at the beginning of the month specified. To 
# get the age at the end of the month (actually 1 day after), add 1 day to the value to push to the next month
    age=patients.age_as_of(
        "last_day_of_month(index_date) + 1 day" ,
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    age_band=patients.categorised_as(
        {
            "Unknown": "DEFAULT",
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.125,
                }
            },
        },

    ),


    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.5, "F": 0.5}},
        }
    ),

# Asthma practice list size is restricted to those aged 6 and over in QOF
    population=patients.satisfying(
        """
        registered AND
        (NOT died) AND

         # Asthma age restriction
        age >= 6

        """,
   
    ),

# population restrictions will already be applied to this cohort using the special variable 'population'
    ast_population=patients.satisfying(
        """
        # Asthma register rule 1
        had_asthma AND
        had_asthma_drug_treatment AND

        # Asthma register rule 2
        NOT had_asthma_resolve AND

        # Asthma register rule 3
        age >= 6

        """,
    
    ),
##############################
# Rule 1 

# Asthma review occurring within the last 12 months last date taken
    ast_rev_count=patients.with_these_clinical_events(
            codelist = rev_cod, #THIS DOESN'T WORK - USE PATIENTS.SATISFYING
            between=["first_day_of_month(index_date) - 11 months","last_day_of_month(index_date)"],
            returning="number_of_matches_in_period",
            return_expectations = {
                "incidence": 0.7,
                "int": {"distribution": "normal", "mean": 5, "stddev": 4},
            },
        ),     
    
    ast_rev_last=patients.with_these_clinical_events(
            codelist = rev_cod, #THIS DOESN'T WORK - USE PATIENTS.SATISFYING
            between=["first_day_of_month(index_date) - 11 months","last_day_of_month(index_date)"],
            returning="date",
            date_format="YYYY-MM-DD",
            find_last_match_in_period=True,
            return_expectations = {
                "date": {"earliest": "2019-03-01", "latest": "index_date"},
                "incidence": 0.9
            },
        ),   

    ast_rev_first=patients.with_these_clinical_events(
            codelist = rev_cod, #THIS DOESN'T WORK - USE PATIENTS.SATISFYING
            between=["first_day_of_month(index_date) - 11 months","last_day_of_month(index_date)"],
            returning="date",
            date_format="YYYY-MM-DD",
            find_first_match_in_period=True,
            return_expectations = {
                "date": {"earliest": "2019-03-01", "latest": "index_date"},
                "incidence": 0.9
            },
        ),     

# Asthma written personalised asthma plan  on the same day and within the last 12 months
    ast_writpastp_count=patients.with_these_clinical_events(
            codelist = writpastp_cod,
            between=["first_day_of_month(index_date) - 11 months","last_day_of_month(index_date)"],
            returning="number_of_matches_in_period",
            return_expectations = {
                "incidence": 0.7,
                "int": {"distribution": "normal", "mean": 5, "stddev": 4},
            },
        ),     
    
    ast_writpastp_first=patients.with_these_clinical_events(
            codelist = writpastp_cod,
            between=["ast_rev_first - 1 day","ast_rev_first"],
            returning="binary_flag",
            return_expectations = {
                "incidence": 0.10
            },
        ),   

    ast_writpastp_last=patients.with_these_clinical_events(
            codelist = writpastp_cod, 
            between=["ast_rev_last - 1 day","ast_rev_last"],
            returning="binary_flag",
            return_expectations = {
                "incidence": 0.10
            },
        ),     

# make measures to return values for analysis
    ast_rev_measure_count=patients.satisfying(
            """
            ast_population AND
            ast_rev_count >=1
            """
    ),

    ast_writpastp_measure_count=patients.satisfying(
            """
            ast_population AND
            ast_writpastp_count
            """
    ),


# # Asthma written personalised asthma plan  on the same day and within the last 12 months
#     ast_writpastp=patients.with_these_clinical_events(
#             codelist = writpastp_cod, #THIS DOESN'T WORK - USE PATIENTS.SATISFYING
#             between=["ast_rev_date - 1 day","ast_rev_date"],
#             returning="date",
#             date_format="YYYY-MM-DD",
#             find_last_match_in_period=True,
#             return_expectations = {
#                 "date": {"earliest": "2019-03-01", "latest": "index_date"},
#                 "incidence": 0.9
#             },
#         ),         

# # Asthma control assessment within 1 month of asthma review date
#     astcontass_dat=patients.with_these_clinical_events(
#             codelist = astcontass_cod,
#             between=["ast_rev_date -  1 month", "ast_rev_date"],
#             returning="binary_flag",
#             return_expectations={"incidence": 0.10},
#         ),

# # Asthma exacerbations recorded within 1 month of asthma review date
#     astexac_dat=patients.with_these_clinical_events(
#             codelist = astexacb_cod,
#             between=["ast_rev_date - 1 month", "ast_rev_date"],
#             returning="binary_flag",
#             return_expectations={"incidence": 0.10},
#         ),

# # Rule 1 logic
#     ast007_rule1=patients.satisfying(
#             """
#             ast_rev AND
#             astcontass_dat AND
#             astexac_dat
#             """
#     ),


)


# Create default measures
measures = [

    Measure(
        id="rev_rate",
        numerator="ast_rev_count",
        denominator="population",
        group_by="population",
        small_number_suppression=True
    ),

    Measure(
        id="rev_rate",
        numerator="ast_rev_measure_count",
        denominator="ast_population",
        group_by="population",
        small_number_suppression=True
    ),

    Measure(
        id="ast_writpastp_count_rate",
        numerator="ast_writpastp_count",
        denominator="population",
        group_by="population",
        small_number_suppression=True
    ),

    Measure(
        id="ast_writpastp_rate",
        numerator="ast_writpastp_measure_count",
        denominator="ast_population",
        group_by="population",
        small_number_suppression=True
    ),
]
