from cohortextractor import (
    StudyDefinition,
    patients,
    codelist,
    codelist_from_csv,
    Measure,
)

from datetime import date

from config import end_date

from codelists import ethnicity_codes

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
    },
    index_date=end_date,
    population=patients.all(),
    # ETHNICITY IN 6 CATEGORIES
    eth=patients.with_these_clinical_events(
        ethnicity_codes,
        returning="category",
        find_last_match_in_period=True,
        include_date_of_match=False,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.75,
        },
    ),
    ethnicity=patients.categorised_as(
        {
            "Unknown": "DEFAULT",
            "White": "eth='1' ",
            "Mixed": "eth='2' ",
            "South Asian": "eth='3' ",
            "Black": "eth='4' ",
            "Other": "eth='5' ",
        },
        return_expectations={
            "category": {"ratios": {"White": 0.2, "Mixed": 0.2, "South Asian": 0.2, "Black": 0.2, "Other": 0.2}},
            "incidence": 0.4,
        },
    ),
)
