"""The schema is the single source of truth, so these tests guard that claim.

`spec.py` is the only place a field may be defined. The published JSON Schema and the checker
are both derived from it, and the spec markdown must not drift from it either.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aorf import spec
from aorf.check import RULES

SPEC_MD = Path(__file__).resolve().parent.parent / "spec" / "AORF-v0.1.md"
SCHEMA_JSON = Path(__file__).resolve().parent.parent / "spec" / "aorf-v0.1.schema.json"


def test_every_type_declares_a_status_field():
    """The display contract has no exemptions, so every type must name its status field."""
    for name, doc_type in spec.TYPES.items():
        assert doc_type.status_field, f"{name} declares no status field"
        assert doc_type.status_field in doc_type.fields, (
            f"{name}.status_field={doc_type.status_field} is not among its fields"
        )


def test_every_status_field_is_required_and_enumerated():
    for name, doc_type in spec.TYPES.items():
        field = doc_type.fields[doc_type.status_field]
        assert field.required, f"{name}.{doc_type.status_field} must be required"
        assert field.enum, f"{name}.{doc_type.status_field} must be an enum"


def test_display_contract_fields_required_everywhere():
    for name, doc_type in spec.TYPES.items():
        for required in ("type", "title", "description"):
            assert doc_type.fields[required].required, f"{name}.{required} must be required"


def test_json_schema_is_generated_and_current():
    """The committed schema must match what spec.py generates, or it is a second source."""
    assert SCHEMA_JSON.exists(), "run python tests/regen_schema.py"
    committed = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
    assert committed == spec.json_schema(), (
        "spec/aorf-v0.1.schema.json is stale; run python tests/regen_schema.py"
    )


def test_json_schema_covers_every_type():
    schema = spec.json_schema()
    covered = {branch["properties"]["type"]["const"] for branch in schema["oneOf"]}
    assert covered == set(spec.TYPES)


def test_json_schema_says_what_it_cannot_check():
    """Implying the schema is the whole spec would be the misleading part."""
    assert "aorf check" in spec.json_schema()["description"]


def test_rule_ids_are_unique_and_contiguous():
    from aorf.check import Issue  # noqa: F401

    ids = [fn.__name__.split("_")[0] for fn in RULES]
    assert ids == sorted(ids), "rules should be registered in order"
    assert len(set(ids)) == len(ids), "duplicate rule id"
    numbers = [int(i[1:]) for i in ids]
    assert numbers == list(range(1, len(numbers) + 1)), f"gap in rule numbering: {numbers}"


@pytest.mark.parametrize("rule", RULES)
def test_every_rule_has_a_docstring(rule):
    """A rule without a stated reason becomes a rule nobody can argue with."""
    assert rule.__doc__ and rule.__doc__.strip(), f"{rule.__name__} has no docstring"


def test_spec_markdown_documents_every_rule():
    text = SPEC_MD.read_text(encoding="utf-8")
    for fn in RULES:
        rule_id = fn.__name__.split("_")[0].upper()
        assert f"| {rule_id} |" in text, f"{rule_id} is not in the spec's rule table"


def test_spec_markdown_lists_every_enum_value():
    """A value the checker accepts but the spec never mentions is undocumented behaviour."""
    text = SPEC_MD.read_text(encoding="utf-8")
    enums = {
        "research_status": spec.RESEARCH_STATUS + spec.QUESTION_STATUS + spec.EXPERIMENT_STATUS,
        "kind": spec.KINDS,
        "verdict": spec.VERDICTS,
        "verdict_state": spec.VERDICT_STATES,
        "storage": spec.STORAGE,
        "severity": spec.SEVERITIES,
        "conclusion": spec.PRIOR_ART_CONCLUSIONS,
        "lifecycle": spec.OKF_LIFECYCLE,
        "role": spec.DATASET_ROLES,
    }
    for field, values in enums.items():
        for value in values:
            assert value in text, f"{field} value {value!r} is undocumented"


def test_agents_template_covers_the_contract():
    """The AGENTS.md template must carry all eight parts of the §10 contract."""
    from aorf.scaffold import ASSETS

    text = (ASSETS / "AGENTS.md").read_text(encoding="utf-8")
    for needle in (
        "artifacts/",  # 1 discovery
        "at most one",  # 2 link resolution
        "research_status",  # 3 types and fields
        "frontmatter before bodies",  # 4 reading rules
        "Comparability group",  # 5 derivation
        "before the run",  # 6 writing rules
        "propose",  # 7 baselines
        "get explicit approval",  # 8 cost gate
        "aorf_scaffolding.md",  # pointer for an unset-up repo
    ):
        assert needle in text, f"AGENTS.md template is missing: {needle!r}"


def test_agents_template_states_the_derivation_rules():
    """An agent computing rollups itself is legitimate, but only if told exactly how."""
    from aorf.scaffold import ASSETS

    text = (ASSETS / "AGENTS.md").read_text(encoding="utf-8")
    for needle in ("direction-aware", "excluded from any current-best", "best_run"):
        assert needle in text, f"derivation rules incomplete: {needle!r}"
