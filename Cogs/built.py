import discord
from discord.ext import commands
import json
import os
import aiohttp
from PIL import Image
from io import BytesIO

CDN_VERSION = "15.23.1"


class BuildReader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db_porocoach.json"
        self.items_db_path = "items.json"

        with open(self.items_db_path, "r", encoding="utf-8") as f:
            self.items_data = json.load(f)["data"]

    # ----------------------------------------------------------------
    # 🔍 OBTENER URL DE IMAGEN DEL ÍTEM
    # ----------------------------------------------------------------
    def get_item_img_url(self, item_name: str):
        for item_id, info in self.items_data.items():
            if info["name"].lower() == item_name.lower():
                filename = info["image"]["full"]
                return f"https://ddragon.leagueoflegends.com/cdn/{CDN_VERSION}/img/item/{filename}"
        return None

    # ----------------------------------------------------------------
    # 🖼️ UNE TODAS LAS IMÁGENES EN UNA SOLA FILA (64x64 c/u)
    # ----------------------------------------------------------------
    async def build_items_image(self, image_urls: list):
        if not image_urls:
            return None

        images = []

        async with aiohttp.ClientSession() as session:
            for url in image_urls:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            img_bytes = await resp.read()
                            img = Image.open(BytesIO(img_bytes)).convert("RGBA")

                            # 🔥 normalizar tamaño para que no se corten
                            img = img.resize((64, 64))
                            images.append(img)
                except:
                    pass

        if not images:
            return None

        # tamaño final
        width = 64 * len(images)
        final_img = Image.new("RGBA", (width, 64))

        x_offset = 0
        for img in images:
            final_img.paste(img, (x_offset, 0))
            x_offset += 64

        output = BytesIO()
        final_img.save(output, "PNG")
        output.seek(0)
        return output

    # ----------------------------------------------------------------
    # 📌 COMANDO !build
    # ----------------------------------------------------------------
    @commands.command()
    async def build(self, ctx, *, champion: str):

        champion_normalized = champion.replace(" ", "").lower()

        if not os.path.exists(self.db_path):
            return await ctx.send("❌ No encontré el archivo de builds.")

        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        champ_key = None
        for key in data.keys():
            if key.replace(" ", "").lower() == champion_normalized:
                champ_key = key
                break

        if champ_key is None:
            return await ctx.send("😿 Ese campeón no existe en la base de datos.")

        champ_data = data[champ_key]

        embed = discord.Embed(
            title=f"Build recomendada para {champ_key}",
            color=discord.Color.purple()
        )

          # ----------------------------------------------------------------
        # 🛡 ÍTEMS
        # ----------------------------------------------------------------
        items = champ_data.get("items", [])

        final_img = None  # <- PREPARAMOS LA VARIABLE DE IMAGEN

        if items:
            embed.add_field(
                name="🛡 Items recomendados",
                value="\n".join([f"- {i}" for i in items]),
                inline=False
            )

            # URLs de imágenes
            urls = []
            for item_name in items:
                url = self.get_item_img_url(item_name)
                if url:
                    urls.append(url)

            # Construir la imagen final
            final_img = await self.build_items_image(urls)

            # Si se genera imagen, la ponemos pero NO enviamos aún
            if final_img:
                file = discord.File(final_img, filename="items.png")
                embed.set_image(url="attachment://items.png")

        # ----------------------------------------------------------------
        # 🔮 RUNAS
        # ----------------------------------------------------------------
        runes = champ_data.get("runes")
        if runes:

            primary = runes.get("primary")
            if primary:
                embed.add_field(
                    name=f"🔮 Runas Primarias ({primary.get('tree')})",
                    value=f"**Keystone:** {primary.get('keystone')}\n"
                    + "\n".join([f"- {r}" for r in primary.get("runes", [])]),
                    inline=False
                )

            secondary = runes.get("secondary")
            if secondary:
                embed.add_field(
                    name=f"✨ Runas Secundarias ({secondary.get('tree')})",
                    value="\n".join([f"- {r}" for r in secondary.get('runes', [])]),
                    inline=False
                )

            shards = runes.get("statShards", [])
            if shards:
                embed.add_field(
                    name="📊 Fragmentos (Stat Shards)",
                    value="\n".join([f"- {s}" for s in shards]),
                    inline=False
                )

        # ----------------------------------------------------------------
        # ✨ SUMMONER SPELLS
        # ----------------------------------------------------------------
        summoners = champ_data.get("summoners", [])
        if summoners:
            embed.add_field(
                name="✨ Hechizos de Invocador",
                value="\n".join([f"- {s}" for s in summoners]),
                inline=False
            )

        # ----------------------------------------------------------------
        # 📤 ENVIAR TODO EN UN SOLO MENSAJE
        # ----------------------------------------------------------------
        if final_img:
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BuildReader(bot))
