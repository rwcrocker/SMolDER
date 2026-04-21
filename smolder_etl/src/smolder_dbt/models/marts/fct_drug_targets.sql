-- FDA-approved drug to biological target associations.
select
    d.struct_id,
    d.name          as drug_name,
    d.approval_year,
    t.target_name,
    t.target_class,
    t.gene,
    t.accession,
    t.action_type,
    t.is_moa
from {{ ref('fct_fda_drugs') }} d
inner join {{ ref('stg_targets') }} t
    on d.struct_id = t.struct_id
