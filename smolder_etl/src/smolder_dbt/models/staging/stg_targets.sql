-- Drug-target bioactivity records from DrugCentral act_table_full.
-- Deduped to one row per drug-target-action combination.
select distinct
    struct_id,
    target_name,
    target_class,
    gene,
    accession,
    action_type,
    cast(moa as boolean) as is_moa
from drugcentral_raw.act_table_full
where target_name is not null
