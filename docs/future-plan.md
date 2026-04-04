# Future Plan

## Current Repository Rules

- Default branch is `master`.
- Students work only on their own branches.
- Student branch format: `student/{github-id}/problem-{number}`.
- Mentor branch format: `mentor/{github-id}/problem-{number}`.
- Student-to-student review is allowed.
- Merge requires 2 mentor approvals.
- Direct pushes to `master` are not allowed.

## Current Folder Structure

```text
problems/
  problem001.md

answer/
  problem001/
    github-id.py
```

- `problems/` stores problem descriptions.
- `answer/problem{number}/` stores student answers for that problem.
- Student answer file format is `{github-id}.py` for now.

## Intended PR Review Flow

The next step is to connect GitHub Actions so that when a Pull Request is opened or updated:

1. Detect the changed answer file.
2. Identify the problem number from the path.
3. Read the matching problem description from `problems/problem{number}.md`.
4. Read the submitted answer file from `answer/problem{number}/{github-id}.py`.
5. Ask AI to review whether the submission appears aligned with the problem.
6. Post an AI review comment on the Pull Request.

## MVP Goal

The first version should focus on AI feedback, not final grading.

- Check whether the PR follows the repository rules.
- Check whether the changed file path matches the expected problem folder.
- Summarize what the student attempted.
- Point out likely mistakes or missing logic.
- Leave a PR comment for mentor and student reference.

## Later Expansion

After the first PR-comment workflow is stable, consider:

- automatic file path validation
- automatic branch naming validation
- hidden test cases
- language-specific runners
- pass/fail status checks
- AI plus rule-based combined review

## Notes

- The repository currently uses collaborator access, not forks, for the main intended workflow.
- The AI review should begin as advisory feedback.
- Final accept/reject decisions should remain in mentor review until rule-based checks are stable.
