"""Ritucharya: the six classical seasons from date + hemisphere.

Fixed solar mapping (accurate within a few days; fine for wellness advice):
  vasant  (spring)    Mar 21 - May 20
  grishma (summer)    May 21 - Jul 20
  varsha  (monsoon)   Jul 21 - Sep 20
  sharad  (autumn)    Sep 21 - Nov 20
  hemant  (late aut)  Nov 21 - Jan 20
  shishir (winter)    Jan 21 - Mar 20
Southern hemisphere shifts by six months.
"""

from datetime import date, timedelta

_BOUNDARIES = (
    ("shishir", (1, 21)),
    ("vasant", (3, 21)),
    ("grishma", (5, 21)),
    ("varsha", (7, 21)),
    ("sharad", (9, 21)),
    ("hemant", (11, 21)),
)


def season_for(d: date, northern: bool = True) -> str:
    if not northern:
        d = (d + timedelta(days=183)).replace(year=d.year)
    result = "hemant"
    for name, (m, dd) in _BOUNDARIES:
        if (d.month, d.day) >= (m, dd):
            result = name
    return result
