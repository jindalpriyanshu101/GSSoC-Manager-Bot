import discord
from datetime import datetime
import os
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @bot.hybrid_command(
        name="about", 
        description="Shows information about the bot and the developer."
    )
    @commands.guild_only()
    async def about(ctx):
        GSSOC_LOGO = "https://images-ext-1.discordapp.net/external/uhOfjzdx2Ybeh7T8RqVFgvs4ryRucs3_7sT51GNfgNQ/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1288156277351907389/94edf9346498881ddbc981cb9b82fe52.webp"
        
        embed = discord.Embed(
            title="About GSSoC Manager",
            description="Welcome to the GirlScript Summer Of Code! 🤖\nThis bot helps streamlining the verification process and managing user roles, name for the GSSoC community while obeying the guidlines.",
            color=0xed8540,
            timestamp=datetime.now()
        )
        
        embed.set_author(name="GSSoC Manager", icon_url=GSSOC_LOGO)
        embed.set_thumbnail(url=GSSOC_LOGO)

        embed.add_field(name="Features", value="✨ Role assignment\n✨ Verification system\n✨ Welcome messages\n✨ Logging and more!", inline=False)
        embed.add_field(name="Developers", value="<a:priyanshu:1289324955410108510> [jindalpriyanshu101](https://github.com/jindalpriyanshu101)", inline=False)
        embed.add_field(name="Support", value="If you have any issues or questions, feel free to reach out to the developer or the support team.", inline=False)

        embed.set_footer(text="GSSoC Manager!", icon_url=GSSOC_LOGO)

        await ctx.send(embed=embed) 