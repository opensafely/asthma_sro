
# Import functions
import json
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

    # Indicator ID: AST005
    # Description: Asthma Register: Patients aged at least 6 years old with an unresolved asthma diagnosis and have received asthma-related drug treatment in the preceding 12 months, up to the end of the reporting period

    registered=patients.registered_as_of(
            "index_date",
            return_expectations={"incidence": 0.9},
        ),

    died=patients.died_from_any_cause(
            on_or_before="index_date",
            returning="binary_flag",
            return_expectations={"incidence": 0.1}
        ),
        
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

    event_code=patients.with_these_medications(
           asttrt_cod,
            between =["last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning='code',
            return_expectations={"category": {
            "ratios": {x: 1/len(codelist_expectation_codes) for x in codelist_expectation_codes}}, }
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

    age=patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    age_band=patients.categorised_as(
        {
            "missing": "DEFAULT",
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

    population=patients.satisfying(
        """
        registered AND
        (NOT died) AND
        (sex = 'F' OR sex='M') AND
        (age_band != 'missing') AND

         # Asthma age restriction
        age >= 6

        """,
   
    ),

    ast_population=patients.satisfying(
        """
        registered AND
        (NOT died) AND
        (sex = 'F' OR sex='M') AND
        (age_band != 'missing') AND

        # Asthma register rule 1
        had_asthma AND
        had_asthma_drug_treatment AND

        # Asthma register rule 2
        NOT had_asthma_resolve AND

        # Asthma register rule 3
        age >= 6

        """,
   
    ),

     
    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence": 0.5}
    ),

    region=patients.registered_practice_as_of(
        "index_date",
        returning="nuts1_region_name",
        return_expectations={"category": {"ratios": {
            "North East": 0.1,
            "North West": 0.1,
            "Yorkshire and the Humber": 0.1,
            "East Midlands": 0.1,
            "West Midlands": 0.1,
            "East of England": 0.1,
            "London": 0.2,
            "South East": 0.2, }}}
    ),
    
    imd=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            "last_day_of_month(index_date)",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),

    learning_disability=patients.with_these_clinical_events(
        ld_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01, },
    ),
    
    care_home_status=patients.with_these_clinical_events(
        nhse_care_homes_codes,
        returning="binary_flag",
        on_or_before="index_date",
        return_expectations={"incidence": 0.2}
    )

)




# Create default measures
measures = [

    Measure(
        id="event_rate",
        numerator="ast_population",
        denominator="population",
        group_by=["imd", "region"],
        small_number_suppression=True
    ),

    Measure(
        id="event_code_rate",
        numerator="ast_population",
        denominator="population",
        group_by=["event_code"],
        small_number_suppression=False
    ),

    Measure(
        id="practice_rate",
        numerator="ast_population",
        denominator="population",
        group_by=["practice"],
        small_number_suppression=False,
    ),


]


#Add demographics measures#
# Q - does this need to be included.

for d in demographics:

    if d == ["imd", "age_band"]:
        apply_suppression = False
    
    else:
        apply_suppression = True
    
    m = Measure(
        id=f'{d}_rate',
        numerator="ast_population",
        denominator="population",
        group_by=[d],
        small_number_suppression=apply_suppression
    )
    
    measures.append(m)

    
