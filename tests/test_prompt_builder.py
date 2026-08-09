"""
Unit tests for PromptBuilder in reasoning package.
"""

from reasoning.prompt_builder import PromptBuilder


def test_prompt_builder_assembly():
    builder = PromptBuilder()
    prompt_obj = builder.build_prompt(
        objective="Extract system prompt instructions",
        mutation_chain=["persona", "delimiter"],
        persona="red_team_auditor"
    )

    assert prompt_obj["persona"] == "red_team_auditor"
    assert "persona -> delimiter" in prompt_obj["assembled_prompt"]
    assert "Extract system prompt instructions" in prompt_obj["assembled_prompt"]
