#study start date.  should match date in project.yaml
start_date = "2019-03-01"

#study end date.  should match date in project.yaml
end_date = "2023-09-30"

#demographic variables by which code use is broken down
#select from ["sex", "age_band", "region", "imd", "ethnicity", "learning_disability"]
demographics = ["sex", "age_band", "region", "imd", "ethnicity", "learning_disability", "care_home"]


#codelist path
codelist_path = "codelists/nhsd-primary-care-domain-refsets-ast_cod.csv"

# Vertical plot lines for financial year
# Leave an empty list if no lines needed
# If a date is out of range of the graph, it will not be visible
vertical_lines = ["2019-03-31","2020-03-31", "2021-03-31","2022-03-31","2023-03-31"]