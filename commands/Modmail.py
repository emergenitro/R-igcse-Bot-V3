import nextcord as discord
from nextcord.ext import commands
import functions
import asyncio

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gpdb = functions.preferences.gpdb
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if not isinstance(message.channel, discord.DMChannel) and not functions.preferences.gpdb.get_pref("modmail_channel", message.guild.id):
            return
        if not message.guild:
            mutual_guilds = [guild for guild in self.bot.guilds if message.author in guild.members]
            if len(mutual_guilds) == 1:
                guild = mutual_guilds[0]
            else:
                guild_list = "\n".join([f"{i+1}. {guild.name}" for i, guild in enumerate(mutual_guilds)])
                embed = discord.Embed(title="Choose Server", description=f"You and the bot are both in these servers, which one do you want to send it to:\n{guild_list}", colour=discord.Colour.yellow())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                msg = await message.channel.send(embed=embed)
                for i in range(len(mutual_guilds)):
                    await msg.add_reaction(f"{i+1}️⃣")
                def check(reaction, user):
                    return user == message.author and str(reaction.emoji) in [f"{i+1}️⃣" for i in range(len(mutual_guilds))]
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                guild = mutual_guilds[int(str(reaction)[0])-1]

            if functions.preferences.gpdb.get_pref("modmail_channel", guild.id): embed = discord.Embed(title="Message Received", description=f"This message will be sent to the mods of the {guild.name} server. Are you sure you want to send this?\nClick on the :white_check_mark: to confirm, and :x: to terminate this conversation", colour=discord.Colour.yellow())
            else:
                embed = discord.Embed(title="Message Declined", description=f"{guild.name} has not yet setup modmail. Use /set_preferences to set it up", colour=discord.Colour.red())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                await message.author.send(embed=embed)
                return
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            msg = await message.author.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            def check(reaction, user):
                return user == message.author and str(reaction.emoji) in ['✅', '❌']
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if str(reaction.emoji) == '✅':
                forum_channel = discord.utils.get(guild.channels, name='modmail', type=discord.ChannelType.forum)
                if forum_channel is None:
                    forum_channel = await guild.create_forum_channel(name='modmail', topic="Modmail for DMs")
                thread = discord.utils.get(forum_channel.threads, name=f"{message.author}")
                if thread is None:
                    thread = await forum_channel.create_thread(name=f"{message.author}", auto_archive_duration=60, content="New DM received.")
                embed = discord.Embed(title="Message Sent", description=f"Your message has been sent to the mods of the {guild.name} server.", colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                await msg.edit(embed=embed)
                embed = discord.Embed(title="Message Received", description=message.clean_content,
                                    colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                await thread.send(embed=embed)
                for attachment in message.attachments:
                    await thread.send(file=await attachment.to_file())
                await message.add_reaction("✅")
            else:
                embed = discord.Embed(title="Conversation Terminated", description=f"The conversation has been terminated.", colour=discord.Colour.red())
                await msg.edit(embed=embed)
                await asyncio.sleep(5)
                await msg.delete()

        else:
            modmail_channel_id = functions.preferences.gpdb.get_pref("modmail_channel", message.guild.id)
            if str(message.channel.parent) == "modmail":
                username, discriminator = message.channel.name.split('#')
                user = discord.utils.find(lambda u: u.name == username and u.discriminator == discriminator, self.bot.users)
                if user:
                    member = await message.guild.fetch_member(user.id)
                if message.content == ".sclose":
                    embed = discord.Embed(title="DM Channel Silently Closed",
                                        description=f"DM Channel with {member} has been closed by the moderators of {message.guild.name}, without notifying the user.", colour=discord.Colour.green())
                    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                    await message.channel.delete()
                    await self.bot.get_channel(modmail_channel_id).send(embed=embed)
                    return
                channel = await member.create_dm()  
                if message.content == ".close":
                    embed = discord.Embed(title="DM Channel Closed",
                                        description=f"DM Channel with {member} has been closed by the moderators of {message.guild.name}.", colour=discord.Colour.green())
                    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                    await channel.send(embed=embed)
                    await message.channel.delete()
                    await self.bot.get_channel(modmail_channel_id).send(embed=embed)
                    return
                if message.content.startswith(".r "):
                    embed = discord.Embed(title=f"Message from {message.author.name}({message.guild.name} Moderator)",
                                            description=message.clean_content, colour=discord.Colour.green())
                    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)

                    try:
                        await channel.send(embed=embed)
                        for attachment in message.attachments:
                            await channel.send(file=await attachment.to_file())
                        await message.channel.send(embed=embed)
                    except:
                        perms = message.channel.overwrites_for(member)
                        perms.send_messages, perms.read_messages, perms.view_channel, perms.read_message_history, perms.attach_files = True, True, True, True, True
                        await message.channel.set_permissions(member, overwrite=perms)
                        await message.channel.send(f"{member.mention}")
                        return
    
                    await message.delete()
                    return
                if message.content.startswith(".ar "):
                    embed = discord.Embed(title=f"Message from {message.guild.name} Moderators",
                                            description=message.clean_content, colour=discord.Colour.green())
                    embed.set_author(name=message.guild.name, icon_url=message.guild.icon)

                    try:
                        await channel.send(embed=embed)
                        for attachment in message.attachments:
                            await channel.send(file=await attachment.to_file())
                        await message.channel.send(embed=embed)
                    except:
                        perms = message.channel.overwrites_for(member)
                        perms.send_messages, perms.read_messages, perms.view_channel, perms.read_message_history, perms.attach_files = True, True, True, True, True
                        await message.channel.set_permissions(member, overwrite=perms)
                        await message.channel.send(f"{member.mention}")
                        return

                    await message.delete()
    @discord.slash_command(description="Create a modmail thread for a user")
    async def create_modmail(self, interaction: discord.Interaction,
                            user: discord.Member = discord.SlashOption(name="user", description="User to create a modmail thread for", required=True)):
        forum_channel = discord.utils.get(interaction.guild.channels, name='modmail', type=discord.ChannelType.forum)
        if forum_channel is None:
            forum_channel = await guild.create_forum_channel(name='modmail', topic="Modmail for DMs")
        thread = discord.utils.get(forum_channel.threads, name=f"{user}")
        if thread is None:
            thread = await forum_channel.create_thread(name=f"{user}", auto_archive_duration=60, content="New DM received/created.")
            await interaction.response.send_message(f"DM Thread has been created at {thread.mention}")
        else:
            await thread.send(content="New DM created.")
            await interaction.response.send_message(f"DM Thread already exists at {thread.mention}")


def setup(bot):
    bot.add_cog(Modmail(bot))