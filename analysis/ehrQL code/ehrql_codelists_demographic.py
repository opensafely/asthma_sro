from ehrql.codes import codelist_from_csv

# ethnicity
ethnicity_codes_6 = codelist_from_csv("codelists/opensafely-ethnicity-snomed-0removed.csv",
                                      column="snomedcode",
                                      category_column="Grouping_6",
                                      )

# learning disability
learning_disability_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ld_cod.csv", column="code",)
# care home
nhse_care_homes_codes = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-carehome_cod.csv", column="code",)
