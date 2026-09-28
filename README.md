# Telegram Reminder Bot — бот-напоминалка

Telegram-бот на Python (`aiogram`), который принимает напоминания вида
«через 5 минут / завтра в 9:00» и вовремя присылает сообщение.

## Как запустить

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Получи токен бота у [@BotFather](https://t.me/BotFather):
   `/newbot` → скопируй токен.

3. Задай токен и (по желанию) разрешённые chat-id:

```bash
export TG_TOKEN="ваш_токен"          # Windows: set TG_TOKEN=...
export TG_ALLOWED=""                 # пусто = доступен всем
python bot.py
```

Бот запускается через `python bot.py` и ждёт сообщений.

## Команды

- `/start` — приветствие
- `/remind 5 мин купить молоко` — напомнить через 5 минут
- `/remind завтра в 9:00 встреча` — в конкретное время
- `/list` — список активных напоминаний
- `/cancel N` — удалить напоминание N

## Форматы времени в `/remind`

```
/remind 10 мин позвонить
/remind 2 часа сделать отчёт
/remind завтра в 10:30 тренировка
/remind в 18:00 выпить воды
```

## Файлы

- `bot.py` — код бота
- `requirements.txt` — `aiogram`
- `.env.example` — шаблон для токена (если используешь `python-dotenv`)