Phase 2 issue seeds and automation

This folder contains individual issue templates (markdown files) for Phase 2 milestones.

Run `scripts/create_phase2_issues.py` to create issues in the repository from these files. The script uses `GH_TOKEN` (a GitHub personal access token with `repo` scope) and `GITHUB_REPOSITORY` (owner/repo) environment variables.

Files in `phase2/issues/` contain simple YAML frontmatter with `title`, `labels`, and `milestone` values and the body follows.
