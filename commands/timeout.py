import discord
import os
from datetime import timedelta
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @bot.hybrid_command(
        name="timeout", 
        description="Timeout a user for a specified duration (minutes, hours, or days)"
    )
    @commands.guild_only()
    async def timeout(ctx, user: discord.Member, 
                     duration: int = commands.parameter(description="Duration of the timeout"), 
                     unit: str = commands.parameter(description="Unit of time (minutes, hours, days)", default="minutes"), 
                     *, reason: str = commands.parameter(description="Reason for timeout", default="No reason provided")):
        """
        Examples
        --------
        !timeout @User 5 minutes Spamming in chat
        !timeout @User 1 hours Breaking server rules
        !timeout @User 1 days Repeated rule violations
        """
        # Check permissions
        if ctx.author.id not in admin_ids and not ctx.author.guild_permissions.moderate_members:
            await ctx.send("You do not have permission to use this command.")
            return
        
        # Convert duration to timedelta
        time_units = {
            "minutes": 60,
            "hours": 3600,
            "days": 86400
        }
        
        if unit.lower() not in time_units:
            await ctx.send(f"Invalid time unit. Use: {', '.join(time_units.keys())}")
            return
            
        timeout_duration = timedelta(seconds=duration * time_units[unit.lower()])
        
        # Apply timeout
        try:
            await user.timeout(timeout_duration, reason=f"Timed out by {ctx.author.name}: {reason}")
            await ctx.send(
                f"{user.mention} has been timed out for {duration} {unit} | Reason: {reason}"
            )
            
            # Log the timeout action if log channel exists
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="User Timeout",
                        description=f"{user.mention} has been timed out",
                        color=discord.Color.orange(),
                        timestamp=ctx.message.created_at if hasattr(ctx, 'message') else discord.utils.utcnow()
                    )
                    embed.add_field(name="Duration", value=f"{duration} {unit}", inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                    embed.set_footer(text=f"ID: {user.id}")
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await ctx.send("I don't have permission to timeout this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}") 