# GitHub Automation

This directory contains GitHub Actions workflows and automation scripts.

## 📁 Contents

### Workflows
- **`workflows/ci.yml`** - Continuous integration tests
- **`workflows/release-manifest.yml`** - Auto-generate download links for releases

### Scripts
- **`scripts/generate-manifest.js`** - Creates manifest.json from release data

### Documentation
- **`QUICK_START.md`** - 3-step setup guide (START HERE! 👈)
- **`RELEASE_MANIFEST_SETUP.md`** - Complete documentation with examples

## 🎯 Quick Start

To automatically generate download links when you publish a release:

1. **Enable GitHub Pages:**
   - Settings → Pages → Source: "GitHub Actions"

2. **Publish a Release:**
   - Build your app: `npm run build:all`
   - Create tag: `git tag v1.0.0 && git push origin v1.0.0`
   - On GitHub: Create release, upload artifacts, publish

3. **Access Links:**
   - Visit: `https://hielf.github.io/doc-masking/`
   - API: `https://hielf.github.io/doc-masking/manifest.json`

See [QUICK_START.md](./QUICK_START.md) for detailed instructions!
