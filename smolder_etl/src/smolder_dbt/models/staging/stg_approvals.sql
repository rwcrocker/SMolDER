-- FDA approval records. One row per drug per approval type.
-- We keep all approval types and filter to FDA in downstream models.
select
    struct_id,
    type                                    as approval_type,
    cast(approval as date)                  as approval_date,
    extract(year from cast(approval as date)) as approval_year,
    coalesce(orphan, 0)                     as is_orphan
from drugcentral_raw.approval
where approval is not null
