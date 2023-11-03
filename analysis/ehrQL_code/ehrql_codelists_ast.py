from ehrql.codes import codelist_from_csv

######################################
## ASTHMA
######################################

# Cluster name: AST_COD
# Description: Asthma diagnosis codes
# SNOMED CT: 
ast_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-ast_cod.csv", column="code")

# Cluster name: ASTTRT_COD
# Description: Asthma treatment codes
# SNOMED CT:
asttrt_cod = codelist_from_csv("codelists/opensafely-asthma-related-drug-treatment-codes.csv",column="code",)

# Cluster name: ASTRES_COD
# Description: Asthma resolved codes
# SNOMED CT:
astres_cod = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-astres_cod.csv",column="code",)
