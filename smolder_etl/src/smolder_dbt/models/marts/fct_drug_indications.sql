-- FDA-approved drug to therapeutic/pharmacological class associations.
select
    d.struct_id,
    d.name              as drug_name,
    d.approval_year,
    i.indication,
    i.indication_type
from {{ ref('fct_fda_drugs') }} d
inner join {{ ref('stg_indications') }} i
    on d.struct_id = i.struct_id
