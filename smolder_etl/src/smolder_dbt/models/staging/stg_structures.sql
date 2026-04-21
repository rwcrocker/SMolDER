-- Drug structures with molecular properties from DrugCentral.
-- Column mapping from actual DrugCentral schema:
--   cd_molweight → mol_weight, oh_nh → hbd, o_n → hba, rotb → rot_bonds, arom_c → arom_c
select
    id                              as struct_id,
    name,
    smiles,
    inchi,
    inchikey                        as inchi_key,
    cast(cd_molweight as double)    as mol_weight,
    cast(clogp as double)           as logp,
    cast(tpsa as double)            as tpsa,
    cast(oh_nh as integer)          as hbd,
    cast(o_n as integer)            as hba,
    cast(arom_c as integer)         as arom_c,
    cast(rotb as integer)           as rot_bonds
from drugcentral_raw.structures
where smiles is not null
