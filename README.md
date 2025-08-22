# Telegram Admin Caller Bot

Бот для быстрого вызова всех администраторов в чате.

## Команды
- `/call` — тегает всех админов
- `/setup` — отправляет кнопку для вызова админов

## Деплой на Render
1. Создай новый Web Service.
2. Укажи `pip install -r requirements.txt` как Build Command.
3. Укажи `python bot.py` как Start Command.
4. В Environment добавь:
   - `TELEGRAM_BOT_TOKEN` — токен из BotFather
   - `COOLDOWN_SECONDS` — пауза между вызовами (по умолчанию 30)

После деплоя бот работает 24/7 🚀
