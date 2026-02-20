# GA4 Service Account Setup

To enable analytics tracking, you need a Google Cloud service account with GA4 API access.

## Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project (or select existing)
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
   - Name: `bughuntertools-analytics`
   - ID: `bughuntertools-analytics`
5. Click **Create and Continue**
6. Skip role assignment (click **Continue**, then **Done**)

## Step 2: Create JSON Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Save the downloaded file as:
   ```
   /home/delmar/.openclaw/workspace/credentials/ga4-service-account.json
   ```

## Step 3: Enable GA4 API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Analytics Data API"
3. Click **Enable**

## Step 4: Grant GA4 Access

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property (Bug Hunter Tools)
3. Click **Admin** (bottom left)
4. Under **Property**, click **Property Access Management**
5. Click **+** → **Add users**
6. Enter the service account email (ends with `@PROJECT-ID.iam.gserviceaccount.com`)
7. Select role: **Viewer**
8. Click **Add**

## Step 5: Get Property ID

1. In Google Analytics Admin
2. Click **Property Settings**
3. Copy the **Property ID** (numeric, e.g., 442911175)
4. Update `analytics/config.json` with this ID

## Step 6: Test Connection

```bash
cd /home/delmar/.openclaw/workspace/projects/altclaw/analytics
./fetch_analytics.py
```

Should output:
```
✓ Analytics fetched for YYYY-MM-DD
  Saved to: history/YYYY-MM-DD.json
  Users: X
  Pageviews: X
```

## Troubleshooting

**Error: "Permission denied"**
- Service account not added to GA4 property
- Check property access management

**Error: "Property not found"**
- Wrong property ID in config.json
- Verify ID in GA4 admin

**Error: "API not enabled"**
- Enable Google Analytics Data API in Cloud Console

## Security

- Service account JSON contains private key - keep secure
- File permissions: `chmod 600 credentials/ga4-service-account.json`
- Never commit to git (already in .gitignore)
