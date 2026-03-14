<#
Simple helper to revert a commit and open a PR.
Run from repo root in PowerShell.
#>
param()

# show recent commits
Write-Host "Recent commits (latest first):" -ForegroundColor Cyan
git --no-pager log --oneline -n 20

$commit = Read-Host "Enter commit hash to revert (or blank to abort)"
if ([string]::IsNullOrWhiteSpace($commit)) {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 1
}

$ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
$branch = "revert/$($commit.Substring(0,7))-$ts"

Write-Host "Creating branch $branch" -ForegroundColor Cyan
git checkout -b $branch

Write-Host "Reverting $commit..." -ForegroundColor Cyan
# create revert commit
if (git revert $commit) {
    git push -u origin HEAD
    Write-Host "Pushed $branch. Creating PR..." -ForegroundColor Green
    gh pr create --title "revert: $($commit.Substring(0,7))" --body "Revert commit $commit" --base main --head $branch
    Write-Host "Done: PR created. You can review and merge on GitHub." -ForegroundColor Green
} else {
    Write-Host "Revert failed. Please resolve conflicts manually." -ForegroundColor Red
}
