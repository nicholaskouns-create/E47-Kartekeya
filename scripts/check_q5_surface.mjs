import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { CELLS, pi, unpi, neighbors, stepAxis, sliceCells } from '../q5/topology.mjs';

const root = resolve(import.meta.dirname, '..');
const live = readFileSync(resolve(root, 'website/interfaces/q5/lattice.js'), 'utf8');
const page = readFileSync(resolve(root, 'website/interfaces/q5/index.html'), 'utf8');
const sourceTopology = readFileSync(resolve(root, 'q5/topology.mjs'), 'utf8');
const deployedTopology = readFileSync(resolve(root, 'website/interfaces/q5/topology.mjs'), 'utf8');

test('Q5 packing address remains exact', () => {
  assert.equal(pi(1, 4, 2), 47);
  assert.equal(CELLS[47].word, '142');
  assert.deepEqual(unpi(78), [3, 0, 3]);
  assert.equal(CELLS[78].word, '303');
  assert.equal(CELLS[62].word, '222');
});

test('cube and torus adjacency differ only at boundaries', () => {
  assert.equal(neighbors(CELLS[62], 'cube').length, 6);
  assert.equal(neighbors(CELLS[62], 'torus').length, 6);
  assert.equal(neighbors(CELLS[100], 'cube').length, 3);
  assert.equal(neighbors(CELLS[100], 'torus').length, 6);
  assert.equal(stepAxis(CELLS[100], 'x', 1, false), 100);
  assert.equal(stepAxis(CELLS[100], 'x', 1, true), 0);
});

test('neighbor stepping reaches the expected Q5 word', () => {
  const i = stepAxis(CELLS[62], 'x', 1, false);
  assert.equal(i, 87);
  assert.equal(CELLS[i].word, '322');
});

test('Q5 slices remain 5 by 5', () => {
  for (const axis of ['x', 'y', 'z']) {
    for (let value = 0; value < 5; value += 1) {
      assert.equal(sliceCells(axis, value).length, 25);
    }
  }
});

test('deployed topology module is the canonical browser copy', () => {
  assert.equal(deployedTopology, sourceTopology);
});

test('live cube exposes executable topology controls', () => {
  for (const token of [
    'Topology · cube',
    'data-axis="x"',
    'data-axis="y"',
    'data-axis="z"',
    'Slice · all'
  ]) {
    assert.ok(page.includes(token), 'missing Q5 UI token: ' + token);
  }
  for (const token of [
    "from './topology.mjs'",
    "neighbors(cell,topology)",
    "stepAxis(cell,axis,dir,topology==='torus')",
    "sliceCells(sliceAxis,sliceValue)"
  ]) {
    assert.ok(live.includes(token), 'missing Q5 runtime token: ' + token);
  }
});
