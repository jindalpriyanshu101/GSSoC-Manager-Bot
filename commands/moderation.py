import discord
import os
import random

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    # Ban command - slash command
    @tree.command(
        name="ban", 
        description="Command to ban a user.", 
        guild=discord.Object(id=guild_id)
    )
    async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        # Check permissions
        if interaction.user.id not in admin_ids:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=False)
            return
        
        # Ban action
        await interaction.response.send_message(f"{user.mention} has been banned for reason: {reason}", ephemeral=False)
    
    # Kick command - slash command
    @tree.command(
        name="kick", 
        description="Command to kick a user.", 
        guild=discord.Object(id=guild_id)
    )
    async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        # Check permissions
        if interaction.user.id not in admin_ids:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=False)
            return
        
        # Kick action
        await interaction.response.send_message(f"{user.mention} has been kicked for reason: {reason}", ephemeral=False)
    
    # Hide command - prefix command
    @bot.command(name="hide", description="Hide a channel from the server.")
    async def hide(ctx, channel: discord.TextChannel = None):
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                await ctx.reply("Please provide the channel to hide.", delete_after=5)
                return

            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await ctx.send(f"Channel {channel.mention} has been hidden.")
        else:
            if ctx.author.id in homies:
                await ctx.reply(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.reply("You do not have permission to use this command.", delete_after=5)
    
    # Unhide command - prefix command
    @bot.command(name="unhide", description="Unhide a channel from the server.")
    async def unhide(ctx, channel: discord.TextChannel = None):
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                await ctx.reply("Please provide the channel to unhide.", delete_after=5)
                return

            await channel.set_permissions(ctx.guild.default_role, read_messages=True)
            await ctx.send(f"Channel {channel.mention} has been unhidden.")
        else:
            if ctx.author.id in homies:
                await ctx.reply(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.reply("You do not have permission to use this command.", delete_after=5)
    
    # Lock command - prefix command
    @bot.command(name="lock", description="Lock a channel.")
    async def lock(ctx, channel: discord.TextChannel = None):
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                await ctx.reply("Please provide the channel to lock.", delete_after=5)
                return

            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"Channel {channel.mention} has been locked.")
        else:
            if ctx.author.id in homies:
                await ctx.reply(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.reply("You do not have permission to use this command.", delete_after=5)
    
    # Unlock command - prefix command
    @bot.command(name="unlock", description="Unlock a channel.")
    async def unlock(ctx, channel: discord.TextChannel = None):
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                await ctx.reply("Please provide the channel to unlock.", delete_after=5)
                return

            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f"Channel {channel.mention} has been unlocked.")
        else:
            if ctx.author.id in homies:
                await ctx.reply(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.reply("You do not have permission to use this command.", delete_after=5)
    
    # Clear command - prefix command
    @bot.command(name="clear", description="Clear a specified number of messages from a channel.")
    async def clear(ctx, amount: int = None):
        if ctx.author.guild_permissions.manage_messages or ctx.author.id in admin_ids:
            try:
                if amount is None or amount <= 0:
                    await ctx.send("Please specify a valid amount to clear.")
                    return

                deleted = await ctx.channel.purge(limit=amount)
                await ctx.send(f"🧹 Cleared {len(deleted)} messages.", delete_after=2)
            except discord.errors.Forbidden:
                await ctx.reply("I do not have permission to manage messages in this channel.", delete_after=5)
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            if ctx.author.id in homies:
                await ctx.reply(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.reply("You do not have permission to use this command.", delete_after=5) 