import pytest

from legalbias import identities as ids
from legalbias import scenarios as sc


def test_twelve_identity_variants():
    assert len(ids.IDENTITIES) == 12
    assert len(ids.LGBTQ_IDS) == 6
    assert sum(i.mode == "control" for i in ids.IDENTITIES) == 2


@pytest.mark.parametrize("vid", ids.LGBTQ_IDS)
def test_reference_keeps_gender_and_mode(vid):
    r = ids.BY_ID[ids.ref(vid)]
    v = ids.BY_ID[vid]
    assert r.orientation == "het" and r.gender == v.gender and r.mode == v.mode


def test_spouse_signals_orientation():
    assert ids.spouse(ids.BY_ID["M_gay_imp"]) == "husband"
    assert ids.spouse(ids.BY_ID["M_het_imp"]) == "wife"
    assert ids.spouse(ids.BY_ID["F_les_imp"]) == "wife"
    assert ids.spouse(ids.BY_ID["F_het_imp"]) == "husband"


@pytest.mark.parametrize("task", ["REC", "PRE", "CRED"])
def test_generation_is_deterministic_and_balanced(task):
    a = sc.generate_scenarios(task, 4, seed=1)
    b = sc.generate_scenarios(task, 4, seed=1)
    assert [s.text for s in a] == [s.text for s in b]
    assert len(a) == 20
    assert len({s.sid for s in a}) == 20
    # every level of the manipulation-check factor is present
    assert len({s.manip_level for s in a}) >= 2


@pytest.mark.parametrize("task", ["REC", "PRE", "CRED"])
def test_counterfactual_invariance(task):
    for s in sc.generate_scenarios(task, 4):
        assert sc.check_invariance(s) == []


def test_render_has_no_placeholders_left():
    for task in ("REC", "PRE", "CRED"):
        for s in sc.generate_scenarios(task, 2):
            for v in ids.IDENTITIES:
                text = sc.render(s, v.vid)
                assert "{" not in text and "}" not in text


def test_invariance_check_detects_a_leak():
    s = sc.generate_scenarios("REC", 1)[0]
    a = sc.render(s, "M_het_exp")
    b = sc.render(s, "M_gay_exp").replace("theft", "robbery")
    assert "robbery" in sc.changed_tokens(a, b)


def test_expand_counts():
    scen = sc.generate_scenarios("PRE", 2)
    rows = sc.expand(scen)
    assert len(rows) == len(scen) * 12
    assert {r["vid"] for r in rows} == {i.vid for i in ids.IDENTITIES}
