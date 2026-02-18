# Discord Bot для масової видачі ролі

Цей бот дозволяє видати певну роль **усім учасникам сервера**, у яких її немає. Команда `!massrole` запускає процес із затримкою 1 секунда між учасниками, щоб уникнути блокування Discord. Усі дії логуються у файл `role_log.txt`.

## Вимоги

- Python 3.8 або вище
- Бібліотеки: `discord.py`, `python-dotenv`

## Налаштування бота на Discord Developer Portal

1. Перейдіть на [Discord Developer Portal](https://discord.com/developers/applications) і створіть нового бота (або використайте існуючого).
2. У розділі **Bot**:
   - Скиньте та скопіюйте **токен** – він знадобиться для файлу `.env`.
   - Увімкніть **Privileged Gateway Intents**:
     - `SERVER MEMBERS INTENT` – обов’язково, щоб бот бачив усіх учасників.
     - `MESSAGE CONTENT INTENT` – щоб бот читав команди.
3. У розділі **OAuth2 > URL Generator**:
   - Виберіть `bot` та `applications.commands`.
   - У правах бота оберіть:
     - `Manage Roles` (керування ролями)
     - `Read Messages/View Channels`
     - `Send Messages`
   - За згенерованим посиланням додайте бота на свій сервер.

## Встановлення та запуск

1. **Завантажте файли бота** – `bot.py`, `config.py` та (опціонально) цей `README.md`.
2. **Встановіть залежності**:
   ```bash
   pip install discord.py python-dotenv
