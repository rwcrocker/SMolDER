-- One row per FDA-approved small molecule drug with structure + properties.
select
    s.struct_id,
    s.name,
    s.smiles,
    s.inchi,
    s.inchi_key,
    s.mol_weight,
    s.logp,
    s.tpsa,
    s.hbd,
    s.hba,
    s.arom_c,
    s.rot_bonds,
    a.approval_date,
    cast(a.approval_year as integer) as approval_year,
    a.is_orphan
from {{ ref('stg_structures') }} s
inner join {{ ref('stg_approvals') }} a
    on s.struct_id = a.struct_id
where a.approval_type = 'FDA'
