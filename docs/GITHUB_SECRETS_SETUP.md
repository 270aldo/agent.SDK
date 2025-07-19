# GitHub Secrets Configuration Guide

## Overview

This guide explains how to configure GitHub secrets for the NGX Voice Sales Agent project. These secrets are essential for CI/CD pipelines and secure deployments.

## Required Secrets

### 1. Core Application Secrets

#### `OPENAI_API_KEY`
- **Description**: OpenAI API key for GPT-4 access
- **Required for**: Development, Staging, Production
- **How to obtain**: https://platform.openai.com/api-keys

#### `ELEVENLABS_API_KEY`
- **Description**: ElevenLabs API key for voice synthesis
- **Required for**: Development, Staging, Production
- **How to obtain**: https://elevenlabs.io/api

#### `SUPABASE_URL`
- **Description**: Supabase project URL
- **Required for**: Development, Staging, Production
- **Format**: `https://xxxxx.supabase.co`

#### `SUPABASE_KEY`
- **Description**: Supabase anonymous key
- **Required for**: Development, Staging, Production
- **Note**: This is the public anonymous key, not the service key

#### `SUPABASE_SERVICE_KEY`
- **Description**: Supabase service role key (admin access)
- **Required for**: CI/CD, Migrations
- **⚠️ Critical**: Never expose this key

#### `JWT_SECRET`
- **Description**: Secret key for JWT token signing
- **Required for**: All environments
- **Generation**: Use a secure random string (min 32 characters)
```bash
openssl rand -base64 32
```

### 2. Deployment Secrets

#### `DOCKER_REGISTRY_USERNAME`
- **Description**: Docker registry username
- **Required for**: Docker image push
- **Default**: Can use GitHub username for ghcr.io

#### `DOCKER_REGISTRY_PASSWORD`
- **Description**: Docker registry password
- **Required for**: Docker image push
- **Default**: Can use GitHub token for ghcr.io

#### `STAGING_HOST`
- **Description**: Staging server hostname/IP
- **Required for**: Staging deployment
- **Example**: `staging.ngx-agent.com`

#### `STAGING_SSH_KEY`
- **Description**: SSH private key for staging server
- **Required for**: Staging deployment
- **Format**: Base64 encoded SSH key

#### `PRODUCTION_HOST`
- **Description**: Production server hostname/IP
- **Required for**: Production deployment
- **Example**: `api.ngx-agent.com`

#### `PRODUCTION_SSH_KEY`
- **Description**: SSH private key for production server
- **Required for**: Production deployment
- **Format**: Base64 encoded SSH key

### 3. Monitoring & Analytics

#### `SENTRY_DSN`
- **Description**: Sentry error tracking DSN
- **Required for**: Error monitoring
- **How to obtain**: https://sentry.io

#### `PROMETHEUS_REMOTE_WRITE_URL`
- **Description**: Prometheus remote write endpoint
- **Required for**: Metrics collection
- **Optional**: Can use local Prometheus

#### `SLACK_WEBHOOK_URL`
- **Description**: Slack webhook for notifications
- **Required for**: Deployment notifications
- **How to obtain**: https://api.slack.com/messaging/webhooks

### 4. Third-party Integrations

#### `CODECOV_TOKEN`
- **Description**: Codecov.io token for coverage reports
- **Required for**: Code coverage tracking
- **How to obtain**: https://codecov.io

#### `SONARCLOUD_TOKEN`
- **Description**: SonarCloud token for code quality
- **Required for**: Code quality analysis
- **How to obtain**: https://sonarcloud.io

## How to Add Secrets

### Via GitHub UI

1. Navigate to your repository on GitHub
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add name and value
5. Click "Add secret"

### Via GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or visit https://cli.github.com/

# Authenticate
gh auth login

# Add a secret
gh secret set SECRET_NAME --body "secret-value"

# Add from file
gh secret set SSH_KEY < ~/.ssh/id_rsa

# Add interactively (for sensitive values)
gh secret set JWT_SECRET
```

## Environment-Specific Secrets

### Development Environment
Create `.env.development`:
```env
OPENAI_API_KEY=sk-dev-xxxxx
ELEVENLABS_API_KEY=dev-xxxxx
SUPABASE_URL=https://dev-project.supabase.co
SUPABASE_KEY=dev-anon-key
JWT_SECRET=dev-secret-key
```

### Staging Environment
Use GitHub environment secrets:
1. Go to Settings → Environments
2. Create "staging" environment
3. Add environment-specific secrets

### Production Environment
Use GitHub environment secrets:
1. Go to Settings → Environments
2. Create "production" environment
3. Add protection rules:
   - Required reviewers
   - Restrict deployment branches (main only)
4. Add environment-specific secrets

## Security Best Practices

### 1. Secret Rotation
- Rotate secrets every 90 days
- Use different secrets per environment
- Document rotation in CHANGELOG

### 2. Access Control
- Limit who can access production secrets
- Use environment protection rules
- Enable audit logging

### 3. Secret Format
- No spaces or special characters in secret names
- Use uppercase with underscores
- Prefix with environment if needed

### 4. Never Commit Secrets
- Add `.env*` to `.gitignore`
- Use git-secrets to scan commits
- Review PRs for accidental secrets

## Verification

### Check Secrets in CI/CD

Add this step to your workflow to verify secrets (without exposing them):
```yaml
- name: Verify secrets
  run: |
    if [ -z "${{ secrets.OPENAI_API_KEY }}" ]; then
      echo "❌ OPENAI_API_KEY is not set"
      exit 1
    else
      echo "✅ OPENAI_API_KEY is set"
    fi
```

### Local Testing

Test with dummy values:
```bash
export OPENAI_API_KEY=test-key
export ELEVENLABS_API_KEY=test-key
python run.py --test-config
```

## Troubleshooting

### Secret Not Found
- Check secret name spelling
- Verify environment selection
- Check workflow permissions

### Invalid Secret Format
- Remove trailing spaces
- Check for special characters
- Verify base64 encoding if required

### Access Denied
- Check repository settings
- Verify workflow has secrets access
- Check environment protection rules

## Emergency Procedures

### Compromised Secret

1. **Immediately rotate the secret**
   ```bash
   gh secret set COMPROMISED_SECRET --body "new-value"
   ```

2. **Revoke old secret** (if applicable)
   - OpenAI: Revoke key in dashboard
   - Supabase: Regenerate keys
   - JWT: Force re-authentication

3. **Audit usage**
   - Check logs for unauthorized access
   - Review recent deployments
   - Monitor for suspicious activity

4. **Update all environments**
   - Development
   - Staging  
   - Production

5. **Notify team**
   - Send security alert
   - Update documentation
   - Plan security review

## Appendix: Secret Generator Script

```bash
#!/bin/bash
# generate-secrets.sh

echo "Generating secure secrets..."

# Generate JWT secret
echo "JWT_SECRET=$(openssl rand -base64 32)"

# Generate API keys (placeholders)
echo "OPENAI_API_KEY=sk-xxxxx"
echo "ELEVENLABS_API_KEY=el-xxxxx"

# Generate database password
echo "DB_PASSWORD=$(openssl rand -base64 24)"

# Generate encryption key
echo "ENCRYPTION_KEY=$(openssl rand -hex 32)"

echo "Remember to replace placeholder values with actual API keys!"
```

Make executable: `chmod +x generate-secrets.sh`