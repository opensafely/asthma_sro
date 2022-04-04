from cohortextractor import codelist_from_csv
from config import codelist_path

# Change the path of the codelist to your chosen codelist
codelist = codelist_from_csv(codelist_path, system='snomed')

ethnicity_codes = codelist_from_csv(
        "codelists/opensafely-ethnicity.csv",
        system="ctv3",
        column="Code",
        category_column="Grouping_16",
    )

nhse_care_homes_codes = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-carehome_cod.csv",
    system="snomed",
    column="code",)

ld_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ld_cod.csv",
    system="snomed",
    column="code",
)

ast_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ast_cod.csv",
    system="snomed",
    column="code",
)

asttrt_cod = codelist_from_csv(
    "codelists/opensafely-asthma-related-drug-treatment-codes.csv",
    system="snomed",
    column="code",
)
astres_cod= codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-astres_cod.csv",
    system="snomed",
    column="code",
)