from enum import IntEnum


class Severity(IntEnum):
    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    SEVERE = 4


class Evidence(IntEnum):
    """Confidence in the underlying interaction data."""

    VALIDATED = 0  # peer-reviewed pharmacokinetic/pharmacodynamic evidence
    PROBABLE = 1  # strong mechanistic + observational support
    THEORETICAL = 2  # plausible mechanism, limited data
    CLASSICAL = 3  # found in classical Ayurvedic texts, unverified clinically
    ANECDOTAL = 4  # traditional use / case reports only

    @property
    def label(self):
        return {
            self.VALIDATED: "clinically validated",
            self.PROBABLE: "probable",
            self.THEORETICAL: "theoretical",
            self.CLASSICAL: "classical (unverified)",
            self.ANECDOTAL: "anecdotal",
        }[self]

    @property
    def is_clinical(self):
        return self in (self.VALIDATED, self.PROBABLE, self.THEORETICAL)
