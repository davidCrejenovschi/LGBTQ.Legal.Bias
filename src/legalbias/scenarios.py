"""Scenario templates -> scenarios -> counterfactual prompts.

A *template* has a text with slots; filling the slots gives a *scenario* s.
Rendering r(s, v) inserts the identity v into the scenario. All variants of the
same scenario must differ only in identity-marking words (checked by
`check_invariance`).
"""
from __future__ import annotations

import difflib
import json
import pathlib
import random
from dataclasses import dataclass, field

from . import identities as ids

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "data" / "templates"
TASK_FILES = {"REC": "recidivism.json", "PRE": "pretrial.json", "CRED": "credibility.json"}
PRONOUN_KEYS = ("He", "he", "His", "his", "him")


@dataclass
class Scenario:
    sid: str
    task: str
    template_id: str
    text: str                      # contains {intro}, {partner} and pronoun slots
    age: str
    levels: dict[str, int] = field(default_factory=dict)  # legally relevant factors
    manip_level: int | None = None  # level of the manipulation-check factor
    k: int = 0                      # running index, rotates partner names
    meta: dict = field(default_factory=dict)  # e.g. ground truth for real data


def load_templates(task: str, template_dir: pathlib.Path = TEMPLATE_DIR) -> dict:
    with open(template_dir / TASK_FILES[task], encoding="utf-8") as f:
        return json.load(f)


def _value(v):
    """Slot values are either plain strings or {"text": ..., "level": int}."""
    if isinstance(v, dict):
        return v["text"], v.get("level")
    return v, None


def generate_scenarios(task: str, per_template: int, seed: int = 2026,
                       template_dir: pathlib.Path = TEMPLATE_DIR) -> list[Scenario]:
    """Fill the slots of every template `per_template` times.

    The manipulation-check slot is cycled through its levels so that every
    level is represented; the other slots are sampled with a seeded RNG and
    duplicates are rejected.
    """
    spec = load_templates(task, template_dir)
    rng = random.Random(f"{seed}-{task}")
    manip = spec["manip_slot"]
    keep = {"intro": "{intro}", "partner": "{partner}", **{k: "{" + k + "}" for k in PRONOUN_KEYS}}
    out: list[Scenario] = []
    for tpl in spec["templates"]:
        slots = {**spec["shared_slots"], **tpl["slots"]}
        n_levels = len(slots[manip])
        seen: set[str] = set()
        k, attempts = 0, 0
        while k < per_template and attempts < 100 * per_template:
            attempts += 1
            fill, levels = {}, {}
            for name, values in slots.items():
                choice = values[k % n_levels] if name == manip else rng.choice(values)
                text, level = _value(choice)
                fill[name] = text
                if level is not None:
                    levels[name] = level
            key = json.dumps(fill, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            body = tpl["text"].format_map({**fill, **keep})
            out.append(Scenario(sid=f"{tpl['id']}_{k:02d}", task=task,
                                template_id=tpl["id"], text=body, age=fill["age"],
                                levels=levels, manip_level=levels.get(manip),
                                k=len(out)))
            k += 1
    return out


def render(s: Scenario, vid: str) -> str:
    """r(s, v): insert identity v into scenario s."""
    v = ids.BY_ID[vid]
    p = ids.pronouns(v.gender)
    if v.mode == "explicit":
        intro = f"a {s.age}-year-old {ids.orientation_adjective(v)} {p['noun']}"
    else:
        intro = f"a {s.age}-year-old {p['noun']}"
    partner = ""
    if v.mode == "implicit":
        partner = (f" {p['He']} lives with {p['his']} {ids.spouse(v)}, "
                   f"{ids.partner_name(v, s.k)}.")
    text = s.text.replace("{intro}", intro).replace("{partner}", partner)
    for key in PRONOUN_KEYS:
        text = text.replace("{" + key + "}", p[key])
    return text


def _tokens(text: str) -> list[str]:
    return [t.strip(".,;:") for t in text.split()]


def changed_tokens(a: str, b: str) -> set[str]:
    """Words that are inserted, deleted or replaced between two texts."""
    ta, tb = _tokens(a), _tokens(b)
    diff: set[str] = set()
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=ta, b=tb, autojunk=False).get_opcodes():
        if op != "equal":
            diff.update(ta[i1:i2])
            diff.update(tb[j1:j2])
    return diff


def check_invariance(s: Scenario, variants: list[str] | None = None) -> list[str]:
    """Condition (1): for every pair of variants with the same gender, the words
    that differ must belong to the identity lexicon. Returns the violations
    (empty list = OK)."""
    allowed = ids.IDENTITY_LEXICON | {"He", "She", "he", "she", "lives"}
    vids = variants or [v.vid for v in ids.IDENTITIES]
    rendered = {v: render(s, v) for v in vids}
    problems = []
    for i, a in enumerate(vids):
        for b in vids[i + 1:]:
            if ids.BY_ID[a].gender != ids.BY_ID[b].gender:
                continue
            bad = changed_tokens(rendered[a], rendered[b]) - allowed
            if bad:
                problems.append(f"{s.sid}: {a} vs {b}: {sorted(bad)}")
    return problems


def expand(scenarios: list[Scenario], identity_ids=None) -> list[dict]:
    """Cartesian product scenarios x identities -> prompt records (without the
    task instruction, which is added by prompts.build_messages)."""
    identity_ids = identity_ids or [i.vid for i in ids.IDENTITIES]
    rows = []
    for s in scenarios:
        for vid in identity_ids:
            v = ids.BY_ID[vid]
            rows.append({
                "pid": f"{s.sid}__{vid}", "sid": s.sid, "task": s.task,
                "template_id": s.template_id, "vid": vid, "gender": v.gender,
                "orientation": v.orientation, "mode": v.mode,
                "manip_level": s.manip_level, "levels": s.levels,
                "scenario": render(s, vid), **({"meta": s.meta} if s.meta else {}),
            })
    return rows
