# GUI Manual Validation Report Template

Use this template in PR comments for device validation.

## Manual device validation

- PR: [number]
- Scope: [OS/desktop/plugin]
- Date: [YYYY-MM-DD]
- Operator: [name]

## Result matrix

| Check | Status | Notes |
| --- | --- | --- |
| optimize | pass/fail/not-available | |
| apply dry-run | pass/fail/not-available | |
| apply do-it | pass/fail/not-available | |
| GUI smoke | pass/fail/not-available | |

## Screenshots

- MainWindow: [path or attached]
- Optimize form: [path or attached]
- Apply area: [path or attached]

## Artifact paths

- JSON: out/manual-validation/pr-[PR番号]-[os].json
- Markdown: out/manual-validation/pr-[PR番号]-[os].md
- Screenshot(mainwindow): out/manual-validation/pr-[PR番号]-[os]-mainwindow.png
- Screenshot(optimize): out/manual-validation/pr-[PR番号]-[os]-optimize.png
- Screenshot(apply): out/manual-validation/pr-[PR番号]-[os]-apply.png

## Failures

- Repro steps: [required if status=fail]
- Follow-up issue/PR: [optional]
