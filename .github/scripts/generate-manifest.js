#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// Read the release payload from environment or file
const payload = JSON.parse(fs.readFileSync('manifests/release.json', 'utf8'));

const tag = payload.tag_name;
const name = payload.name || tag;
const publishedAt = payload.published_at;

// Extract assets
const assets = (payload.assets || []).map(a => ({
  id: a.id,
  name: a.name,
  size: a.size,
  content_type: a.content_type,
  download_count: a.download_count,
  url: a.browser_download_url
}));

// Categorize assets by platform
const platforms = {};
for (const asset of assets) {
  const lower = asset.name.toLowerCase();
  let platform = 'unknown';
  
  if (lower.includes('win') || lower.endsWith('.exe') || lower.endsWith('.msi')) {
    platform = 'windows';
  } else if (lower.includes('mac') || lower.includes('darwin') || lower.endsWith('.dmg') || lower.endsWith('.pkg') || lower.endsWith('.zip')) {
    platform = 'macos';
  } else if (lower.includes('linux') || lower.endsWith('.appimage') || lower.endsWith('.deb') || lower.endsWith('.rpm')) {
    platform = 'linux';
  }
  
  if (!platforms[platform]) platforms[platform] = [];
  platforms[platform].push({
    name: asset.name,
    contentType: asset.content_type,
    size: asset.size,
    downloadUrl: asset.url
  });
}

// Create manifest object
const manifest = { tag, name, publishedAt, assets, platforms };

// Write manifest.json
fs.writeFileSync(
  path.join('manifests', 'manifest.json'),
  JSON.stringify(manifest, null, 2)
);

// Create index.html
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Doc Masking - Download Links</title>
  <style>
    * { box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      max-width: 900px;
      margin: 40px auto;
      padding: 20px;
      background: #ffffff;
      color: #333;
      line-height: 1.6;
    }
    h1 { 
      color: #333;
      border-bottom: 3px solid #0066cc;
      padding-bottom: 10px;
    }
    .platform { 
      margin: 20px 0;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
      border-left: 4px solid #0066cc;
    }
    .platform h2 { 
      margin-top: 0;
      color: #0066cc;
      font-size: 1.5em;
    }
    .asset { 
      margin: 10px 0;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    .download-btn { 
      display: inline-block;
      padding: 10px 20px;
      background: #0066cc;
      color: white;
      text-decoration: none;
      border-radius: 5px;
      transition: background 0.3s;
      font-weight: 500;
    }
    .download-btn:hover { 
      background: #0052a3;
    }
    .size { 
      color: #666;
      font-size: 0.9em;
    }
    .metadata { 
      color: #666;
      margin: 10px 0;
      font-size: 0.95em;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #ddd;
      color: #666;
      font-size: 0.9em;
    }
    .api-info {
      background: #e7f3ff;
      padding: 15px;
      border-radius: 5px;
      margin: 20px 0;
    }
    .api-info code {
      background: #fff;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
    }
  </style>
</head>
<body>
  <h1>📦 Doc Masking - Release ${tag}</h1>
  <p class="metadata">📅 Published: ${new Date(publishedAt).toLocaleString()}</p>
  
  <div class="api-info">
    <strong>🔗 API Access:</strong> 
    <p>You can fetch this data programmatically from: <code>manifest.json</code></p>
  </div>

  <div id="platforms"></div>

  <script>
    const manifest = ${JSON.stringify(manifest, null, 2)};
    const platformNames = {
      windows: '🪟 Windows',
      macos: '🍎 macOS',
      linux: '🐧 Linux',
      unknown: '📦 Other'
    };
    
    const platformsDiv = document.getElementById('platforms');
    
    for (const [platform, assets] of Object.entries(manifest.platforms)) {
      const platformDiv = document.createElement('div');
      platformDiv.className = 'platform';
      
      const title = document.createElement('h2');
      title.textContent = platformNames[platform] || platform;
      platformDiv.appendChild(title);
      
      assets.forEach(asset => {
        const assetDiv = document.createElement('div');
        assetDiv.className = 'asset';
        
        const link = document.createElement('a');
        link.className = 'download-btn';
        link.href = asset.downloadUrl;
        link.textContent = asset.name;
        
        const size = document.createElement('span');
        size.className = 'size';
        size.textContent = '(' + (asset.size / 1024 / 1024).toFixed(2) + ' MB)';
        
        assetDiv.appendChild(link);
        assetDiv.appendChild(size);
        platformDiv.appendChild(assetDiv);
      });
      
      platformsDiv.appendChild(platformDiv);
    }
  </script>

  <div class="footer">
    <p><strong>Raw Data:</strong> <a href="manifest.json">manifest.json</a></p>
    <p>Generated automatically by GitHub Actions</p>
  </div>
</body>
</html>`;

fs.writeFileSync(path.join('manifests', 'index.html'), html);

console.log('✅ Manifest generated successfully!');
console.log('📄 Files created:');
console.log('  - manifests/manifest.json');
console.log('  - manifests/index.html');

