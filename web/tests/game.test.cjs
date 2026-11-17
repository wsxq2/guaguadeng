const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const scripts = [...html.matchAll(/<script(?: id="[^"]+")?>([\s\S]*?)<\/script>/g)];
for (const [, source] of scripts) new vm.Script(source);
const context = vm.createContext({});
vm.runInContext(scripts[0][1] + ';globalThis.api={fresh,startGame,submit,turn,aiChoice,legal}', context);
const {fresh,startGame,submit,turn,aiChoice,legal} = context.api;
for (let trial = 0; trial < 50; trial++) {
  const state = fresh();
  for (let game = 0; game < 2; game++) {
    startGame(state);
    let plays = 0;
    while (state.phase === 'playing') {
      const id = turn(state);
      const cards = aiChoice(state, id);
      assert.ok(legal(state.players[id].hand, state.round).length);
      assert.equal(submit(state, id, cards), '');
      assert.ok(++plays <= 40);
    }
    assert.equal(state.players.reduce((n, player) => n + player.won.length, 0), 10);
    assert.equal(state.players.reduce((n, player) => n + player.score, 0), 400);
  }
}
console.log('100 complete games passed');
