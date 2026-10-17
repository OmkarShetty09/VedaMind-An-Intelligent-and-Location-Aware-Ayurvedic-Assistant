from .decision import ReasonCode
from .severity import Severity

# --- entity resolution ---
ALIAS_MATCH_THRESHOLD = 0.85  # below this, the entity is ambiguous -> NEEDS_REVIEW
HERB_MIN_LENGTH = 3
DRUG_MIN_LENGTH = 2

# --- dose awareness ---
DOSE_AWARE = True  # culinary vs therapeutic dose distinction is enabled
CULINARY_CURCUMIN_DOSE_MG = 500  # below this, turmeric/curcumin rules don't fire

# --- policy mapping (severity x evidence -> decision) ---
SEVERITY_BLOCK = (Severity.MODERATE, Severity.HIGH, Severity.SEVERE)
SEVERITY_CAUTION = (Severity.LOW,)

POLYPHARMACY_ESCALATE_COUNT = 2  # >=2 moderate+ matches -> BLOCK (compounding risk)

# --- engine reliability ---
FAIL_CLOSED_REASON = ReasonCode.ENGINE_ERROR
FAIL_CLOSED_DECISION = "needs_review"
