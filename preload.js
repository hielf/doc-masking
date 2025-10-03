const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  selectInputFile: () => ipcRenderer.invoke('select-input-file'),
  selectOutputFile: () => ipcRenderer.invoke('select-output-file'),
  processDocument: (data) => ipcRenderer.invoke('process-document', data),
  generateDryRunReport: (data) => ipcRenderer.invoke('generate-dry-run-report', data),
  copyFile: (src, dest, overwrite = false) => ipcRenderer.invoke('copy-file', { src, dest, overwrite })
});
