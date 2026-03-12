$owner='oggy8021'
$repo='Harite'
$branch='feature/monitor-split'
for($i=0;$i -lt 20;$i++){
  try{
    $res=Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo/actions/runs?branch=$branch" -Headers @{ 'User-Agent'='harite-ci-monitor' } -ErrorAction Stop
  } catch {
    Write-Output "HTTP request failed: $_"
    Start-Sleep -Seconds 15
    continue
  }
  if(-not $res.workflow_runs -or $res.total_count -eq 0){
    Write-Output "No workflow runs found yet (attempt $($i+1)/20)"
  } else {
    $run=$res.workflow_runs[0]
    $status=$run.status
    $conclusion=$run.conclusion
    $url=$run.html_url
    Write-Output "Run found: status=$status conclusion=$conclusion url=$url"
    if($status -eq 'completed'){
      if($conclusion -eq 'success'){
        Write-Output "SUCCESS: $url"
        exit 0
      } else {
        Write-Output "COMPLETED with conclusion: $conclusion. $url"
        exit 0
      }
    }
  }
  Start-Sleep -Seconds 15
}
Write-Output 'Timeout waiting for workflow runs'
exit 2
