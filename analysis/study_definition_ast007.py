
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
from codelists_ast import *
from codelists_ast_indicators import *

from config import start_date, end_date, demographics

from dict_ast_reg_variables import ast_reg_variables
from dict_demographic_variables import demographic_variables

# Specify study definition

study = StudyDefinition(
    index_date=start_date,
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "uniform",
        "incidence": 0.5,
    },
    # Include Asthma register variables
    **ast_reg_variables,
    # Include demographic variables
    **demographic_variables,

    population=patients.satisfying(
        """
        # Define general population parameters
        (NOT died) AND
        (sex = 'M' OR sex = 'F') AND
        (age_band != 'missing') AND
        # Define GMS registration status
        gms_reg_status AND

        # Asthma list size age restriction
        age >= 6 AND

        # Asthma register
        asthma
        """,
    ),


    ##############################
    # Rule 1

    # Rule 1 logic
    # Asthma review occurring within the last 12 months
    ast_rev=patients.with_these_clinical_events(
        codelist=rev_cod,
        between=[
            "first_day_of_month(index_date) - 11 months", "last_day_of_month(index_date)"],
        returning="binary_flag",
        include_date_of_match=True,
        date_format="YYYY-MM-DD",
        find_last_match_in_period=True,
        return_expectations={
            "date": {"earliest": "2018-03-01", "latest": "index_date"},
            "incidence": 0.9
        },
    ),

    # Asthma written personalised asthma plan  on the same day and within the last 12 months
    ast_writpastp=patients.with_these_clinical_events(
        codelist=writpastp_cod,
        between=["ast_rev_date - 1 day", "ast_rev_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),

    # Asthma control assessment within 1 month of asthma review date
    astcontass_dat=patients.with_these_clinical_events(
        codelist=astcontass_cod,
        between=["ast_rev_date -  1 month", "ast_rev_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),

    # Asthma exacerbations recorded within 1 month of asthma review date
    astexac_dat=patients.with_these_clinical_events(
        codelist=astexacb_cod,
        between=["ast_rev_date - 1 month", "ast_rev_date"],
        returning="binary_flag",
        return_expectations={"incidence": 0.10},
    ),

    ast007_rule1=patients.satisfying(
        """
            ast_rev AND
            ast_writpastp AND
            astcontass_dat AND
            astexac_dat
            """,

    ),


    ##############################

    # Rule 2

    # People for who Asthma quality indicator care was unsuitable in previous 12 months
    denom_rule2=patients.satisfying(
        """
        NOT astpcapu
        """,
        astpcapu=patients.with_these_clinical_events(
            codelist=astpcapu_cod,
            between=["last_day_of_month(index_date) - 365 days",
                     "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={"incidence": 0.10},
        ),
    ),

    ##############################

    # Rule 3

    # People who chose not to receive asthma monitoring in previous 12 months
    denom_rule3=patients.satisfying(
        """
        NOT astmondec
        """,
        astmondec=patients.with_these_clinical_events(
            codelist=astmondec_cod,
            between=[
                "last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={"incidence": 0.10},
        ),
    ),

    ##############################

    # Rule 4

    # People who chose not to receive asthma quality indicator care in previous 12 months
    denom_rule4=patients.satisfying(
        """
        NOT astpcadec
        """,
        astpcadec=patients.with_these_clinical_events(
            codelist=astpcadec_cod,
            between=[
                "last_day_of_month(index_date) - 365 days", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={"incidence": 0.10},
        ),
    ),
    ##############################

    # Rule 5

    denom_rule5=patients.satisfying(
        """
        NOT astinvite_2
        """,
        # Latest asthma invite date
        astinvite_1=patients.with_these_clinical_events(
            codelist=astinvite_cod,
            returning="binary_flag",
            find_last_match_in_period=True,
            on_or_before="last_day_of_month(index_date)",
            include_date_of_match=True,
            date_format="YYYY-MM-DD",
        ),
        # Latest asthma invite date 7 days before the last one
        astinvite_2=patients.with_these_clinical_events(
            codelist=astinvite_cod,
            returning="binary_flag",
            find_last_match_in_period=True,
            between=[
                "last_day_of_month(index_date)- 365 days",
                "astinvite_1_date - 6 days",
            ],
        ),
    ),

    ##############################

    # Rule 6

    # Exclude people who were diagnosed with asthma in the last 3 months
    denom_rule6=patients.with_these_clinical_events(
        ast_cod,
        on_or_before="first_day_of_month(index_date) - 2 months",
        returning='binary_flag',
        return_expectations={"incidence": 0.10},
    ),
    ##############################

    # Rule 7

    # Reject patients passed to this rule who registered with the GP practice
    # in the 3 month period leading up to and including the payment period end
    # date. Select the remaining patients.
    denom_rule7=patients.registered_with_one_practice_between(
        start_date="first_day_of_month(index_date) - 2 months",
        end_date="last_day_of_month(index_date)",
        return_expectations={"incidence": 0.1},
    ),

    ##############################

    ast007_denom=patients.satisfying(
        """
    ast007_rule1

    OR
        (
        denom_rule2 AND
        denom_rule3 AND
        denom_rule4 AND
        denom_rule5 AND
        denom_rule6 AND
        denom_rule7
        )

    """
    ),

    ast007_num=patients.satisfying(
        """
    ast007_rule1

    """
    ),

)

# Create default measures
# Create default measures
measures = [
    Measure(
        id="ast007_total_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["population"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_practice_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["practice"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_age_band_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["age_band"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_sex_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["sex"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_imd_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["imd"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_region_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["region"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_ethnicity_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["ethnicity"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_learning_disability_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["learning_disability"],
        small_number_suppression=True,
    ),
    Measure(
        id="ast007_care_home_rate",
        numerator="ast007_num",
        denominator="ast007_denom",
        group_by=["care_home"],
        small_number_suppression=True,
    ),
]
