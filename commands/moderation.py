import discord
import os
import random
from datetime import timedelta
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    # Ban command - hybrid command
    @bot.hybrid_command(
        name="ban", 
        description="Command to ban a user from the server"
    )
    @commands.guild_only()
    async def ban(ctx, user: discord.Member, *, reason: str = commands.parameter(description="Reason for the ban", default="No reason provided")):
        """Ban a user from the server
        
        Parameters
        ----------
        user: The user to ban
        reason: The reason for the ban
        
        Examples
        --------
        !ban @User Breaking server rules
        !ban @User Spamming in chat
        """
        # Check permissions
        if ctx.author.id not in admin_ids and not ctx.author.guild_permissions.ban_members:
            await ctx.send("You do not have permission to use this command.")
            return
        
        # Ban action
        try:
            await user.ban(reason=f"Banned by {ctx.author.name}: {reason}")
            await ctx.send(f"{user.mention} has been banned for reason: {reason}")
            
            # Log the ban action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="User Banned",
                        description=f"{user.mention} has been banned",
                        color=discord.Color.red(),
                        timestamp=ctx.message.created_at if hasattr(ctx, 'message') else discord.utils.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=True)
                    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                    embed.set_footer(text=f"ID: {user.id}")
                    
                    await log_channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    
    # Kick command - hybrid command
    @bot.hybrid_command(
        name="kick", 
        description="Command to kick a user from the server"
    )
    @commands.guild_only()
    async def kick(ctx, user: discord.Member, *, reason: str = commands.parameter(description="Reason for the kick", default="No reason provided")):
        """Kick a user from the server
        
        Parameters
        ----------
        user: The user to kick
        reason: The reason for the kick
        
        Examples
        --------
        !kick @User Breaking server rules
        !kick @User Spamming in chat
        """
        # Check permissions
        if ctx.author.id not in admin_ids and not ctx.author.guild_permissions.kick_members:
            await ctx.send("You do not have permission to use this command.")
            return
        
        # Kick action
        try:
            await user.kick(reason=f"Kicked by {ctx.author.name}: {reason}")
            await ctx.send(f"{user.mention} has been kicked for reason: {reason}")
            
            # Log the kick action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="User Kicked",
                        description=f"{user.mention} has been kicked",
                        color=discord.Color.orange(),
                        timestamp=ctx.message.created_at if hasattr(ctx, 'message') else discord.utils.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=True)
                    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                    embed.set_footer(text=f"ID: {user.id}")
                    
                    await log_channel.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    
    # Hide command - hybrid command
    @bot.hybrid_command(
        name="hide", 
        description="Hide a channel from the server"
    )
    @commands.guild_only()
    async def hide(ctx, channel: discord.TextChannel = commands.parameter(description="The channel to hide", default=None)):
        
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                channel = ctx.channel
                
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            await ctx.send(f"Channel {channel.mention} has been hidden.")
        else:
            if ctx.author.id in homies:
                await ctx.send(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.send("You do not have permission to use this command.", delete_after=5)
    
    # Unhide command - hybrid command
    @bot.hybrid_command(
        name="unhide", 
        description="Unhide a channel from the server"
    )
    @commands.guild_only()
    async def unhide(ctx, channel: discord.TextChannel = commands.parameter(description="The channel to unhide", default=None)):
        
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                channel = ctx.channel
                
            await channel.set_permissions(ctx.guild.default_role, read_messages=True)
            await ctx.send(f"Channel {channel.mention} has been unhidden.")
        else:
            if ctx.author.id in homies:
                await ctx.send(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.send("You do not have permission to use this command.", delete_after=5)
    
    # Lock command - hybrid command
    @bot.hybrid_command(
        name="lock", 
        description="Lock a channel to prevent new messages"
    )
    @commands.guild_only()
    async def lock(ctx, channel: discord.TextChannel = commands.parameter(description="The channel to lock", default=None)):
        
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                channel = ctx.channel
                
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"Channel {channel.mention} has been locked.")
        else:
            if ctx.author.id in homies:
                await ctx.send(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.send("You do not have permission to use this command.", delete_after=5)
    
    # Unlock command - hybrid command
    @bot.hybrid_command(
        name="unlock", 
        description="Unlock a channel to allow messages again"
    )
    @commands.guild_only()
    async def unlock(ctx, channel: discord.TextChannel = commands.parameter(description="The channel to unlock", default=None)):
        
        if ctx.author.guild_permissions.manage_channels or ctx.author.id in admin_ids:
            if not channel:
                channel = ctx.channel
                
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f"Channel {channel.mention} has been unlocked.")
        else:
            if ctx.author.id in homies:
                await ctx.send(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.send("You do not have permission to use this command.", delete_after=5)
    
    # Clear command - hybrid command
    @bot.hybrid_command(
        name="clear", 
        description="Clear a specified number of messages from a channel"
    )
    @commands.guild_only()
    async def clear(ctx, amount: int = commands.parameter(description="Number of messages to delete")):
        
        if ctx.author.guild_permissions.manage_messages or ctx.author.id in admin_ids:
            try:
                if amount is None or amount <= 0:
                    await ctx.send("Please specify a valid amount to clear.")
                    return
                elif amount > 100:
                    await ctx.send("You can only delete up to 100 messages at once.")
                    return

                deleted = await ctx.channel.purge(limit=amount)
                await ctx.send(f"🧹 Cleared {len(deleted)} messages.", delete_after=2)
            except discord.errors.Forbidden:
                await ctx.send("I do not have permission to manage messages in this channel.", delete_after=5)
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            if ctx.author.id in homies:
                await ctx.send(f"{random.choice(bot_data['constants']['APSHABD'])}", delete_after=5)
            else:
                await ctx.send("You do not have permission to use this command.", delete_after=5)
    
    # Unban command - hybrid command
    @bot.hybrid_command(
        name="unban", 
        description="Unban a user from the server"
    )
    @commands.guild_only()
    async def unban(ctx, user_id: int = commands.parameter(description="The ID of the user to unban")):
        
        # Check permissions
        if ctx.author.id not in admin_ids and not ctx.author.guild_permissions.ban_members:
            await ctx.send("You do not have permission to use this command.")
            return
        
        # Unban action
        try:
            await ctx.guild.unban(discord.Object(id=user_id))
            await ctx.send(f"User with ID {user_id} has been unbanned.")
            
            # Log the unban action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="User Unbanned",
                        description=f"User with ID {user_id} has been unbanned",
                        color=discord.Color.green(),
                        timestamp=ctx.message.created_at if hasattr(ctx, 'message') else discord.utils.utcnow()
                    )
                    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                    
                    await log_channel.send(embed=embed)
        except discord.NotFound:
            await ctx.send(f"User with ID {user_id} was not found in the ban list.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unban users.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}") 