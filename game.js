const { ROLES, assignRoles } = require('./roles');

class MafiaGame {
  constructor(groupId, hostId, hostName) {
    this.groupId = groupId;
    this.hostId = hostId;
    this.state = 'lobby';
    this.players = new Map(); // userId -> player object
    this.round = 0;

    this.mafiaTarget = null;
    this.doctorTarget = null;
    this.sheriffTarget = null;
    this.sheriffResult = null;
    this.votes = new Map(); // voterId -> targetId | 'skip'

    this._addPlayer(hostId, hostName);
  }

  // ── Lobby ────────────────────────────────────────────────
  _addPlayer(userId, name) {
    if (this.players.has(userId)) return false;
    this.players.set(userId, {
      userId, name,
      role: null,
      alive: true,
      hasActed: false,
      selfSaveUsed: false,
    });
    return true;
  }

  addPlayer(userId, name) { return this._addPlayer(userId, name); }
  playerCount() { return this.players.size; }

  // ── Start ────────────────────────────────────────────────
  start() {
    assignRoles([...this.players.values()]);
    this.state = 'night';
    this.round = 1;
    this._resetNight();
  }

  // ── Night ────────────────────────────────────────────────
  _resetNight() {
    this.mafiaTarget = null;
    this.doctorTarget = null;
    this.sheriffTarget = null;
    this.sheriffResult = null;
    this.players.forEach(p => { p.hasActed = false; });
  }

  alivePlayers() {
    return [...this.players.values()].filter(p => p.alive);
  }

  aliveOthers(excludeId) {
    return this.alivePlayers().filter(p => p.userId !== excludeId);
  }

  mafiaPlayers() {
    return [...this.players.values()].filter(
      p => p.role === ROLES.MAFIA && p.alive
    );
  }

  _rolePlayer(role) {
    return [...this.players.values()].find(p => p.role === role) || null;
  }

  recordMafiaVote(voterId, targetId) {
    const p = this.players.get(voterId);
    if (!p || !p.alive || p.hasActed) return false;
    this.mafiaTarget = targetId;
    this.mafiaPlayers().forEach(mp => { mp.hasActed = true; });
    return true;
  }

  recordDoctorAction(doctorId, targetId) {
    const p = this.players.get(doctorId);
    if (!p || !p.alive || p.hasActed) return false;
    if (targetId === doctorId && p.selfSaveUsed) return false;
    if (targetId === doctorId) p.selfSaveUsed = true;
    this.doctorTarget = targetId;
    p.hasActed = true;
    return true;
  }

  recordSheriffAction(sheriffId, targetId) {
    const p = this.players.get(sheriffId);
    if (!p || !p.alive || p.hasActed) return false;
    const target = this.players.get(targetId);
    if (!target) return false;
    this.sheriffTarget = targetId;
    this.sheriffResult = target.role === ROLES.MAFIA ? 'mafia' : 'clean';
    p.hasActed = true;
    return true;
  }

  allNightDone() {
    const mafiaDone = this.mafiaPlayers().every(p => p.hasActed);
    const doctor = this._rolePlayer(ROLES.DOCTOR);
    const sheriff = this._rolePlayer(ROLES.SHERIFF);
    const doctorDone = !doctor || !doctor.alive || doctor.hasActed;
    const sheriffDone = !sheriff || !sheriff.alive || sheriff.hasActed;
    return mafiaDone && doctorDone && sheriffDone;
  }

  resolveNight() {
    let killed = null;
    if (this.mafiaTarget !== null && this.mafiaTarget !== this.doctorTarget) {
      const victim = this.players.get(this.mafiaTarget);
      if (victim) { victim.alive = false; killed = victim; }
    }
    this.state = 'day';
    return killed;
  }

  // ── Vote ─────────────────────────────────────────────────
  startVote() {
    this.state = 'vote';
    this.votes = new Map();
    this.players.forEach(p => { p.hasActed = false; });
  }

  recordVote(voterId, targetId) {
    const p = this.players.get(voterId);
    if (!p || !p.alive || p.hasActed) return false;
    this.votes.set(voterId, targetId);
    p.hasActed = true;
    return true;
  }

  allVoted() {
    return this.alivePlayers().every(p => p.hasActed);
  }

  resolveVote() {
    const tally = new Map();
    for (const target of this.votes.values()) {
      if (target !== 'skip') tally.set(target, (tally.get(target) || 0) + 1);
    }

    let eliminated = null;
    if (tally.size > 0) {
      const maxVotes = Math.max(...tally.values());
      const top = [...tally.entries()].filter(([, v]) => v === maxVotes);
      if (top.length === 1) {
        const target = this.players.get(top[0][0]);
        if (target) { target.alive = false; eliminated = target; }
      }
    }

    this._nextNight();
    return eliminated;
  }

  _nextNight() {
    this.state = 'night';
    this.round += 1;
    this._resetNight();
  }

  // ── Win check ────────────────────────────────────────────
  checkWinner() {
    const alive = this.alivePlayers();
    const mafiaAlive = alive.filter(p => p.role === ROLES.MAFIA).length;
    const townAlive = alive.filter(p => p.role !== ROLES.MAFIA).length;
    if (mafiaAlive === 0) { this.state = 'ended'; return 'citizens'; }
    if (mafiaAlive >= townAlive) { this.state = 'ended'; return 'mafia'; }
    return null;
  }

  summary() {
    return [...this.players.values()]
      .map(p => `${p.alive ? '✅' : '💀'} ${p.name} — ${p.role.emoji} ${p.role.name}`)
      .join('\n');
  }
}

module.exports = MafiaGame;
