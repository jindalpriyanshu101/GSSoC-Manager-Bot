import discord
import os
from discord.ext import commands

def setup(bot, tree, bot_data, admin_ids, homies):
   
    guild_id = int(os.getenv('DISCORD_GUILD_ID'))
    
    @tree.command(
        name="addrole", 
        description="Add a role to a user", 
        guild=discord.Object(id=guild_id)
    )
    async def add_role(
        interaction: discord.Interaction, 
        user: discord.Member, 
        role: discord.Role,
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You do not have permission to add roles.", ephemeral=True)
            return
        
        # Check if bot can manage this role (role hierarchy)
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "I cannot add this role because it is higher than or equal to my highest role.",
                ephemeral=True
            )
            return
            
        # Check if the user already has the role
        if role in user.roles:
            await interaction.response.send_message(
                f"{user.mention} already has the {role.mention} role.",
                ephemeral=True
            )
            return
        
        # Add the role
        try:
            await user.add_roles(role, reason=f"Added by {interaction.user.name}: {reason}")
            await interaction.response.send_message(
                f"Added {role.mention} role to {user.mention}",
                ephemeral=False
            )
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Role Added",
                        description=f"{role.mention} role added to {user.mention}",
                        color=role.color,
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Added by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    
                    await log_channel.send(embed=embed)
        
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to add roles to this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @tree.command(
        name="removerole", 
        description="Remove a role from a user", 
        guild=discord.Object(id=guild_id)
    )
    async def remove_role(
        interaction: discord.Interaction, 
        user: discord.Member, 
        role: discord.Role,
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You do not have permission to remove roles.", ephemeral=True)
            return
        
        # Check if bot can manage this role (role hierarchy)
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "I cannot remove this role because it is higher than or equal to my highest role.",
                ephemeral=True
            )
            return
            
        # Check if the user has the role
        if role not in user.roles:
            await interaction.response.send_message(
                f"{user.mention} doesn't have the {role.mention} role.",
                ephemeral=True
            )
            return
        
        # Remove the role
        try:
            await user.remove_roles(role, reason=f"Removed by {interaction.user.name}: {reason}")
            await interaction.response.send_message(
                f"Removed {role.mention} role from {user.mention}",
                ephemeral=False
            )
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Role Removed",
                        description=f"{role.mention} role removed from {user.mention}",
                        color=discord.Color.orange(),
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Removed by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    
                    await log_channel.send(embed=embed)
        
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to remove roles from this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
            
    @tree.command(
        name="createrole", 
        description="Create a new role", 
        guild=discord.Object(id=guild_id)
    )
    async def create_role(
        interaction: discord.Interaction, 
        name: str,
        color: str = "#000000",
        hoist: bool = False,
        mentionable: bool = False,
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You do not have permission to create roles.", ephemeral=True)
            return
        
        try:
            # Parse the color
            try:
                # Strip the # if present
                if color.startswith('#'):
                    color = color[1:]
                
                # Convert hex to int
                color_int = int(color, 16)
                discord_color = discord.Color(color_int)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid color format. Please use hex format (e.g., #FF0000 for red).",
                    ephemeral=True
                )
                return
            
            # Create the role
            role = await interaction.guild.create_role(
                name=name,
                color=discord_color,
                hoist=hoist,  # Whether the role should be displayed separately in the member list
                mentionable=mentionable,
                reason=f"Created by {interaction.user.name}: {reason}"
            )
            
            await interaction.response.send_message(
                f"Created new role: {role.mention}",
                ephemeral=False
            )
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Role Created",
                        description=f"New role {role.mention} has been created",
                        color=discord_color,
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    
                    options = []
                    if hoist:
                        options.append("Displayed separately")
                    if mentionable:
                        options.append("Mentionable")
                    
                    if options:
                        embed.add_field(name="Options", value=", ".join(options), inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create roles.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
            
    @tree.command(
        name="deleterole", 
        description="Delete a role", 
        guild=discord.Object(id=guild_id)
    )
    async def delete_role(
        interaction: discord.Interaction, 
        role: discord.Role,
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to delete roles.", ephemeral=True)
            return
        
        # Check if bot can manage this role (role hierarchy)
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "I cannot delete this role because it is higher than or equal to my highest role.",
                ephemeral=True
            )
            return
            
        role_name = role.name
        role_color = role.color
        
        try:
            # Delete the role
            await role.delete(reason=f"Deleted by {interaction.user.name}: {reason}")
            
            await interaction.response.send_message(
                f"Deleted role: {role_name}",
                ephemeral=False
            )
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Role Deleted",
                        description=f"Role '{role_name}' has been deleted",
                        color=role_color,
                        timestamp=interaction.created_at
                    )
                    embed.add_field(name="Deleted by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    
                    await log_channel.send(embed=embed)
                    
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to delete this role.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
            
    @tree.command(
        name="massrole", 
        description="Add or remove a role from multiple users at once", 
        guild=discord.Object(id=guild_id)
    )
    async def mass_role(
        interaction: discord.Interaction, 
        role: discord.Role,
        action: str = "add",  # "add" or "remove"
        filter_role: discord.Role = None,  # Optional role to filter users by
        reason: str = "No reason provided"
    ):
        # Check permissions
        if interaction.user.id not in admin_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to perform mass role modifications.", ephemeral=True)
            return
        
        # Check if bot can manage this role (role hierarchy)
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "I cannot modify this role because it is higher than or equal to my highest role.",
                ephemeral=True
            )
            return
            
        # Validate action
        action = action.lower()
        if action not in ["add", "remove"]:
            await interaction.response.send_message(
                "Invalid action. Use 'add' or 'remove'.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Get members to modify
            members = []
            
            if filter_role:
                members = [member for member in interaction.guild.members if filter_role in member.roles]
            else:
                members = interaction.guild.members
                
            # Counters
            success_count = 0
            already_count = 0  # Already has/doesn't have role
            error_count = 0
                
            for member in members:
                try:
                    if action == "add":
                        if role in member.roles:
                            already_count += 1
                            continue
                            
                        await member.add_roles(role, reason=f"Mass role add by {interaction.user.name}: {reason}")
                        success_count += 1
                    else:  # remove
                        if role not in member.roles:
                            already_count += 1
                            continue
                            
                        await member.remove_roles(role, reason=f"Mass role remove by {interaction.user.name}: {reason}")
                        success_count += 1
                except:
                    error_count += 1
            
            # Build status message
            action_str = "added to" if action == "add" else "removed from"
            status = f"Role {role.mention} {action_str} {success_count} members"
            
            if already_count > 0:
                status += f", {already_count} already had/didn't have the role"
                
            if error_count > 0:
                status += f", {error_count} errors"
                
            await interaction.followup.send(status)
            
            # Log the action
            log_channel_id = int(os.getenv('LOG_CHANNEL_ID', 0))
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title=f"Mass Role {action.capitalize()}",
                        description=f"Role {role.mention} mass {action_str} members",
                        color=role.color,
                        timestamp=interaction.created_at
                    )
                    
                    filter_str = f"with {filter_role.mention} role" if filter_role else "all members"
                    
                    embed.add_field(name="Filter", value=filter_str, inline=True)
                    embed.add_field(name="Performed by", value=interaction.user.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=True)
                    embed.add_field(name="Results", value=status, inline=False)
                    
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
