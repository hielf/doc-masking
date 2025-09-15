const fs = require('fs');
const path = require('path');

// Files to remove to reduce package size
const filesToRemove = [
  'd3dcompiler_47.dll',
  'ffmpeg.dll',
  'libEGL.dll',
  'libGLESv2.dll',
  'vk_swiftshader.dll',
  'vulkan-1.dll',
  'chrome_100_percent.pak',
  'chrome_200_percent.pak',
  'LICENSES.chromium.html'
];

// Directories to remove
const dirsToRemove = [
  'locales'
];

function cleanupDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) return;
  
  console.log(`Cleaning up ${dirPath}...`);
  
  // Remove files
  filesToRemove.forEach(file => {
    const filePath = path.join(dirPath, file);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`Removed: ${file}`);
    }
  });
  
  // Remove directories
  dirsToRemove.forEach(dir => {
    const dirPath_full = path.join(dirPath, dir);
    if (fs.existsSync(dirPath_full)) {
      fs.rmSync(dirPath_full, { recursive: true, force: true });
      console.log(`Removed directory: ${dir}`);
    }
  });
}

// Clean up win-unpacked directory
const winUnpackedPath = path.join(__dirname, '..', 'dist', 'win-unpacked');
cleanupDirectory(winUnpackedPath);

console.log('Cleanup completed!');
