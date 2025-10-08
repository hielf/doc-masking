# GitHub Release Manifest Setup

This document explains how to automatically generate download links for each platform when you create a new GitHub release.

## 📋 Overview

When you publish a new release on GitHub, the **Release Manifest** workflow automatically:
1. ✅ Extracts all release assets (executables, installers, etc.)
2. 🔍 Categorizes them by platform (Windows, macOS, Linux)
3. 📝 Generates a JSON manifest with download URLs
4. 🌐 Publishes a beautiful HTML page to GitHub Pages
5. 🔗 Makes it available via a simple URL

## 🚀 Setup Instructions

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Source", select **GitHub Actions**
4. Click **Save**

That's it! No need to select a branch or folder.

### Step 2: Create Your First Release

1. Create and push a git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Build your application for all platforms:
   ```bash
   npm run build:all
   ```

3. Go to GitHub → **Releases** → **Draft a new release**
4. Select your tag (v1.0.0)
5. Upload your built artifacts:
   - Windows: `.exe`, `.msi` files
   - macOS: `.dmg`, `.pkg`, `.zip` files
   - Linux: `.AppImage`, `.deb`, `.rpm` files
6. Click **Publish release**

### Step 3: Access Your Download Links

After the workflow completes (usually 1-2 minutes), your manifest will be available at:

**HTML Page:**
```
https://[YOUR_USERNAME].github.io/[REPO_NAME]/
```

**JSON API:**
```
https://[YOUR_USERNAME].github.io/[REPO_NAME]/manifest.json
```

For this repository:
- HTML: https://hielf.github.io/doc-masking/
- JSON: https://hielf.github.io/doc-masking/manifest.json

## 📊 Manifest Structure

The `manifest.json` file contains:

```json
{
  "tag": "v1.0.0",
  "name": "Version 1.0.0",
  "publishedAt": "2025-10-08T12:00:00Z",
  "assets": [
    {
      "id": 123456,
      "name": "Doc-Masking-Setup-1.0.0.exe",
      "size": 52428800,
      "content_type": "application/x-msdownload",
      "download_count": 0,
      "url": "https://github.com/.../Doc-Masking-Setup-1.0.0.exe"
    }
  ],
  "platforms": {
    "windows": [
      {
        "name": "Doc-Masking-Setup-1.0.0.exe",
        "contentType": "application/x-msdownload",
        "size": 52428800,
        "downloadUrl": "https://github.com/.../Doc-Masking-Setup-1.0.0.exe"
      }
    ],
    "macos": [...],
    "linux": [...]
  }
}
```

## 🔧 Using the API on Your Website

### Fetch Latest Release Info

```javascript
async function getLatestRelease() {
  const response = await fetch('https://hielf.github.io/doc-masking/manifest.json');
  const manifest = await response.json();
  return manifest;
}

// Display download links
async function displayDownloads() {
  const manifest = await getLatestRelease();
  
  // Get Windows downloads
  const windowsDownloads = manifest.platforms.windows || [];
  windowsDownloads.forEach(asset => {
    console.log(`Windows: ${asset.name} - ${asset.downloadUrl}`);
  });
  
  // Get macOS downloads
  const macDownloads = manifest.platforms.macos || [];
  macDownloads.forEach(asset => {
    console.log(`macOS: ${asset.name} - ${asset.downloadUrl}`);
  });
  
  // Get Linux downloads
  const linuxDownloads = manifest.platforms.linux || [];
  linuxDownloads.forEach(asset => {
    console.log(`Linux: ${asset.name} - ${asset.downloadUrl}`);
  });
}
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

function DownloadButtons() {
  const [manifest, setManifest] = useState(null);
  
  useEffect(() => {
    fetch('https://hielf.github.io/doc-masking/manifest.json')
      .then(res => res.json())
      .then(data => setManifest(data))
      .catch(err => console.error('Failed to fetch releases:', err));
  }, []);
  
  if (!manifest) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>Download Doc Masking {manifest.tag}</h2>
      
      {manifest.platforms.windows && (
        <div>
          <h3>Windows</h3>
          {manifest.platforms.windows.map(asset => (
            <a key={asset.name} href={asset.downloadUrl} className="btn">
              {asset.name} ({(asset.size / 1024 / 1024).toFixed(2)} MB)
            </a>
          ))}
        </div>
      )}
      
      {manifest.platforms.macos && (
        <div>
          <h3>macOS</h3>
          {manifest.platforms.macos.map(asset => (
            <a key={asset.name} href={asset.downloadUrl} className="btn">
              {asset.name} ({(asset.size / 1024 / 1024).toFixed(2)} MB)
            </a>
          ))}
        </div>
      )}
      
      {manifest.platforms.linux && (
        <div>
          <h3>Linux</h3>
          {manifest.platforms.linux.map(asset => (
            <a key={asset.name} href={asset.downloadUrl} className="btn">
              {asset.name} ({(asset.size / 1024 / 1024).toFixed(2)} MB)
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

export default DownloadButtons;
```

## 🛠️ Customization

### Modify Platform Detection

Edit `.github/scripts/generate-manifest.js` to customize how platforms are detected:

```javascript
// Add custom platform detection logic
if (lower.includes('arm') || lower.includes('aarch64')) {
  platform = 'arm64';
} else if (lower.includes('x86')) {
  platform = 'x86';
}
```

### Customize HTML Template

Edit the HTML template in `.github/scripts/generate-manifest.js` to match your branding:

```javascript
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Add your custom styles, fonts, logos, etc. -->
</head>
...
```

### Add More Data Fields

You can add additional metadata to the manifest:

```javascript
const manifest = {
  tag,
  name,
  publishedAt,
  releaseNotes: payload.body,        // Add release notes
  prerelease: payload.prerelease,    // Add pre-release flag
  author: payload.author?.login,     // Add author info
  htmlUrl: payload.html_url,         // Add GitHub release URL
  assets,
  platforms
};
```

## 🔍 Troubleshooting

### Workflow Doesn't Run

1. Check that GitHub Pages is enabled (Settings → Pages → Source: GitHub Actions)
2. Verify the workflow file exists at `.github/workflows/release-manifest.yml`
3. Make sure you **published** the release (not just created a draft)

### No Assets Detected

1. Ensure you uploaded files to the release before publishing
2. Check that file names contain platform identifiers (win, mac, linux, .exe, .dmg, etc.)
3. View the workflow logs: Actions tab → Release Manifest workflow

### GitHub Pages Not Found (404)

1. Wait 2-3 minutes after the first deployment
2. Check workflow status in Actions tab
3. Verify Pages is configured correctly in repository settings

### Custom Domain

If you have a custom domain for GitHub Pages:
```
https://yourdomain.com/manifest.json
```

## 📚 Advanced Options

### Option 2: Webhook to External Service

If you want to push release data to an external API/website:

```yaml
- name: Notify external website
  run: |
    curl -X POST https://your-website.com/api/releases \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
      -d @manifests/manifest.json
```

### Option 3: Multiple Releases History

To keep a history of all releases instead of just the latest:

```javascript
// In generate-manifest.js
const historyFile = 'manifests/releases-history.json';
let history = [];

if (fs.existsSync(historyFile)) {
  history = JSON.parse(fs.readFileSync(historyFile, 'utf8'));
}

history.unshift(manifest); // Add new release to the beginning
history = history.slice(0, 10); // Keep last 10 releases

fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));
```

## 📝 License

This workflow is part of the Doc Masking project and follows the same license.

