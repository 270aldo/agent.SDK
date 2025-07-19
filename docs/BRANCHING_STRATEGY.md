# Git Branching Strategy

## Overview

This project follows a simplified Git Flow strategy optimized for continuous deployment.

## Branch Structure

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Strict protection rules
- **Deployments**: Automatic deployment to production
- **Direct commits**: Forbidden

#### `develop`
- **Purpose**: Integration branch for features
- **Protection**: Protected with review requirements
- **Deployments**: Automatic deployment to staging
- **Direct commits**: Only hotfixes allowed

### Supporting Branches

#### Feature Branches (`feature/*`)
- **Purpose**: New features or enhancements
- **Base**: Created from `develop`
- **Merge**: Back into `develop` via PR
- **Naming**: `feature/description-of-feature`
- **Example**: `feature/add-voice-analytics`

#### Bugfix Branches (`bugfix/*`)
- **Purpose**: Bug fixes for development
- **Base**: Created from `develop`
- **Merge**: Back into `develop` via PR
- **Naming**: `bugfix/description-of-bug`
- **Example**: `bugfix/fix-async-initialization`

#### Hotfix Branches (`hotfix/*`)
- **Purpose**: Critical production fixes
- **Base**: Created from `main`
- **Merge**: Into both `main` and `develop` via PR
- **Naming**: `hotfix/description-of-fix`
- **Example**: `hotfix/critical-auth-bypass`

#### Release Branches (`release/*`)
- **Purpose**: Prepare for production release
- **Base**: Created from `develop`
- **Merge**: Into both `main` and `develop`
- **Naming**: `release/version-number`
- **Example**: `release/1.2.0`

## Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push and create PR
git push origin feature/new-feature
# Create PR on GitHub to develop branch
```

### Bug Fixes

```bash
# 1. Create bugfix branch
git checkout develop
git pull origin develop
git checkout -b bugfix/fix-issue

# 2. Fix and commit
git add .
git commit -m "fix: resolve issue with X"

# 3. Push and create PR
git push origin bugfix/fix-issue
```

### Hotfixes (Production Issues)

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. Fix and commit
git add .
git commit -m "hotfix: resolve critical issue"

# 3. Push and create PRs to both main and develop
git push origin hotfix/critical-fix
```

### Release Process

```bash
# 1. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/1.2.0

# 2. Update version, finalize changelog
# Make any last-minute fixes

# 3. Merge to main
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# 4. Back-merge to develop
git checkout develop
git merge --no-ff release/1.2.0
git push origin develop

# 5. Delete release branch
git branch -d release/1.2.0
git push origin --delete release/1.2.0
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, semicolons, etc)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Add or update tests
- `build:` Build system or dependencies
- `ci:` CI/CD configuration
- `chore:` Other changes (update dependencies, etc)

Examples:
```
feat: add voice synthesis with ElevenLabs
fix: resolve async initialization in prediction services
docs: update API documentation
refactor: split conversation service into modules
```

## Pull Request Guidelines

1. **Title**: Use conventional commit format
2. **Description**: Include:
   - What changed
   - Why it changed
   - How to test
   - Screenshots (if UI changes)
3. **Labels**: Add appropriate labels
4. **Reviewers**: Request at least 1 review
5. **Tests**: Ensure all tests pass
6. **Documentation**: Update if needed

## Branch Protection Rules

### `main` Branch
- Require PR reviews: 2 approvals
- Dismiss stale reviews
- Require status checks:
  - CI/CD pipeline
  - Tests
  - Linting
  - Type checking
- Require branches to be up to date
- Include administrators
- Restrict who can push

### `develop` Branch
- Require PR reviews: 1 approval
- Require status checks:
  - Tests
  - Linting
- Require branches to be up to date

## Environment Mapping

| Branch    | Environment | Auto Deploy |
|-----------|------------|-------------|
| main      | Production | Yes         |
| develop   | Staging    | Yes         |
| feature/* | Preview    | On PR       |

## Version Tags

- Production releases: `v1.2.3`
- Pre-releases: `v1.2.3-beta.1`
- Release candidates: `v1.2.3-rc.1`

## Emergency Procedures

### Rolling Back Production

```bash
# Find the last stable version
git tag -l

# Create hotfix from stable tag
git checkout v1.2.2
git checkout -b hotfix/rollback-to-stable

# Push and deploy
git push origin hotfix/rollback-to-stable
```

### Skip CI

In emergencies, add `[skip ci]` to commit message:
```bash
git commit -m "hotfix: emergency fix [skip ci]"
```

## Tools and Automation

- **GitHub Actions**: CI/CD pipeline
- **Dependabot**: Dependency updates
- **CodeQL**: Security scanning
- **Branch cleanup**: Auto-delete merged branches