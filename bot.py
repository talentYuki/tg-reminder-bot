#!/usr/bin/env python3
"""Telegram Reminder Bot на aiogram 3.

Запуск:
    pip install -r requirements.txt
    set TG_TOKEN=ваш_токен   (Windows)  |  export TG_TOKEN=...  (Linux/mac)
    python bot.py
"""

import asyncio
import datetime as dt
import os
import re

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("TG_TOKEN")
if not TOKEN:
    raise SystemExit("Задай TG_TOKEN (токен бота от @BotFather).")

router = Router()

# напоминания: список dict {chat_id, text, when}
reminders = []
counter = 0


def parse_relative(text: str) -> dt.datetime | None:
    m = re.match(r"\s*(\d+)\s+(мин|минут|час|часа|часов|час\b)", text)
    if not m:
        return None
    num = int(m.group(1))
    unit = m.group(2)
    now = dt.datetime.now()
    if unit.startswith("мин"):
        return now + dt.timedelta(minutes=num)
    return now + dt.timedelta(hours=num)


def parse_absolute(text: str) -> dt.datetime | None:
    # "в 18:00"
    m = re.search(r"\bв\s+(\d{1,2}):(\d{2})\b", text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        now = dt.datetime.now()
        when = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        if when <= now:
            when += dt.timedelta(days=1)
        return when
    # "завтра в 9:00"
    m = re.search(r"завтра\s+в\s+(\d{1,2}):(\d{2})\b", text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        now = dt.datetime.now()
        return (now + dt.timedelta(days=1)).replace(hour=h, minute=mi, second=0)
    return None


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Я бот-напоминалка.\n"
                     "Примеры:\n"
                     "/remind 5 мин купить молоко\n"
                     "/remind в 18:00 выпить воды\n"
                     "/remind завтра в 9:00 встреча\n"
                     "/list — список напоминаний\n"
                     "/cancel 1 — удалить первое")


@router.message(Command("remind"))
async def remind(msg: Message):
    global counter
    text = msg.text[len("/remind"):].strip()
    if not text:
        await msg.answer("Использование: /remind <когда> <что>\n"
                         "напр.: /remind 10 мин позвонить")
        return
    when = parse_relative(text) or parse_absolute(text)
    if when is None:
        await msg.answer("Не понял время. Примеры:\n"
                         "10 мин / 2 часа / в 18:00 / завтра в 9:00")
        return
    # уберём "когда" из текста для самого напоминания
    task = re.sub(r"^\s*\d+\s+(мин|минут|час|часов|часа)\s+", "", text)
    task = re.sub(r"^\s*в\s+\d{1,2}:\d{2}\s*", "", task)
    task = re.sub(r"^\s*завтра\s+в\s+\d{1,2}:\d{2}\s*", "", task)
    counter += 1
    reminders.append({"chat": msg.chat.id, "text": task or text,
                      "when": when, "id": counter})
    await msg.answer(f"Ок, напомню: «{task or text}»\nв {when:%H:%M %d.%m}")


@router.message(Command("list"))
async def list_reminders(msg: Message):
    mine = [r for r in reminders if r["chat"] == msg.chat.id]
    if not mine:
        await msg.answer("Активных напоминаний нет.")
        return
    lines = [f"{r['id']}. {r['text']} — {r['when']:%H:%M %d.%m}" for r in mine]
    await msg.answer("\n".join(lines))


@router.message(Command("cancel"))
async def cancel(msg: Message):
    try:
        rid = int(msg.text.split()[1])
    except (IndexError, ValueError):
        await msg.answer("Использование: /cancel <номер>")
        return
    global reminders
    before = len(reminders)
    reminders = [r for r in reminders
                 if not (r["id"] == rid and r["chat"] == msg.chat.id)]
    await msg.answer("Удалено." if len(reminders) < before else "Не нашёл.")


async def scheduler(bot: Bot):
    global reminders
    while True:
        now = dt.datetime.now()
        due = [r for r in reminders if r["when"] <= now]
        for r in due:
            try:
                await bot.send_message(r["chat"], "⏰ " + r["text"])
            except Exception:
                pass
        if due:
            ids = {d["id"] for d in due}
            reminders = [r for r in reminders if r["id"] not in ids]
        await asyncio.sleep(1)


async def main():
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(lambda: asyncio.create_task(scheduler(bot)))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())