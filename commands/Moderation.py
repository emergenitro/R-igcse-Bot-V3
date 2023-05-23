import datetime
import nextcord as discord
from nextcord.ext import commands
import functions

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gpdb = functions.preferences.gpdb

    @commands.Cog.listener()
    async def on_auto_moderation_action_execution(self, automod_execution):
        # {"bot": "", "guild_id": "", "user_name": "", "user_id": "", "action_type": "", "moderator": "", "reason": "", "seconds": ""}
        guild = automod_execution.guild
        action_type = "Timeout"

        if automod_execution.action.type.name == "timeout":
            rule = await guild.fetch_auto_moderation_rule(automod_execution.rule_id)

            reason = rule.name  # Rule Name
            user_id = automod_execution.member_id  # Member ID
            timeout_time_seconds = automod_execution.action.metadata.duration_seconds  # Timeout Time in seconds

        await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": guild.id, "user_name": guild.get_member(user_id), "user_id": user_id, "action_type": "Timeout", "moderator": "Automod", "reason": rule.name, "seconds": timeout_time_seconds})
    
    # Add mod roles
    @discord.slash_command(description="Add a role to the list of mod roles (for mods)")
    async def addmod(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can use this command.")
            return
        mod_roles = self.gpdb.get_pref('mod_roles', interaction.guild.id) or []
        if role.id not in mod_roles:
            mod_roles.append(role.id)
            self.gpdb.set_pref('mod_roles', mod_roles, interaction.guild.id)
            await interaction.response.send_message(f"{role.name} has been added as a mod role.")
        else:
            await interaction.response.send_message(f"{role.name} is already a mod role.")

    # Remove mod roles
    @discord.slash_command(description="Remove a role from the list of mod roles (for mods)")
    async def removemod(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can use this command.")
            return
        mod_roles = self.gpdb.get_pref('mod_roles', interaction.guild.id) or []
        if role.id in mod_roles:
            mod_roles.remove(role.id)
            self.gpdb.set_pref('mod_roles', mod_roles, interaction.guild.id)
            await interaction.response.send_message(f"{role.name} has been removed as a mod role.")
        else:
            await interaction.response.send_message(f"{role.name} is not a mod role.")




    
    @discord.slash_command(description="Check a user's previous offenses (warns/timeouts/bans)")
    async def history(self, interaction: discord.Interaction,
                user: discord.User = discord.SlashOption(name="user", description="User to view history of", required=True)):
        mod = interaction.user
        if await functions.utility.isModerator(user) or (not await functions.utility.isModerator(interaction.user) and not await functions.utility.hasRole(interaction.user, "Chat Moderator")):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        await interaction.response.defer()
        modlog = self.gpdb.get_pref("modlog_channel", interaction.guild.id)
        warnlog = self.gpdb.get_pref("warnlog_channel", interaction.guild.id)
        if modlog and warnlog:
            history = []
            modlog = self.bot.get_channel(modlog)
            warnlog = self.bot.get_channel(warnlog)
            warn_history = await warnlog.history(limit=750).flatten()
            modlog_history = await modlog.history(limit=500).flatten()
            for msg in warn_history:
                if str(user.id) in msg.content:
                    history.append(msg.clean_content)
            for msg in modlog_history:
                if str(user.id) in msg.content:
                    history.append(msg.clean_content)
            if len(history) == 0:
                await interaction.send(f"{user} does not have any previous offenses.", ephemeral=False)
            else:
                text = ('\n\n'.join(history))[:1900]
                await interaction.send(f"{user}'s Moderation History:\n```{text}```", ephemeral=False)
        else:
            await interaction.send("Please set up your moglog and warnlog through /set_preferences first!")


    @discord.slash_command(description="Warn a user (for mods)")
    async def warn(self, interaction: discord.Interaction,
                user: discord.Member = discord.SlashOption(name="user", description="User to warn",
                                                            required=True),
                reason: str = discord.SlashOption(name="reason", description="Reason for warn", required=True)):
        action_type = "Warn"
        mod = interaction.user
        if await functions.utility.is_banned(user, interaction.guild):
            await interaction.send("User is banned from the server!", ephemeral=True)
            return
        if await functions.utility.isModerator(user) or (not await functions.utility.isModerator(interaction.user) and not await functions.utility.hasRole(interaction.user, "Chat Moderator")):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        await interaction.response.defer()
        warnlog_channel = self.gpdb.get_pref("warnlog_channel", interaction.guild.id)
        if warnlog_channel:
            await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod, "reason": reason})
        channel = await user.create_dm()
        await channel.send(
            f"You have been warned in r/IGCSE by moderator {mod} for \"{reason}\".\n\nPlease be mindful in your further interaction in the server to avoid further action being taken against you, such as a timeout or a ban.")
    

    @discord.slash_command(description="Timeout a user (for mods)")
    async def timeout(self, interaction: discord.Interaction,
                    user: discord.Member = discord.SlashOption(name="user", description="User to timeout",
                                                                required=True),
                    time_: str = discord.SlashOption(name="duration",
                                                    description="Duration of timeout (e.g. 1d5h) up to 28 days (use 'permanent')",
                                                    required=True),
                    reason: str = discord.SlashOption(name="reason", description="Reason for timeout", required=True)):
        action_type = "Timeout"
        mod = interaction.user.mention
        if await functions.utility.is_banned(user, interaction.guild):
            await interaction.send("User is banned from the server!", ephemeral=True)
            return
        if await functions.utility.isModerator(user) or (not await functions.utility.isModerator(interaction.user) and not await functions.utility.hasRole(interaction.user, "Chat Moderator")):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        await interaction.response.defer()
        if time_.lower() == "unspecified" or time_.lower() == "permanent" or time_.lower() == "undecided":
            seconds = 86400 * 28
        else:
            seconds = 0
            if "d" in time_:
                seconds += int(time_.split("d")[0]) * 86400
                time_ = time_.split("d")[1]
            if "h" in time_:
                seconds += int(time_.split("h")[0]) * 3600
                time_ = time_.split("h")[1]
            if "m" in time_:
                seconds += int(time_.split("m")[0]) * 60
                time_ = time_.split("m")[1]
            if "s" in time_:
                seconds += int(time_.split("s")[0])
        if seconds == 0:
            await interaction.send("You can't timeout for zero seconds!", ephemeral=True)
            return
        await user.edit(timeout=discord.utils.utcnow() + datetime.timedelta(seconds=seconds))

        message = await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod, "reason": reason, "seconds": seconds})

        await user.send(f'''You have been given a timeout on the r/IGCSE server 
    Reason: {reason}
    Duration: {message}
    Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)''')
        await interaction.send(
            f"{str(user)} has been put on time out until <t:{int(time.time()) + seconds}>, which is <t:{int(time.time()) + seconds}:R>.")


    @discord.slash_command(description="Untimeout a user (for mods)")
    async def untimeout(self, interaction: discord.Interaction,
                        user: discord.Member = discord.SlashOption(name="user", description="User to untimeout",
                                                                required=True)):
        action_type = "Remove Timeout"
        mod = interaction.user.mention
        if await functions.utility.is_banned(user, interaction.guild):
            await interaction.send("User is banned from the server!", ephemeral=True)
            return
        if await functions.utility.isModerator(user) or (not await functions.utility.isModerator(interaction.user) and not await functions.utility.hasRole(interaction.user, "Chat Moderator")):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        await interaction.response.defer()
        await user.edit(timeout=None)

        await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod})

        await interaction.send(f"Timeout has been removed from {str(user)}.")


    @discord.slash_command(description="Ban a user from the server (for mods)")
    async def ban(self, interaction:discord.Interaction,
                user: discord.Member = discord.SlashOption(name="user", description="User to ban",
                                                        required=True),
                reason: str = discord.SlashOption(name="reason", description="Reason for ban", required=True),
                delete_message_days: int = discord.SlashOption(name="delete_messages", choices={"Don't Delete Messages" : 0, "Delete Today's Messages" : 1, "Delete 3 Days of Messages" : 3, 'Delete 1 Week of Messages' : 7}, default=0, description="Duration of messages from the user to delete (defaults to zero)", required=False)):
        action_type = "Ban"
        mod = interaction.user.mention

        if type(user) is not discord.Member:
            await interaction.send("User is not a member of the server", ephemeral=True)
            return 
        if await functions.utility.isModerator(user) or not await functions.utility.isModerator(interaction.user) or await functions.utility.hasRole(interaction.user, "Temp Mod"):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        if await functions.utility.is_banned(user, interaction.guild):
            await interaction.send("User is banned from the server!", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            if interaction.guild.id == 576460042774118420:  # r/igcse
                await user.send(
                    f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'. If you feel this ban was done in error, to appeal your ban, please fill the form below.\nhttps://forms.gle/8qnWpSFbLDLdntdt8")
            else:
                await user.send(
                    f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'.")
        except:
            pass

        await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod, "reason": reason})

        await interaction.guild.ban(user, delete_message_days=delete_message_days)
        await interaction.send(f"{str(user)} has been banned.")


    @discord.slash_command(description="Unban a user from the server (for mods)")
    async def unban(self, interaction:discord.Interaction,
                    user: discord.User = discord.SlashOption(name="user", description="User to unban",
                                                    required=True)):
        action_type = "Unban"
        mod = interaction.user.mention
        if not await functions.utility.isModerator(interaction.user):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod})

        await interaction.response.defer()
        await interaction.guild.unban(user)
        await interaction.send(f"{str(user)} has been unbanned.")


    @discord.slash_command(description="Kick a user from the server (for mods)")
    async def kick(self, interaction:discord.Interaction,
                user: discord.Member = discord.SlashOption(name="user", description="User to kick",
                                                            required=True),
                reason: str = discord.SlashOption(name="reason", description="Reason for kick", required=True)):
        action_type = "Kick"
        mod = interaction.user.mention
        if await functions.utility.isModerator(user) or not await functions.utility.isModerator(interaction.user):
            await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
            return
        if await functions.utility.is_banned(user, interaction.guild):
            await interaction.send("User is banned from the server!", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been kicked from the server due to '{reason}'.")
        except:
            pass
        await functions.mod_funcs.send_action_message({"bot": self.bot, "guild_id": interaction.guild.id, "user_name": user, "user_id": user.id, "action_type": action_type, "moderator": mod})
        await interaction.guild.kick(user)
        await interaction.send(f"{str(user)} has been kicked.")


def setup(bot):
    bot.add_cog(Moderation(bot))