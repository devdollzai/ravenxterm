# GitHub repository configuration script
$repo_name = "ravenxterm"
$owner = "devdollzai"

# Get GitHub token
$gh_token = Read-Host "Enter your GitHub Personal Access Token"

# Headers for GitHub API
$headers = @{
    Authorization = "token $gh_token"
    Accept = "application/vnd.github.v3+json"
}

# 1. Update repository settings
$repo_settings = @{
    name = $repo_name
    description = "A Local-First AI Terminal Extension with seamless integration into your terminal environment"
    homepage = "https://devdollzai.github.io/ravenxterm"
    topics = @(
        "ai",
        "terminal",
        "python",
        "local-first",
        "llama2",
        "cli",
        "developer-tools"
    )
    has_wiki = $true
    has_issues = $true
    has_projects = $true
    allow_squash_merge = $true
    allow_merge_commit = $false
    allow_rebase_merge = $true
    delete_branch_on_merge = $true
} | ConvertTo-Json

try {
    # Update repository settings
    Write-Host "Updating repository settings..."
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo_name" -Method Patch -Headers $headers -Body $repo_settings -ContentType "application/json"
    
    # 2. Enable GitHub Pages
    $pages_settings = @{
        source = @{
            branch = "gh-pages"
            path = "/"
        }
    } | ConvertTo-Json

    Write-Host "Enabling GitHub Pages..."
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo_name/pages" -Method Post -Headers $headers -Body $pages_settings -ContentType "application/json"
    
    # 3. Set up branch protection rules
    $branch_protection = @{
        required_status_checks = @{
            strict = $true
            contexts = @("test (3.10)", "test (3.11)")
        }
        enforce_admins = $false
        required_pull_request_reviews = @{
            dismissal_restrictions = @{}
            dismiss_stale_reviews = $true
            require_code_owner_reviews = $true
            required_approving_review_count = 1
        }
        restrictions = $null
    } | ConvertTo-Json -Depth 10

    Write-Host "Setting up branch protection rules..."
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$owner/$repo_name/branches/main/protection" -Method Put -Headers $headers -Body $branch_protection -ContentType "application/json"

    # 4. Create gh-pages branch and push initial docs
    Write-Host "Setting up gh-pages branch..."
    git checkout -b gh-pages
    mkdocs build
    git add site/
    git commit -m "docs: initial documentation build"
    git push origin gh-pages
    git checkout main

    Write-Host "Repository configuration completed successfully!"
    Write-Host "Documentation will be available at: https://$owner.github.io/$repo_name"
    
} catch {
    Write-Host "Error configuring repository: $_"
    Write-Host "Response: $($_.ErrorDetails.Message)"
}
