---
name: project-skill-template
description: Template scaffold for creating repo-local Codex skills in this project. Use this only when explicitly creating or updating a skill scaffold, not for normal report or coding tasks.
---

# Project Skill Template

## Purpose

This directory is a copyable starting point for repo-local Codex skills.

When creating a new skill:

1. Copy this directory to `.agents/skills/<new-skill-name>`.
2. Rename the frontmatter `name` to the new skill name in lowercase hyphen-case.
3. Replace the description with a concrete trigger statement that explains what the skill does and when to use it.
4. Update `agents/openai.yaml` so the UI metadata matches the new skill.
5. Delete the placeholder content that is not relevant to the new skill.

## Keep It Lean

- Put only workflow-critical instructions in this file.
- Move detailed documentation into `references/` and link it from here.
- Put deterministic helpers in `scripts/`.
- Store reusable templates or starter files in `assets/`.

## Suggested Structure

## Overview

[Replace with 1-2 sentences explaining what the skill enables.]

## Workflow

1. [Describe the first decision or action.]
2. [Describe the main execution path.]
3. [Describe how to validate the output.]

## Resources

- `scripts/example.py`: Replace with helper code when the workflow benefits from deterministic execution.
- `references/example.md`: Move detailed guidance here when `SKILL.md` starts getting long.
- `assets/example-template.txt`: Replace with templates, boilerplate, or other files the skill should use in its output.

## Validation

- Test the skill with a realistic prompt before relying on it.
- Check that the frontmatter description is specific enough to avoid unrelated triggering.
- Remove placeholder sections once the skill has real instructions.
