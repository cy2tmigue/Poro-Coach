import discord
from discord.ext import commands
from scrapers.champion_single import SingleChampionScraper


class ChampionInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scraper = SingleChampionScraper()

    @commands.command(name="champinfo")
    async def champinfo(self, ctx, *, champion_name: str):
        embed = discord.Embed(
            title="⏳ Buscando información...",
            description=f"Consultando datos de **{champion_name}**...",
            color=discord.Color.yellow()
        )
        msg = await ctx.send(embed=embed)

        data = self.scraper.get_champion(champion_name)

        if not data:
            return await msg.edit(embed=discord.Embed(
                title="❌ Error",
                description=f"No pude obtener datos de **{champion_name}**.",
                color=discord.Color.red()
            ))

        stats = data["stats"]

        embed = discord.Embed(
            title=f"📘 Stats de {data['name']}",
            url=data["url"],
            color=discord.Color.blue()
        )

        embed.add_field(name="❤️ Vida Base", value=stats["hp"], inline=True)
        embed.add_field(name="❤️ Vida por Nivel", value=stats["hp_plus"], inline=True)
        embed.add_field(name="🔵 Maná Base", value=stats["mp"], inline=True)
        embed.add_field(name="🔵 Maná por Nivel", value=stats["mp_plus"], inline=True)

        embed.add_field(name="🛡 Armadura", value=stats["armor"], inline=True)
        embed.add_field(name="🛡 Armadura por Nivel", value=stats["armor_plus"], inline=True)

        embed.add_field(name="⚔️ Daño de Ataque", value=stats["ad"], inline=True)
        embed.add_field(name="⚔️ DA por Nivel", value=stats["ad_plus"], inline=True)

        embed.add_field(name="🥷 Velocidad de Ataque", value=stats["as"], inline=True)
        embed.add_field(name="🏃 Velocidad de Movimiento", value=stats["movespeed"], inline=True)

        await msg.edit(embed=embed)

    def cog_unload(self):
        """Cerrar el navegador cuando se descargue el cog"""
        self.scraper.close()


async def setup(bot):
    await bot.add_cog(ChampionInfo(bot))
