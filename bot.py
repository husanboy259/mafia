import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from telegram.constants import ParseMode

import config
import strings as s
from game import MafiaGame
from roles import MAFIA, DOCTOR, SHERIFF

logging.basicConfig(level=logging.INFO)

# group_id -> MafiaGame
games: dict[int, MafiaGame] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_name(user) -> str:
    return user.full_name or user.username or str(user.id)


def _alive_keyboard(game: MafiaGame, exclude_id: int, prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{p.name}", callback_data=f"{prefix}:{p.user_id}")]
        for p in game.alive_others(exclude_id)
    ]
    return InlineKeyboardMarkup(buttons)


def _vote_keyboard(game: MafiaGame, voter_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{p.name}", callback_data=f"vote:{p.user_id}")]
        for p in game.alive_others(voter_id)
    ]
    buttons.append([InlineKeyboardButton(s.VOTE_SKIP, callback_data="vote:skip")])
    return InlineKeyboardMarkup(buttons)


async def _send_role_dms(game: MafiaGame, app: Application) -> None:
    mafia_names = ", ".join(
        p.name for p in game.players.values() if p.role == MAFIA
    )
    for player in game.players.values():
        if player.role == MAFIA:
            teammates = ", ".join(
                p.name for p in game.players.values()
                if p.role == MAFIA and p.user_id != player.user_id
            ) or "Siz yolg'izsiz"
            text = s.YOUR_ROLE_MAFIA.format(teammates=teammates)
        elif player.role == DOCTOR:
            text = s.YOUR_ROLE_DOCTOR
        elif player.role == SHERIFF:
            text = s.YOUR_ROLE_SHERIFF
        else:
            text = s.YOUR_ROLE_CITIZEN

        try:
            await app.bot.send_message(
                chat_id=player.user_id, text=text, parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass  # user hasn't started the bot in private


async def _send_night_actions(game: MafiaGame, app: Application) -> None:
    for player in game.alive_players():
        if player.role == MAFIA:
            keyboard = _alive_keyboard(game, player.user_id, "night_mafia")
            try:
                await app.bot.send_message(
                    chat_id=player.user_id,
                    text=s.NIGHT_MAFIA_CHOOSE,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception:
                pass
        elif player.role == DOCTOR:
            # Doctor can target self too
            buttons = [
                [InlineKeyboardButton(p.name, callback_data=f"night_doctor:{p.user_id}")]
                for p in game.alive_players()
            ]
            try:
                await app.bot.send_message(
                    chat_id=player.user_id,
                    text=s.NIGHT_DOCTOR_CHOOSE,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception:
                pass
        elif player.role == SHERIFF:
            keyboard = _alive_keyboard(game, player.user_id, "night_sheriff")
            try:
                await app.bot.send_message(
                    chat_id=player.user_id,
                    text=s.NIGHT_SHERIFF_CHOOSE,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception:
                pass


async def _check_night_done(game: MafiaGame, app: Application) -> None:
    if not game.all_night_actions_done():
        return
    await _resolve_and_day(game, app)


async def _resolve_and_day(game: MafiaGame, app: Application) -> None:
    killed = game.resolve_night()

    winner = game.check_winner()
    if winner:
        await _end_game(game, winner, app)
        return

    if killed:
        text = s.DAY_START_KILLED.format(round=game.round, name=killed.name)
    else:
        text = s.DAY_START_SAVED.format(round=game.round)

    await app.bot.send_message(
        game.group_id, text, parse_mode=ParseMode.MARKDOWN
    )

    await asyncio.sleep(config.DAY_DURATION)

    winner = game.check_winner()
    if winner:
        await _end_game(game, winner, app)
        return

    await _start_vote(game, app)


async def _start_vote(game: MafiaGame, app: Application) -> None:
    game.start_vote()
    await app.bot.send_message(
        game.group_id, s.VOTE_START, parse_mode=ParseMode.MARKDOWN
    )
    for player in game.alive_players():
        keyboard = _vote_keyboard(game, player.user_id)
        try:
            await app.bot.send_message(
                chat_id=player.user_id,
                text=s.VOTE_START,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            pass

    await asyncio.sleep(config.VOTE_DURATION)

    if game.state == "vote":
        await _resolve_vote(game, app)


async def _resolve_vote(game: MafiaGame, app: Application) -> None:
    eliminated = game.resolve_vote()

    if eliminated:
        text = s.VOTE_RESULT_ELIMINATED.format(
            name=eliminated.name, role=eliminated.role.name
        )
    else:
        tally = {}
        for t in game.votes.values():
            tally[t] = tally.get(t, 0) + 1
        top_vals = [v for k, v in tally.items() if k is not None]
        if top_vals and len([v for v in tally.values() if v == max(top_vals)]) > 1:
            text = s.VOTE_RESULT_TIE
        else:
            text = s.VOTE_RESULT_SKIP

    await app.bot.send_message(game.group_id, text, parse_mode=ParseMode.MARKDOWN)

    winner = game.check_winner()
    if winner:
        await _end_game(game, winner, app)
        return

    # Next night
    night_text = s.NIGHT_START.format(round=game.round)
    await app.bot.send_message(game.group_id, night_text, parse_mode=ParseMode.MARKDOWN)
    await _send_night_actions(game, app)

    await asyncio.sleep(config.NIGHT_DURATION)
    if game.state == "night":
        await _resolve_and_day(game, app)


async def _end_game(game: MafiaGame, winner: str, app: Application) -> None:
    summary = game.summary()
    if winner == "citizens":
        text = s.WIN_CITIZENS.format(summary=summary)
    else:
        text = s.WIN_MAFIA.format(summary=summary)

    await app.bot.send_message(game.group_id, text, parse_mode=ParseMode.MARKDOWN)
    games.pop(game.group_id, None)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def cmd_newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu komanda faqat guruh chatda ishlaydi.")
        return

    if group_id in games:
        await update.message.reply_text(s.GAME_ALREADY_RUNNING)
        return

    user = update.effective_user
    game = MafiaGame(group_id, user.id, _full_name(user))
    games[group_id] = game

    text = s.GAME_STARTED_LOBBY.format(
        min_players=config.MIN_PLAYERS,
        host=_full_name(user),
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    game = games.get(group_id)

    if not game or game.state != "lobby":
        await update.message.reply_text(s.GAME_NOT_RUNNING)
        return

    user = update.effective_user
    added = game.add_player(user.id, _full_name(user))

    if not added:
        await update.message.reply_text(s.ALREADY_JOINED)
        return

    text = s.JOINED.format(name=_full_name(user), count=game.player_count())
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_startgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    game = games.get(group_id)

    if not game or game.state != "lobby":
        await update.message.reply_text(s.GAME_NOT_RUNNING)
        return

    user = update.effective_user
    if not await _is_admin(group_id, user.id, ctx.application):
        await update.message.reply_text(s.ONLY_ADMIN_CAN_START)
        return

    if game.player_count() < config.MIN_PLAYERS:
        await update.message.reply_text(
            s.NOT_ENOUGH_PLAYERS.format(
                min_players=config.MIN_PLAYERS, count=game.player_count()
            )
        )
        return

    game.start()

    players_list = "\n".join(
        f"• {p.name}" for p in game.players.values()
    )
    await update.message.reply_text(
        s.ROLES_ASSIGNED.format(players=players_list),
        parse_mode=ParseMode.MARKDOWN,
    )

    await _send_role_dms(game, ctx.application)

    night_text = s.NIGHT_START.format(round=game.round)
    await update.message.reply_text(night_text, parse_mode=ParseMode.MARKDOWN)

    await _send_night_actions(game, ctx.application)

    await asyncio.sleep(config.NIGHT_DURATION)
    if game.state == "night":
        await _resolve_and_day(game, ctx.application)


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    game = games.get(group_id)

    if not game:
        await update.message.reply_text(s.NO_GAME_TO_CANCEL)
        return

    user = update.effective_user
    if not await _is_admin(group_id, user.id, ctx.application):
        await update.message.reply_text(s.ONLY_ADMIN_CAN_CANCEL)
        return

    games.pop(group_id, None)
    await update.message.reply_text(s.GAME_CANCELLED)


# ---------------------------------------------------------------------------
# Callback query handlers (inline keyboards in private chat)
# ---------------------------------------------------------------------------

async def _is_admin(chat_id: int, user_id: int, app: Application) -> bool:
    if user_id in config.SUPER_ADMINS:
        return True
    member = await app.bot.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")


def _find_game_by_player(user_id: int) -> MafiaGame | None:
    for game in games.values():
        if user_id in game.players:
            return game
    return None


async def cb_night_mafia(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.split(":")[1])

    game = _find_game_by_player(user_id)
    if not game or game.state != "night":
        await query.edit_message_text(s.GAME_NOT_IN_NIGHT)
        return

    player = game.players.get(user_id)
    if not player or not player.alive:
        await query.edit_message_text(s.PLAYER_DEAD_CANNOT_ACT)
        return

    if player.has_acted:
        await query.answer(s.ALREADY_ACTED, show_alert=True)
        return

    game.record_mafia_vote(user_id, target_id)
    await query.edit_message_text(s.NIGHT_ACTION_RECORDED)

    if game.all_night_actions_done():
        asyncio.create_task(_resolve_and_day(game, ctx.application))


async def cb_night_doctor(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.split(":")[1])

    game = _find_game_by_player(user_id)
    if not game or game.state != "night":
        await query.edit_message_text(s.GAME_NOT_IN_NIGHT)
        return

    player = game.players.get(user_id)
    if not player or not player.alive:
        await query.edit_message_text(s.PLAYER_DEAD_CANNOT_ACT)
        return

    if player.has_acted:
        await query.answer(s.ALREADY_ACTED, show_alert=True)
        return

    game.record_doctor_action(user_id, target_id)
    await query.edit_message_text(s.NIGHT_ACTION_RECORDED)

    if game.all_night_actions_done():
        asyncio.create_task(_resolve_and_day(game, ctx.application))


async def cb_night_sheriff(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.split(":")[1])

    game = _find_game_by_player(user_id)
    if not game or game.state != "night":
        await query.edit_message_text(s.GAME_NOT_IN_NIGHT)
        return

    player = game.players.get(user_id)
    if not player or not player.alive:
        await query.edit_message_text(s.PLAYER_DEAD_CANNOT_ACT)
        return

    if player.has_acted:
        await query.answer(s.ALREADY_ACTED, show_alert=True)
        return

    success = game.record_sheriff_action(user_id, target_id)
    if not success:
        await query.answer(s.ALREADY_ACTED, show_alert=True)
        return

    target_name = game.players[target_id].name
    if game.sheriff_result == "mafia":
        result_text = s.SHERIFF_RESULT_MAFIA.format(name=target_name)
    else:
        result_text = s.SHERIFF_RESULT_CLEAN.format(name=target_name)

    await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)

    if game.all_night_actions_done():
        asyncio.create_task(_resolve_and_day(game, ctx.application))


async def cb_vote(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    raw = query.data.split(":")[1]
    target_id = None if raw == "skip" else int(raw)

    game = _find_game_by_player(user_id)
    if not game or game.state != "vote":
        await query.edit_message_text(s.GAME_NOT_IN_VOTE)
        return

    player = game.players.get(user_id)
    if not player or not player.alive:
        await query.edit_message_text(s.PLAYER_DEAD_CANNOT_ACT)
        return

    if player.has_acted:
        await query.answer(s.ALREADY_VOTED, show_alert=True)
        return

    game.record_vote(user_id, target_id)
    await query.edit_message_text(s.VOTE_RECORDED)

    if game.all_voted():
        asyncio.create_task(_resolve_vote(game, ctx.application))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    app = Application.builder().token(config.TOKEN).build()

    app.add_handler(CommandHandler("newgame", cmd_newgame))
    app.add_handler(CommandHandler("join", cmd_join))
    app.add_handler(CommandHandler("startgame", cmd_startgame))
    app.add_handler(CommandHandler("cancel", cmd_cancel))

    app.add_handler(CallbackQueryHandler(cb_night_mafia,  pattern=r"^night_mafia:"))
    app.add_handler(CallbackQueryHandler(cb_night_doctor, pattern=r"^night_doctor:"))
    app.add_handler(CallbackQueryHandler(cb_night_sheriff,pattern=r"^night_sheriff:"))
    app.add_handler(CallbackQueryHandler(cb_vote,         pattern=r"^vote:"))

    print("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
