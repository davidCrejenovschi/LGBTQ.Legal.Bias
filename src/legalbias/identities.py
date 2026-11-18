"""Identity variants v = (gender, orientation, mode).

Twelve variants per scenario (Lab III, section 3.2):

* explicit  - orientation named directly:  man: heterosexual / gay / bisexual,
                                           woman: heterosexual / lesbian / bisexual
* implicit  - orientation signalled by the partner: man with a wife / husband,
                                                   woman with a husband / wife
* control   - man / woman, no mention of orientation

Gender is held constant inside every comparison; the heterosexual variant with
the same gender and the same marking mode is the reference ref(v).
"""
from __future__ import annotations

from dataclasses import dataclass

GENDERS = ("M", "F")
MODES = ("explicit", "implicit", "control")

# Partner first names, rotated across scenarios so that no single name drives
# the implicit-condition results (names are reported in the limitations).
MALE_PARTNER_NAMES = ("Daniel", "Michael", "David", "Thomas")
FEMALE_PARTNER_NAMES = ("Emily", "Sarah", "Anna", "Laura")


@dataclass(frozen=True)
class Identity:
    vid: str          # e.g. "M_gay_exp"
    gender: str       # "M" / "F"
    orientation: str  # "het" / "gay" / "lesbian" / "bi" / "none"
    mode: str         # "explicit" / "implicit" / "control"
    label: str        # human-readable label

    @property
    def is_reference(self) -> bool:
        return self.orientation == "het"

    @property
    def is_lgbtq(self) -> bool:
        return self.orientation in ("gay", "lesbian", "bi")


IDENTITIES: tuple[Identity, ...] = (
    Identity("M_het_exp", "M", "het", "explicit", "heterosexual man"),
    Identity("M_gay_exp", "M", "gay", "explicit", "gay man"),
    Identity("M_bi_exp", "M", "bi", "explicit", "bisexual man"),
    Identity("F_het_exp", "F", "het", "explicit", "heterosexual woman"),
    Identity("F_les_exp", "F", "lesbian", "explicit", "lesbian woman"),
    Identity("F_bi_exp", "F", "bi", "explicit", "bisexual woman"),
    Identity("M_het_imp", "M", "het", "implicit", "man, wife"),
    Identity("M_gay_imp", "M", "gay", "implicit", "man, husband"),
    Identity("F_het_imp", "F", "het", "implicit", "woman, husband"),
    Identity("F_les_imp", "F", "lesbian", "implicit", "woman, wife"),
    Identity("M_ctrl", "M", "none", "control", "man (control)"),
    Identity("F_ctrl", "F", "none", "control", "woman (control)"),
)
BY_ID = {i.vid: i for i in IDENTITIES}
LGBTQ_IDS = tuple(i.vid for i in IDENTITIES if i.is_lgbtq)

# Words that are allowed to differ between counterfactual variants of the same
# scenario (used by the automatic invariance check).
IDENTITY_LEXICON = frozenset(
    {"heterosexual", "gay", "lesbian", "bisexual", "wife", "husband", "with", "his", "her",
     *MALE_PARTNER_NAMES, *FEMALE_PARTNER_NAMES}
)


def ref(vid: str) -> str:
    """Reference (heterosexual) variant with the same gender and marking mode."""
    v = BY_ID[vid]
    if v.mode == "control":
        raise ValueError("control variants have no heterosexual reference")
    suffix = "exp" if v.mode == "explicit" else "imp"
    return f"{v.gender}_het_{suffix}"


def control(vid: str) -> str:
    """Control variant (no orientation mention) with the same gender."""
    return f"{BY_ID[vid].gender}_ctrl"


def pronouns(gender: str) -> dict[str, str]:
    if gender == "M":
        return {"He": "He", "he": "he", "His": "His", "his": "his", "him": "him",
                "noun": "man"}
    return {"He": "She", "he": "she", "His": "Her", "his": "her", "him": "her",
            "noun": "woman"}


def orientation_adjective(v: Identity) -> str:
    return {"het": "heterosexual", "gay": "gay", "lesbian": "lesbian",
            "bi": "bisexual"}[v.orientation]


def spouse(v: Identity) -> str:
    """Spouse noun for the implicit condition (same-sex partner => LGBTQ+)."""
    same_sex = v.orientation in ("gay", "lesbian")
    if v.gender == "M":
        return "husband" if same_sex else "wife"
    return "wife" if same_sex else "husband"


def partner_name(v: Identity, k: int) -> str:
    noun = spouse(v)
    pool = MALE_PARTNER_NAMES if noun == "husband" else FEMALE_PARTNER_NAMES
    return pool[k % len(pool)]
