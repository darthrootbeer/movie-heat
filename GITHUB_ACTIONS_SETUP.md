# GitHub Actions Setup Guide

This guide will help you set up automated weekly email delivery of movie ratings using GitHub Actions.

## Prerequisites

1. A GitHub repository (this project)
2. Gmail account with App Password enabled
3. TMDB and OMDb API keys

## Step 1: Get Gmail App Password

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable it if not already enabled)
3. Scroll down to **App passwords**
4. Create a new app password for "Mail"
5. Copy the 16-character password (you'll need this for GitHub Secrets)

## Step 2: Add GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add each of these:

   - **TMDB_API_KEY**: Your TMDB API key
   - **OMDB_API_KEY**: Your OMDb API key
   - **GMAIL_USER**: Your Gmail address (e.g., `yourname@gmail.com`)
   - **GMAIL_APP_PASSWORD**: The 16-character app password from Step 1
   - **RECIPIENT_EMAIL**: Email address to receive the newsletter (can be same as GMAIL_USER)

## Step 3: Configure Schedule (Optional)

The workflow is set to run every Friday at 9:00 AM UTC by default.

To change the schedule, edit `.github/workflows/weekly-newsletter.yml` and modify the cron expression:

```yaml
schedule:
  - cron: '0 9 * * 5'  # Friday 9 AM UTC
```

Cron format: `minute hour day-of-month month day-of-week`
- `0 9 * * 5` = Friday 9:00 AM UTC
- `0 14 * * 1` = Monday 2:00 PM UTC (14:00)
- `0 9 * * 1,5` = Monday and Friday 9:00 AM UTC

## Step 4: Test the Workflow

1. Go to **Actions** tab in your GitHub repository
2. Click on **Weekly Movie Ratings Newsletter** workflow
3. Click **Run workflow** → **Run workflow** (manual trigger)
4. Watch it run and check your email!

## Troubleshooting

### Workflow fails with "Missing required API keys"
- Double-check that all secrets are set correctly in GitHub Settings
- Ensure secret names match exactly (case-sensitive)

### Email not received
- Check Gmail spam folder
- Verify GMAIL_APP_PASSWORD is correct (not your regular password)
- Ensure 2-Step Verification is enabled on your Google account
- Check workflow logs in GitHub Actions tab for error messages

### Want to change email frequency?
Edit the cron schedule in `.github/workflows/weekly-newsletter.yml` or trigger manually via the Actions tab.

## Manual Testing Locally

Before pushing to GitHub, you can test email functionality locally:

```bash
export GMAIL_USER='your_email@gmail.com'
export GMAIL_APP_PASSWORD='your_app_password'
export RECIPIENT_EMAIL='recipient@gmail.com'
export TMDB_API_KEY='your_tmdb_key'
export OMDB_API_KEY='your_omdb_key'

python movie_ratings.py --email
```

This will send a test email to verify everything works.
