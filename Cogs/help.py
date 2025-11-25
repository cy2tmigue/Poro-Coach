from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📘 Lista de Comandos — Poro-Coach",
            description="Aquí tienes todos los comandos del bot, organizados por categoría.",
            color=discord.Color.purple()
        )

        # 🌟 GENERAL
        embed.add_field(
            name="🌟 General",
            value=(
                "`!info` — Información del bot"
            ),
            inline=False
        )

        # 🧰 UTILIDAD
        embed.add_field(
            name="🧰 Utilidad",
            value=(
                "`!avatar @user` — Muestra el avatar de un usuario\n"
                "`!userinfo @user` — Datos de un usuario\n"
                "`!serverinfo` — Información del servidor"
            ),
            inline=False
        )

        # 🎮 LEAGUE OF LEGENDS
        embed.add_field(
            name="🎮 League of Legends",
            value=(
                "`!champinfo <campeón>` — Muestra estadísticas del campeón\n"
                "`!build <campeón>` — Build recomendada (ítems, runas y hechizos)"
            ),
            inline=False
        )

        # 🛠 ADMINISTRACIÓN
        embed.add_field(
            name="🛠 Administración",
            value="`!clear <n>` — Borra n mensajes (requiere permisos)",
            inline=False
        )

        embed.set_footer(text="Poro-Coach | Proyecto académico de Miguel y Juan Pablo")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
