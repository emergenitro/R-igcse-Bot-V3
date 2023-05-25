import time
import datetime
import nextcord as discord
from nextcord.ext import commands
import functions


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", message.guild.id))

        # Get message info
        user = message.author
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Get all attachments
        media_list = [await attachment.to_file() for attachment in message.attachments]

        # Create the message embed
        body = f"Message deleted in {message.channel.mention}"
        date = f"Sent on <t:{int(message.created_at.timestamp())}:F> and deleted on <t:{int(time.time())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nMessage = {message.id}```"

        delete_embed = discord.Embed(description=body, color=discord.Color.brand_red(
        ), timestamp=datetime.datetime.now())

        fields_dict = {"Content": message.content, "Date": date, "ID": id_str}
        functions.log_funcs.add_fields(delete_embed, fields_dict)
        delete_embed.set_author(name=name, icon_url=user.display_avatar.url)

        # Send the message embed
        await log_channel.send(embed=delete_embed, files=media_list)

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_before.author.bot: return
        
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", message_before.guild.id))

        # Check if the message content or attachments were edited
        if message_after.attachments != message_before.attachments or message_after.content != message_before.content:
            # Get message info
            user = message_before.author
            user_nickname = f" ({user.nick})" if user.nick else ""
            channel = message_before.channel

            # Get previous message attachments with their content
            prev_content = message_before.content
            prev_timestamp = message_before.created_at.timestamp()
            prev_attachments = []
            for attachment in message_before.attachments:
                prev_attachment_content = await attachment.read()
                prev_attachments.append((prev_attachment_content, await attachment.to_file()))

            # Get new message attachments with their content
            new_content = message_after.content
            new_attachments_dict = {}
            for attachment in message_after.attachments:
                new_attachment_content = await attachment.read()
                if (new_attachment_content, await attachment.to_file()) not in prev_attachments:
                    new_attachments_dict[new_attachment_content] = await attachment.to_file()
            new_timestamp = message_after.edited_at.timestamp()

            # Get message data
            body = f"[Message]({message_before.jump_url}) edited in {channel.mention}"
            date = f"Sent on <t:{int(prev_timestamp)}:F> and edited on <t:{int(new_timestamp)}:T>"
            name = f"{user.name}#{user.discriminator}{user_nickname}"
            id_str = f"```ini\nUser = {user.id}\nMessage = {message_after.id}```"
            deleted_attachment = []

            # Add deleted attachments
            for content, file in prev_attachments:
                if content not in new_attachments_dict:
                    deleted_attachment.append(file)

            # Create and send the message embed
            fields_dict = {"Old content": prev_content,
                           "New content": new_content, "Date": date, "ID": id_str}
            edit_embed = discord.Embed(
                description=body, color=discord.Color.blue(), timestamp=datetime.datetime.now())
            functions.log_funcs.add_fields(edit_embed, fields_dict)
            edit_embed.set_author(name=name, icon_url=user.display_avatar.url)
            await log_channel.send(embed=edit_embed, files=deleted_attachment)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", channel.guild.id))
        
        # Get the audit log entry for the channel create action
        audit_log_entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1).get()
        if not audit_log_entry:
            return

        # Get information about the user who created the channel
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the message content and embed
        body = f"New [channel]({channel.jump_url}) `{channel.name}` created"
        date = f"Created on <t:{int(channel.created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nChannel = {channel.id}```"
        channel_create_embed = discord.Embed(
            description=body, color=discord.Color.green(), timestamp=datetime.datetime.now())

        # Add fields to the embed
        fields_dict = {"Date": date, "ID": id_str}
        functions.log_funcs.add_fields(channel_create_embed, fields_dict)

        # Set author and send the message to the log channel
        channel_create_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=channel_create_embed)

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", thread.guild.id))

        # Get the audit log entry for the thread create action
        audit_log_entry = await thread.guild.audit_logs(action=discord.AuditLogAction.thread_create, limit=1).get()
        if not audit_log_entry:
            return

        # Get information about the user who created the thread
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the message content and embed
        body = f"New [thread]({thread.jump_url}) `{thread.name}` created"
        date = f"Created on <t:{int(thread.created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nThread = {thread.id}```"
        thread_create_embed = discord.Embed(
            description=body, color=discord.Color.green(), timestamp=datetime.datetime.now())

        # Add fields to the embed
        fields_dict = {"Date": date, "ID": id_str}
        functions.log_funcs.add_fields(thread_create_embed, fields_dict)

        # Set author and send the message to the log channel
        thread_create_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=thread_create_embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", channel.guild.id))

        # Get the audit log entry for the deleted channel
        audit_log_entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
        if not audit_log_entry:
            return

        # Get the user who deleted the channel and their nickname if they have one
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Get the time when the channel was deleted from the audit log entry
        channel_deleted_time = audit_log_entry.created_at.timestamp()

        # Create the body, date, name, and ID strings for the log message
        body = f"Channel `{channel.name}` deleted"
        date = f"Deleted on <t:{int(channel_deleted_time)}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nChannel = {channel.id}```"

        # Create the log embed and add the fields
        channel_delete_embed = discord.Embed(
            description=body, color=discord.Color.brand_red(), timestamp=datetime.datetime.now())
        fields_dict = {"Date": date, "ID": id_str}
        functions.log_funcs.add_fields(channel_delete_embed, fields_dict)

        # Set the author of the embed to the user who deleted the channel and their avatar
        channel_delete_embed.set_author(
            name=name, icon_url=user.display_avatar.url)

        # Send the log message to the log channel
        await log_channel.send(embed=channel_delete_embed)

    @commands.Cog.listener()
    async def on_thread_delete(self, thread):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", thread.guild.id))

        # Get the audit log entry for the deleted thread
        audit_log_entry = await thread.guild.audit_logs(action=discord.AuditLogAction.thread_delete, limit=1).get()
        if not audit_log_entry:
            return

        # Get the user who deleted the thread and their nickname if they have one
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Get the time when the thread was deleted from the audit log entry
        thread_deleted_time = audit_log_entry.created_at.timestamp()

        # Create the body, date, name, and ID strings for the log message
        body = f"Thread `{thread.name}` deleted"
        date = f"Deleted on <t:{int(thread_deleted_time)}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nThread = {thread.id}```"

        # Create the log embed and add the fields
        thread_delete_embed = discord.Embed(
            description=body, color=discord.Color.brand_red(), timestamp=datetime.datetime.now())
        fields_dict = {"Date": date, "ID": id_str}
        functions.log_funcs.add_fields(thread_delete_embed, fields_dict)

        # Set the author of the embed to the user who deleted the thread and their avatar
        thread_delete_embed.set_author(
            name=name, icon_url=user.display_avatar.url)

        # Send the log message to the log channel
        await log_channel.send(embed=thread_delete_embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", before.guild.id))

        # Get the audit log entry for the channel update
        audit_log_entry = await before.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1).flatten()
        if not audit_log_entry:
            return

        # Get the user who made the update and their nickname if they have one
        user = audit_log_entry[0].user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the embed body, author, and ID string
        body = f"[Channel]({after.jump_url}) `{before.name}` updated"
        date = f"Updated on <t:{int(audit_log_entry[0].created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nPerpetrator = {user.id}\nChannel = {after.id}```"

        # Create a dictionary of fields to add to the embed
        fields_dict = {"Date": date}

        # Handle text channel updates
        if isinstance(before, discord.channel.TextChannel):
            attribute_to_check = [
                ("Name", "name"), ("Description", "topic"), ("Slowmode", "slowmode_delay")]
            functions.functions.log_funcs.add_fields_for_functions(
                before, after, attribute_to_check, fields_dict)

        # Handle voice and stage channel updates
        elif isinstance(before, (discord.channel.VoiceChannel, discord.channel.StageChannel)):
            attribute_to_check = [("Name", "name"), ("Bitrate", "bitrate")]
            functions.log_funcs.add_fields_for_functions(
                before, after, attribute_to_check, fields_dict)

        # Add the ID field to the dictionary
        fields_dict["ID"] = id_str

        # Create the embed and send it to the log channel
        channel_update_embed = discord.Embed(
            description=body, color=discord.Color.green(), timestamp=datetime.datetime.now())
        functions.log_funcs.add_fields(channel_update_embed, fields_dict)
        channel_update_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=channel_update_embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", role.guild.id))

        # Get the audit log entry for the role create action
        audit_log_entry = await role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1).get()

        # Get information about the user who created the thread
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the message content and embed
        body = f"New role `{role.name}` created"
        date = f"Created on <t:{int(role.created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nRole = {role.id}```"
        role_create_embed = discord.Embed(
            description=body, color=discord.Color.green(), timestamp=datetime.datetime.now())

        # Add fields to the embed
        fields_dict = {"Date": date, "ID": id_str,
                       "Colour": role.color, "Hoist": role.hoist}
        functions.log_funcs.add_fields(role_create_embed, fields_dict)

        # Set author and send the message to the log channel
        role_create_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=role_create_embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", role.guild.id))

        # Get the audit log entry for the role create action
        audit_log_entry = await role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1).get()
        if not audit_log_entry:
            return

        # Get information about the user who created the thread
        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the message content and embed
        body = f"Role `{role.name}` deleted"
        date = f"Created on <t:{int(role.created_at.timestamp())}:F> and deleted on <t:{int(audit_log_entry.created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nUser = {user.id}\nRole = {role.id}```"
        role_delete_embed = discord.Embed(
            description=body, color=discord.Color.brand_red(), timestamp=datetime.datetime.now())

        # Add fields to the embed
        fields_dict = {"Date": date, "ID": id_str,
                       "Colour": role.color, "Hoist": role.hoist}
        functions.log_funcs.add_fields(role_delete_embed, fields_dict)

        # Set author and send the message to the log channel
        role_delete_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=role_delete_embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", before.guild.id))

        # Get the audit log entry for the channel update
        audit_log_entry = await before.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1).flatten()
        if not audit_log_entry:
            return

        # Get the user who made the update and their nickname if they have one
        user = audit_log_entry[0].user
        user_nickname = f" ({user.nick})" if user.nick else ""

        # Create the embed body, author, and ID string
        body = f"Role `{before.name}` updated"
        date = f"Updated on <t:{int(audit_log_entry[0].created_at.timestamp())}:F>"
        name = f"{user.name}#{user.discriminator}{user_nickname}"
        id_str = f"```ini\nPerpetrator = {user.id}\nChannel = {after.id}```"

        # Create a dictionary of fields to add to the embed
        fields_dict = {"Date": date}

        attributes_to_check = [
            ("Name", "name"), ("Colour", "color"), ("Hoist", "hoist")]
        functions.log_funcs.add_fields_for_functions(
            before, after, attributes_to_check, fields_dict)

        role_update_embed = discord.Embed(
            description=body, color=discord.Color.blue(), timestamp=datetime.datetime.now())
        functions.log_funcs.add_fields(role_update_embed, fields_dict)
        role_update_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=role_update_embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        log_channel = self.bot.get_channel(functions.preferences.gpdb.get_pref("log_channel", guild.id))

        # Get the audit log entry for the emoji update
        audit_log_entry = await guild.audit_logs(action=discord.AuditLogAction.emoji_create, limit=1).get()
        if not audit_log_entry:
            return

        user = audit_log_entry.user
        user_nickname = f" ({user.nick})" if user.nick else ""

        converted_before = [emoji.name for emoji in before]
        converted_after = [emoji.name for emoji in after]
        changes = list(set(converted_after) - set(converted_before))

        if len(after) == len(before):
            converted_before_unchanged = [
                emoji for emoji in converted_before if emoji not in converted_after]
            body = f"Emoji name of <:{changes[0]}:{after[converted_after.index(changes[0])].id}> updated\nBefore: {converted_before_unchanged[0]}\nAfter: {changes[0]}"
            color = discord.Color.blue()
        elif len(after) > len(before):
            body = f"New emoji {changes[0]} <:{changes[0]}:{after[converted_after.index(changes[0])].id}> created"
            color = discord.Color.green()
        elif len(after) < len(before):
            changes = list(set(converted_before) - set(converted_after))
            body = f"Emoji {changes[0]} deleted"
            color = discord.Color.red()

        name = f"{user.name}#{user.discriminator}{user_nickname}"

        try:
            id_str = f"```ini\nUser = {user.id}\nEmoji = {after[convertedAfter.index(changes[0])].id}```"
        except:
            id_str = f"```ini\nUser = {user.id}```"

        emoji_create_embed = discord.Embed(
            description=body, color=color, timestamp=datetime.datetime.now())
        fields_dict = {"ID": id_str}
        functions.log_funcs.add_fields(emoji_create_embed, fields_dict)

        emoji_create_embed.set_author(
            name=name, icon_url=user.display_avatar.url)
        await log_channel.send(embed=emoji_create_embed)


def setup(bot):
    bot.add_cog(Logs(bot))
