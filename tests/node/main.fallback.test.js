const path = require('path');

// Refactor mocks to keep all factories self-contained and avoid out-of-scope usage

jest.mock('electron', () => {
  const ipcMain = { handle: jest.fn() };
  const app = {
    isPackaged: false,
    whenReady: () => ({ then: () => {} }),
    on: jest.fn(),
  };
  const BrowserWindow = function () {};
  BrowserWindow.getAllWindows = () => [];
  return {
    app,
    BrowserWindow,
    ipcMain,
    dialog: {},
  };
});

jest.mock('fs', () => ({ existsSync: jest.fn(() => false) }));

jest.mock('child_process', () => ({ spawn: jest.fn() }));

describe('process-document handler', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  test('falls back to python when compiled is missing', async () => {
    const { ipcMain } = require('electron');
    const { spawn } = require('child_process');

    // Prepare fake child process with event hooks
    const events = {};
    spawn.mockImplementation(() => ({
      stdout: { on: (e, cb) => { if (e === 'data') events.stdout = cb; } },
      stderr: { on: (e, cb) => { if (e === 'data') events.stderr = cb; } },
      on: (e, cb) => { if (e === 'close') events.close = cb; if (e === 'error') events.err = cb; },
    }));

    // Now require main.js which registers the handler
    require('../../main.js');

    const call = ipcMain.handle.mock.calls.find(c => c[0] === 'process-document');
    expect(call).toBeTruthy();
    const handler = call[1];

    const p = handler({}, { inputPath: '/in.txt', outputPath: '/out.txt' });

    // Simulate python success
    const successJson = JSON.stringify({ status: 'success', message: 'ok' }) + '\n';
    events.stdout(Buffer.from(successJson));
    events.close(0);

    const result = await p;
    expect(result.status).toBe('success');

    // First spawn should be python (since compiled missing)
    const [cmd, args] = spawn.mock.calls[0];
    expect(/python3|python/.test(cmd)).toBe(true);
    expect(args[0]).toMatch(/python_backend[\/\\]processor\.py$/);
  });
});
