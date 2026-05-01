const { Telegraf, Markup } = require('telegraf');
const config = require('./config');
const s = require('./strings');
const MafiaGame = require('./game');
const { ROLES } = require('./roles');

/** groupId -> MafiaGame */
const games = new Map();

// ─────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────

function fullName(user) {
  return [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username || String(user.id);
}

async function isAdmin(ctx, userId) {
  if (config.SUPER_ADMINS.has(userId)) return true;
  try {
    const member = await ctx.telegram.getChatMember(ctx.chat.id, userId);
    return ['administrator', 'creator'].includes(member.status);
  } catch { return false; }
}

function aliveKeyboard(game, excludeId, prefix) {
  const buttons = game.aliveOthers(excludeId).map(p =>
    [Markup.button.callback(p.name, `${prefix}:${p.userId}`)]
  );
  return Markup.inlineKeyboard(buttons);
}

function voteKeyboard(game, voterId) {
  const buttons = game.aliveOthers(voterId).map(p =>
    [Markup.button.callback(p.name, `vote:${p.userId}`)]
  );
  buttons.push([Markup.button.callback(s.VOTE_SKIP, 'vote:skip')]);
  return Markup.inlineKeyboard(buttons);
}

async function sendDMs(game) {
  const mafiaNames = game.mafiaPlayers().map(p => p.name).join(', ') || 'Yolg\'iz';

  for (const player of game.players.values()) {
    let text;
    if (player.role === ROLES.MAFIA) {
      const teammates = game.mafiaPlayers()
        .filter(p => p.userId !== player.userId)
        .map(p => p.name).join(', ') || 'Siz yolg\'izsiz';
      text = s.YOUR_ROLE_MAFIA(teammates);
    } else if (player.role === ROLES.DOCTOR) {
      text = s.YOUR_ROLE_DOCTOR;
    } else if (player.role === ROLES.SHERIFF) {
      text = s.YOUR_ROLE_SHERIFF;
    } else {
      text = s.YOUR_ROLE_CITIZEN;
    }
    try {
      await bot.telegram.sendMessage(player.userId, text, { parse_mode: 'MarkdownV2' });
    } catch { /* user hasn't started bot in private */ }
  }
}

async function sendNightActions(game) {
  for (const player of game.alivePlayers()) {
    try {
      if (player.role === ROLES.MAFIA) {
        await bot.telegram.sendMessage(
          player.userId,
          s.NIGHT_MAFIA_CHOOSE,
          { parse_mode: 'MarkdownV2', ...aliveKeyboard(game, player.userId, 'night_mafia') }
        );
      } else if (player.role === ROLES.DOCTOR) {
        const buttons = game.alivePlayers().map(p =>
          [Markup.button.callback(p.name, `night_doctor:${p.userId}`)]
        );
        await bot.telegram.sendMessage(
          player.userId,
          s.NIGHT_DOCTOR_CHOOSE,
          { parse_mode: 'MarkdownV2', ...Markup.inlineKeyboard(buttons) }
        );
      } else if (player.role === ROLES.SHERIFF) {
        await bot.telegram.sendMessage(
          player.userId,
          s.NIGHT_SHERIFF_CHOOSE,
          { parse_mode: 'MarkdownV2', ...aliveKeyboard(game, player.userId, 'night_sheriff') }
        );
      }
    } catch { /* user blocked bot */ }
  }
}

async function resolveAndDay(game) {
  const killed = game.resolveNight();

  const winner = game.checkWinner();
  if (winner) { await endGame(game, winner); return; }

  const dayText = killed ? s.DAY_KILLED(game.round, killed.name) : s.DAY_SAVED(game.round);
  await bot.telegram.sendMessage(game.groupId, dayText, { parse_mode: 'MarkdownV2' });

  await sleep(config.DAY_DURATION);
  if (game.checkWinner()) { await endGame(game, game.checkWinner()); return; }

  await startVote(game);
}

async function startVote(game) {
  game.startVote();
  await bot.telegram.sendMessage(game.groupId, s.VOTE_START, { parse_mode: 'MarkdownV2' });

  for (const player of game.alivePlayers()) {
    try {
      await bot.telegram.sendMessage(
        player.userId,
        s.VOTE_START,
        { parse_mode: 'MarkdownV2', ...voteKeyboard(game, player.userId) }
      );
    } catch { /* blocked */ }
  }

  await sleep(config.VOTE_DURATION);
  if (game.state === 'vote') await resolveVote(game);
}

async function resolveVote(game) {
  const eliminated = game.resolveVote();

  let text;
  if (eliminated) {
    text = s.VOTE_ELIMINATED(eliminated.name, eliminated.role.name);
  } else {
    const hasRealVotes = [...game.votes.values()].some(v => v !== 'skip');
    text = hasRealVotes ? s.VOTE_TIE : s.VOTE_SKIP_RESULT;
  }

  await bot.telegram.sendMessage(game.groupId, text, { parse_mode: 'MarkdownV2' });

  const winner = game.checkWinner();
  if (winner) { await endGame(game, winner); return; }

  await bot.telegram.sendMessage(game.groupId, s.NIGHT_START(game.round), { parse_mode: 'MarkdownV2' });
  await sendNightActions(game);

  await sleep(config.NIGHT_DURATION);
  if (game.state === 'night') await resolveAndDay(game);
}

async function endGame(game, winner) {
  const summary = game.summary();
  const text = winner === 'citizens' ? s.WIN_CITIZENS(summary) : s.WIN_MAFIA(summary);
  await bot.telegram.sendMessage(game.groupId, text, { parse_mode: 'MarkdownV2' });
  games.delete(game.groupId);
}

function findGameByPlayer(userId) {
  for (const game of games.values()) {
    if (game.players.has(userId)) return game;
  }
  return null;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─────────────────────────────────────────────────────────────
// Setup & Launch
// ─────────────────────────────────────────────────────────────

function setupBot(instance) {
  instance.start(async (ctx) => {
    await ctx.reply(
      s.START(config.CHANNEL_LINK),
      { parse_mode: 'HTML', disable_web_page_preview: false }
    );
  });

  instance.command('newgame', async (ctx) => {
    if (ctx.chat.type === 'private') return ctx.reply(s.GROUP_ONLY);
    const groupId = ctx.chat.id;
    if (games.has(groupId)) return ctx.reply(s.GAME_ALREADY_RUNNING);
    const user = ctx.from;
    games.set(groupId, new MafiaGame(groupId, user.id, fullName(user)));
    await ctx.reply(s.GAME_STARTED_LOBBY(fullName(user), config.MIN_PLAYERS), { parse_mode: 'MarkdownV2' });
  });

  instance.command('join', async (ctx) => {
    const groupId = ctx.chat.id;
    const game = games.get(groupId);
    if (!game || game.state !== 'lobby') return ctx.reply(s.GAME_NOT_RUNNING);
    const user = ctx.from;
    const added = game.addPlayer(user.id, fullName(user));
    if (!added) return ctx.reply(s.ALREADY_JOINED);
    await ctx.reply(s.JOINED(fullName(user), game.playerCount()), { parse_mode: 'MarkdownV2' });
  });

  instance.command('startgame', async (ctx) => {
    const groupId = ctx.chat.id;
    const game = games.get(groupId);
    if (!game || game.state !== 'lobby') return ctx.reply(s.GAME_NOT_RUNNING);
    if (!await isAdmin(ctx, ctx.from.id)) return ctx.reply(s.ONLY_ADMIN_CAN_START);
    if (game.playerCount() < config.MIN_PLAYERS) {
      return ctx.reply(s.NOT_ENOUGH_PLAYERS(config.MIN_PLAYERS, game.playerCount()), { parse_mode: 'MarkdownV2' });
    }
    game.start();
    const playersList = [...game.players.values()].map(p => `• ${p.name}`).join('\n');
    await ctx.reply(s.ROLES_ASSIGNED(playersList), { parse_mode: 'MarkdownV2' });
    await sendDMs(game);
    await ctx.reply(s.NIGHT_START(game.round), { parse_mode: 'MarkdownV2' });
    await sendNightActions(game);
    await sleep(config.NIGHT_DURATION);
    if (game.state === 'night') await resolveAndDay(game);
  });

  instance.command('cancel', async (ctx) => {
    const groupId = ctx.chat.id;
    const game = games.get(groupId);
    if (!game) return ctx.reply(s.NO_GAME_TO_CANCEL);
    if (!await isAdmin(ctx, ctx.from.id)) return ctx.reply(s.ONLY_ADMIN_CAN_CANCEL);
    games.delete(groupId);
    await ctx.reply(s.GAME_CANCELLED);
  });

  instance.action(/^night_mafia:(\d+)$/, async (ctx) => {
    await ctx.answerCbQuery();
    const userId = ctx.from.id;
    const targetId = parseInt(ctx.match[1]);
    const game = findGameByPlayer(userId);
    if (!game || game.state !== 'night') return ctx.editMessageText(s.GAME_NOT_IN_NIGHT);
    const player = game.players.get(userId);
    if (!player?.alive) return ctx.editMessageText(s.PLAYER_DEAD);
    if (player.hasActed) return ctx.answerCbQuery(s.ALREADY_ACTED, { show_alert: true });
    game.recordMafiaVote(userId, targetId);
    await ctx.editMessageText(s.NIGHT_ACTION_RECORDED);
    if (game.allNightDone()) resolveAndDay(game);
  });

  instance.action(/^night_doctor:(\d+)$/, async (ctx) => {
    await ctx.answerCbQuery();
    const userId = ctx.from.id;
    const targetId = parseInt(ctx.match[1]);
    const game = findGameByPlayer(userId);
    if (!game || game.state !== 'night') return ctx.editMessageText(s.GAME_NOT_IN_NIGHT);
    const player = game.players.get(userId);
    if (!player?.alive) return ctx.editMessageText(s.PLAYER_DEAD);
    if (player.hasActed) return ctx.answerCbQuery(s.ALREADY_ACTED, { show_alert: true });
    game.recordDoctorAction(userId, targetId);
    await ctx.editMessageText(s.NIGHT_ACTION_RECORDED);
    if (game.allNightDone()) resolveAndDay(game);
  });

  instance.action(/^night_sheriff:(\d+)$/, async (ctx) => {
    await ctx.answerCbQuery();
    const userId = ctx.from.id;
    const targetId = parseInt(ctx.match[1]);
    const game = findGameByPlayer(userId);
    if (!game || game.state !== 'night') return ctx.editMessageText(s.GAME_NOT_IN_NIGHT);
    const player = game.players.get(userId);
    if (!player?.alive) return ctx.editMessageText(s.PLAYER_DEAD);
    if (player.hasActed) return ctx.answerCbQuery(s.ALREADY_ACTED, { show_alert: true });
    const ok = game.recordSheriffAction(userId, targetId);
    if (!ok) return ctx.answerCbQuery(s.ALREADY_ACTED, { show_alert: true });
    const targetName = game.players.get(targetId)?.name || '?';
    const result = game.sheriffResult === 'mafia' ? s.SHERIFF_MAFIA(targetName) : s.SHERIFF_CLEAN(targetName);
    await ctx.editMessageText(result, { parse_mode: 'MarkdownV2' });
    if (game.allNightDone()) resolveAndDay(game);
  });

  instance.action(/^vote:(.+)$/, async (ctx) => {
    await ctx.answerCbQuery();
    const userId = ctx.from.id;
    const raw = ctx.match[1];
    const targetId = raw === 'skip' ? 'skip' : parseInt(raw);
    const game = findGameByPlayer(userId);
    if (!game || game.state !== 'vote') return ctx.editMessageText(s.GAME_NOT_IN_VOTE);
    const player = game.players.get(userId);
    if (!player?.alive) return ctx.editMessageText(s.PLAYER_DEAD);
    if (player.hasActed) return ctx.answerCbQuery(s.ALREADY_VOTED, { show_alert: true });
    game.recordVote(userId, targetId);
    await ctx.editMessageText(s.VOTE_RECORDED);
    if (game.allVoted()) resolveVote(game);
  });
}

if (require.main === module) {
  const bot = new Telegraf(config.TOKEN);
  setupBot(bot);
  bot.launch().then(() => console.log('Bot ishga tushdi...'));
  process.once('SIGINT',  () => bot.stop('SIGINT'));
  process.once('SIGTERM', () => bot.stop('SIGTERM'));
}

module.exports = { setupBot };
