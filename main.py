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
    filename="role_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Бот запущено як {bot.user}")
    print("Команди:")
    for cmd in bot.commands:
        print(f" - {cmd.name}")


def can_use_massrole(ctx):
    if ctx.author.guild_permissions.administrator:
        return True

    allowed_roles = set(config.ALLOWED_ROLE_IDS or [])
    user_roles = {role.id for role in ctx.author.roles}

    return bool(allowed_roles & user_roles)


@bot.command()
async def massrole(ctx):
    if not can_use_massrole(ctx):
        await ctx.send("У тебе немає прав на цю команду.")
        return

    guild = ctx.guild
    role = guild.get_role(config.TARGET_ROLE_ID)

    if not role:
        await ctx.send("Роль не знайдена. Перевір TARGET_ROLE_ID.")
        return

    if role >= guild.me.top_role:
        await ctx.send("Я не можу видати роль, що вища за мою.")
        return

    msg = await ctx.send("Починаю видачу ролі...")

    given = 0
    skipped = 0
    errors = 0

    for member in guild.members:
        if role in member.roles:
            skipped += 1
            continue

        try:
            await member.add_roles(role, reason="Масова видача ролі")
            given += 1
            logging.info(f"Роль видано: {member} ({member.id})")
        except discord.Forbidden:
            errors += 1
            logging.warning(f"Немає прав для {member} ({member.id})")
        except discord.HTTPException as e:
            errors += 1
            logging.error(f"HTTP помилка для {member} ({member.id}): {e}")

        await asyncio.sleep(0.5)  # анти-рейтліміт

    result = (
        "**Готово!**\n"
        f"Видано: {given}\n"
        f"Пропущено: {skipped}\n"
        f"Помилки: {errors}"
    )

    await msg.edit(content=result)
    logging.info(f"Завершено: +{given}, skip {skipped}, errors {errors}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Помилка: {error}")


token = os.getenv("BOT_TOKEN")
if not token:
    print("BOT_TOKEN не знайдено в .env")
    sys.exit(1)

bot.run(token)
