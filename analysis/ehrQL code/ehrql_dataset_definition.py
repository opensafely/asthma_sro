from ehrql import Dataset, years, months, weeks, case, when, Measures, INTERVAL
from ehrql.tables.beta.tpp import (
        patients, 
        medications, 
        clinical_events,
        addresses,
        practice_registrations
)
import ehrql_codelists_ast

# Function to define dataset #

def make_dataset_asthma(index_date, end_date):

    dataset = Dataset()

# define variables
    asthma_diag = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.ast_cod))
                                    .where(clinical_events.date.is_on_or_before(index_date))                       
                                    .exists_for_patient()
    )

    asthma_trt = (medications.where(medications.dmd_code.is_in(ehrql_codelists_ast.asttrt_cod))
                                    .where(medications.date.is_on_or_between(index_date,index_date - years(1)))
                                    .exists_for_patient()
    )

    latest_asthma_diag = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.ast_cod))
                                    .where(clinical_events.date.is_on_or_before(index_date - years(1)))                                
                                    .date
                                    .maximum_for_patient()
    )

    asthma_res = (clinical_events.where(clinical_events.snomedct_code.is_in(ehrql_codelists_ast.astres_cod))
                                    .sort_by(clinical_events.date)
                                    .where(clinical_events.date.is_after(latest_asthma_diag))
                                    .last_for_patient()
                                    .exists_for_patient()
    )

    ##create asthma register
    dataset.asthma_register = case(
            when((asthma_diag == True) & (asthma_trt == True) & (asthma_res == False)).then(1),
            default=0,
    )

    return dataset

    ####################################################################