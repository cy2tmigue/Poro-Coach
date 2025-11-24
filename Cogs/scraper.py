import discord
from discord.ext import commands
import json
import os

class BuildReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db_porocoach.json"  # Archivo JSON local

    @commands.command()
    async def build(self, ctx, *, champion: str):
        """Devuelve la build de un campeón desde la base de datos JSON."""

        # Normalizar entrada
        champion_normalized = champion.replace(" ", "").lower()

        # --- Verificar existencia del JSON ---
        if not os.path.exists(self.db_path):
            return await ctx.send("❌ No encontré el archivo db_porocoach.json.")

        # --- Leer JSON ---
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return await ctx.send(f"⚠️ Error al leer el archivo JSON: {e}")

        # --- Buscar campeón ignorando mayúsculas ---
        champ_key = None
        for key in data.keys():
            if key.replace(" ", "").lower() == champion_normalized:
                champ_key = key
                break

        if champ_key is None:
            return await ctx.send("😿 Ese campeón no existe en la base de datos.")

        champ_data = data[champ_key]

        # --------------- EMBED ---------------

        embed = discord.Embed(
            title=f"Build recomendada para {champ_key}",
            color=discord.Color.purple()
        )

        # 🛡 Items
        items = champ_data.get("items", [])
        if items:
            embed.add_field(
                name="🛡 Items recomendados",
                value="\n".join([f"- {item}" for item in items]),
                inline=False
            )

        # 🔮 Runas
        runes = champ_data.get("runes")
        if runes:

            # Runa primaria
            primary = runes.get("primary")
            if primary:
                embed.add_field(
                    name=f"🔮 Runas Primarias ({primary.get('tree')})",
                    value=f"**Keystone:** {primary.get('keystone')}\n" +
                          "\n".join([f"- {r}" for r in primary.get("runes", [])]),
                    inline=False
                )

            # Runa secundaria
            secondary = runes.get("secondary")
            if secondary:
                embed.add_field(
                    name=f"✨ Runas Secundarias ({secondary.get('tree')})",
                    value="\n".join([f"- {r}" for r in secondary.get("runes", [])]),
                    inline=False
                )

            # Shards
            shards = runes.get("statShards", [])
            if shards:
                embed.add_field(
                    name="📊 Fragmentos (Stat Shards)",
                    value="\n".join([f"- {s}" for s in shards]),
                    inline=False
                )

        # ✨ Summoner Spells
        summoners = champ_data.get("summoners", [])
        if summoners:
            embed.add_field(
                name="✨ Hechizos de Invocador",
                value="\n".join([f"- {s}" for s in summoners]),
                inline=False
            )

        # Enviar embed
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BuildReader(bot))
