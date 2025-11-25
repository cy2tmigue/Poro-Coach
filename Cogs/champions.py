import discord
from discord.ext import commands
from scrapers.champion_scraper import load_champions

class ChampionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="champions", help="Muestra una lista con los campeones scrapeados.")
    async def champions(self, ctx):
        await ctx.send("⏳ Scrapeando información de campeones... Esto puede tardar 10–20 segundos.")

        champions = load_champions()

        if not champions:
            return await ctx.send("❌ No se pudo obtener información de los campeones.")

        # Crear un mensaje resumido
        lines = []
        for c in champions:
            lines.append(
                f"**{c['name'].title()}** — {c['category']} | "
                f"Range: {c['attackRange']} | "
                f"MS: {c['movementSpeed']} | "
                f"Style: {c['style']} | "
                f"Difficulty: {c['difficulty']}"
            )

        text = "\n".join(lines)

        # Discord no permite mensajes de más de 2000 caracteres → dividir mensaje si es necesario
        if len(text) <= 2000:
            await ctx.send(text)
        else:
            for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
                await ctx.send(chunk)

async def setup(bot):
    await bot.add_cog(ChampionsCog(bot))
