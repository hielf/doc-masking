const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers
ipcMain.handle('select-input-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

ipcMain.handle('select-output-file', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (!result.canceled) {
    return result.filePath;
  }
  return null;
});

ipcMain.handle('process-document', async (event, { inputPath, outputPath }) => {
  return new Promise((resolve) => {
    const isWindows = process.platform === 'win32';
    const backendBase = app.isPackaged
      ? path.join(process.resourcesPath, 'python_backend')
      : path.join(__dirname, 'python_backend');

    const compiledPath = isWindows
      ? path.join(backendBase, 'dist', 'processor.exe')
      : path.join(backendBase, 'dist', 'processor');
    const scriptPath = path.join(backendBase, 'processor.py');

    const trySpawnCompiled = () => {
      if (!fs.existsSync(compiledPath)) return null;
      try {
        return spawn(compiledPath, [inputPath, outputPath]);
      } catch (_e) {
        return null;
      }
    };

    const trySpawnPython = () => {
      const pythonCandidates = isWindows ? ['python', 'python3'] : ['python3', 'python'];
      for (const cmd of pythonCandidates) {
        try {
          return spawn(cmd, [scriptPath, inputPath, outputPath]);
        } catch (_e) {
          // try next candidate
        }
      }
      return null;
    };

    const attachHandlers = (proc) => {
      let stdout = '';
      let stderr = '';
      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      proc.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (error) {
            resolve({
              status: 'error',
              message: 'Failed to parse processor output',
              error: stdout
            });
          }
        } else {
          resolve({
            status: 'error',
            message: 'Processor failed',
            error: stderr || stdout
          });
        }
      });
      proc.on('error', (_error) => {
        // If the current proc failed to start, fall back to Python once
        if (proc.__attemptedFallback !== true) {
          const fb = trySpawnPython();
          if (fb) {
            fb.__attemptedFallback = true;
            attachHandlers(fb);
            return;
          }
        }
        resolve({
          status: 'error',
          message: 'Failed to start processor',
          error: `ENOENT or not executable. Looked for compiled at ${compiledPath} and script at ${scriptPath}`
        });
      });
    };

    // Prefer compiled binary when available
    const compiled = trySpawnCompiled();
    if (compiled) {
      attachHandlers(compiled);
      return;
    }

    // Fallback to Python
    const pythonProc = trySpawnPython();
    if (pythonProc) {
      pythonProc.__attemptedFallback = true;
      attachHandlers(pythonProc);
      return;
    }

    resolve({
      status: 'error',
      message: 'Failed to start processor',
      error: `No usable processor found. Tried compiled at ${compiledPath} and Python at ${scriptPath}`
    });
  });
});
