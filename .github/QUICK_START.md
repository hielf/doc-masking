# 🚀 Quick Start: Automatic Release Download Links

## What Was Created

Three files have been added to automatically generate platform-specific download links:

1. **`.github/workflows/release-manifest.yml`** - GitHub Actions workflow
2. **`.github/scripts/generate-manifest.js`** - Manifest generator script
3. **`.github/RELEASE_MANIFEST_SETUP.md`** - Complete documentation

## How It Works

```
GitHub Release Published
    ↓
Workflow Triggered
    ↓
Extract Assets & Categorize by Platform
    ↓
Generate manifest.json + index.html
    ↓
Deploy to GitHub Pages
    ↓
✅ Available at: https://hielf.github.io/doc-masking/
```

## 3-Step Setup

### 1️⃣ Enable GitHub Pages
- Go to **Settings** → **Pages**
- Set **Source** to: `GitHub Actions`
- Click **Save**

### 2️⃣ Create a Release
```bash
# Build your app
npm run build:all

# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# Then on GitHub:
# - Create new release
# - Upload your build artifacts
# - Publish!
```

### 3️⃣ Access Your Links
After ~2 minutes, visit:
- **HTML Page**: https://hielf.github.io/doc-masking/
- **JSON API**: https://hielf.github.io/doc-masking/manifest.json

## Use on Your Website

```javascript
// Fetch latest release
fetch('https://hielf.github.io/doc-masking/manifest.json')
  .then(res => res.json())
  .then(data => {
    console.log('Latest version:', data.tag);
    console.log('Windows downloads:', data.platforms.windows);
    console.log('macOS downloads:', data.platforms.macos);
    console.log('Linux downloads:', data.platforms.linux);
  });
```

## Example HTML Integration

```html
<div id="downloads"></div>

<script>
fetch('https://hielf.github.io/doc-masking/manifest.json')
  .then(res => res.json())
  .then(manifest => {
    const html = `
      <h2>Download ${manifest.name}</h2>
      ${Object.entries(manifest.platforms).map(([platform, assets]) => `
        <h3>${platform}</h3>
        ${assets.map(asset => `
          <a href="${asset.downloadUrl}" class="btn">
            ${asset.name}
          </a>
        `).join('')}
      `).join('')}
    `;
    document.getElementById('downloads').innerHTML = html;
  });
</script>
```

## Manifest Structure

```json
{
  "tag": "v1.0.0",
  "name": "Release v1.0.0",
  "publishedAt": "2025-10-08T...",
  "platforms": {
    "windows": [
      {
        "name": "Doc-Masking.exe",
        "size": 52428800,
        "downloadUrl": "https://github.com/.../Doc-Masking.exe"
      }
    ],
    "macos": [...],
    "linux": [...]
  }
}
```

## Need More Details?

See the full documentation: [RELEASE_MANIFEST_SETUP.md](./RELEASE_MANIFEST_SETUP.md)

## Troubleshooting

**Workflow not running?**
- Make sure you **published** the release (not draft)
- Check GitHub Actions tab for errors

**404 on GitHub Pages?**
- Wait 2-3 minutes after first deployment
- Verify Pages is enabled in Settings

**Wrong platform detection?**
- Edit `.github/scripts/generate-manifest.js`
- Customize the platform detection logic

---

**Need help?** Open an issue on GitHub!

