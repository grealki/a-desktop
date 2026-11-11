import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// Import the worker without installing its help-page Anthropic dependency.
const here = dirname(fileURLToPath(import.meta.url));
const room = mkdtempSync(join(tmpdir(), 'azure-worker-'));
const sdk = join(room, 'node_modules', '@anthropic-ai', 'sdk');
mkdirSync(sdk, { recursive: true });
writeFileSync(join(sdk, 'package.json'), JSON.stringify({ name: '@anthropic-ai/sdk', type: 'module', main: 'index.js' }));
writeFileSync(join(sdk, 'index.js'), 'export default class Anthropic {}');
writeFileSync(join(room, 'package.json'), JSON.stringify({ type: 'module' }));
copyFileSync(join(here, 'src', 'index.js'), join(room, 'index.js'));
const { default: worker } = await import(pathToFileURL(join(room, 'index.js')).href);
process.on('exit', () => rmSync(room, { recursive: true, force: true }));

const ctx = { waitUntil() {} };
for (const path of ['/codes', '/codes/off', '/codes/on', '/brain', '/brain/v1/models', '/brain/v1/messages']) {
  for (const method of ['GET', 'POST']) {
    const response = await worker.fetch(new Request('https://local.test' + path, {
      method,
      ...(method === 'POST' ? { headers: { 'Content-Type': 'application/json' }, body: '{}' } : {})
    }), {}, ctx);
    assert.equal(response.status, 404, method + ' ' + path + ' must stay disabled');
    assert.equal(response.headers.get('capri-code-left'), null);
    assert.equal(response.headers.get('capri-code-expires'), null);
  }
}
console.log('PASS legacy Capri access-code and AI proxy routes stay disabled');
