import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Crear bot
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None  # Desactiva el help default
)

# Cargar cogs dinámicamente desde /Cogs
async def load_cogs():
    print("\n=== CARGANDO COGS ===")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(name)
                print(f"✅ Cargado: {name}")
            except Exception as e:
                print(f"❌ Error cargando {name}: {e}")
    print("=== FIN DE CARGA ===\n")

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Main asincrónico
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
