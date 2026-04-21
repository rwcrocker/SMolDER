-- Drug-to-pharmacological-class mappings via struct2drgclass + drug_class lookup.
select distinct
    s2c.struct_id,
    dc.name     as indication,
    dc.source   as indication_type
from drugcentral_raw.struct2drgclass s2c
inner join drugcentral_raw.drug_class dc
    on s2c.drug_class_id = dc.id
where dc.name is not null
