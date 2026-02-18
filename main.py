import discord
from discord.ext import commands
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
import config

load_dotenv()

logging.basicConfig(
    filename='role_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Start {bot.user}')
    print('Доступні команди:')
    for cmd in bot.commands:
        print(f'   • {cmd.name}')

def has_allowed_role_or_admin(ctx):
    if ctx.author.guild_permissions.administrator:
        return True
    if config.ALLOWED_ROLE_IDS:
        user_role_ids = [role.id for role in ctx.author.roles]
        if any(role_id in user_role_ids for role_id in config.ALLOWED_ROLE_IDS):
            return True
    return False

@bot.command(name='massrole')
async def massrole(ctx):
    if not has_allowed_role_or_admin(ctx):
        await ctx.send("У вас немає прав для використання цієї команди.")
        return

    guild = ctx.guild
    role = guild.get_role(config.TARGET_ROLE_ID)

    if role is None:
        await ctx.send("Роль із таким ID не знайдено на цьому сервері. Перевірте config.py.")
        return

    if role >= guild.me.top_role:
        await ctx.send("Не можу видати цю роль: вона вища або дорівнює моїй найвищій ролі.")
        return

    try:
        status_msg = await ctx.send("Починаю масову видачу ролі...")
    except Exception as e:
        logging.error(f"Не вдалося надіслати початкове повідомлення: {e}")
        return

    await asyncio.sleep(1)

    given = 0
    already_have = 0
    failed = 0
    errors = []

    try:
        for member in guild.members:
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason="Масова видача ролі за командою")
                    given += 1
                    logging.info(f"Додано роль {member.name} (ID: {member.id})")
                except discord.Forbidden:
                    failed += 1
                    msg = f"Немає прав для додавання ролі {member.name} (ID: {member.id})"
                    logging.error(msg)
                    errors.append(msg)
                except discord.HTTPException as e:
                    failed += 1
                    msg = f"Помилка HTTP для {member.name} (ID: {member.id}): {e}"
                    logging.error(msg)
                    errors.append(msg)
            else:
                already_have += 1
                logging.info(f"Роль вже є у {member.name} (ID: {member.id}) - пропущено")

            await asyncio.sleep(1)

    except Exception as e:
        error_msg = f"Критична помилка під час виконання: {e}"
        logging.error(error_msg)
        errors.append(error_msg)
    finally:
        summary_lines = [
            "**Готово!**",
            f"Видано роль: {given}",
            f"⏭Вже мали роль: {already_have}",
            f"Помилок: {failed}"
        ]
        if errors:
            summary_lines.append("\n**Деталі помилок:**")
            for err in errors[:5]:
                summary_lines.append(f"• {err}")
        summary = "\n".join(summary_lines)

        try:
            await status_msg.edit(content=summary)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            try:
                await ctx.send(summary)
            except Exception as e:
                logging.error(f"Не вдалося надіслати звіт: {e}")
        finally:
            logging.info(f"Підсумок: видано {given}, вже мали {already_have}, помилок {failed}")

@massrole.error
async def massrole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Ви не маєте права для використання цієї команди.")
    else:
        await ctx.send(f"Помилка: {error}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Такої команди не існує. Спробуй `!massrole`.")
    else:
        await ctx.send(f"Сталася помилка: {error}")

# старт
token = os.getenv('BOT_TOKEN')
if not token:
    print("Токен не знайдено! Переконайся, що у файлі .env є BOT_TOKEN=ваш_токен")
    sys.exit(1)

bot.run(token)