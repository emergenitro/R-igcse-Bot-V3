import nextcord as discord
import functions

class Modmail(commands.Cog):
    @commands.Cog.listener()
    def on_message(self, message):
        if not message.guild:
            mutual_guilds = [guild for guild in bot.guilds if message.author in guild.members]
            if len(mutual_guilds) == 1:
                guild = mutual_guilds[0]
            else:
                guild_list = "\n".join([f"{i+1}. {guild.name}" for i, guild in enumerate(mutual_guilds)])
                embed = discord.Embed(title="Choose Server", description=f"You and the bot are both in these servers, which one do you want to send it to:\n{guild_list}", colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                msg = await message.channel.send(embed=embed)
                for i in range(len(mutual_guilds)):
                    await msg.add_reaction(f"{i+1}️⃣")
                def check(reaction, user):
                    return user == message.author and str(reaction.emoji) in [f"{i+1}️⃣" for i in range(len(mutual_guilds))]
                reaction, user = await bot.wait_for('reaction_add', check=check)
                guild = mutual_guilds[int(str(reaction)[0])-1]
            category = discord.utils.get(guild.categories, name='COMMS')
            channel = discord.utils.get(category.channels, topic=str(message.author.id))
            if not channel:
                channel = await guild.create_text_channel(str(message.author).replace("#", "-"),
                                                        category=category,
                                                        topic=str(message.author.id))
            embed = discord.Embed(title="Message Received", description=f"This message will be sent to the mods of the {guild.name} server. Are you sure you want to send this?",
                                colour=discord.Colour.green())
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            msg = await channel.send(embed=embed)
            await msg.add_reaction("✅")
            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == '✅'
            reaction, user = await bot.wait_for('reaction_add', check=check)
            embed = discord.Embed(title="Message Received", description=message.clean_content,
                                colour=discord.Colour.green())
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            await channel.send(embed=embed)
            for attachment in message.attachments:
                await channel.send(file=await attachment.to_file())
            await message.add_reaction("✅")

        if message.guild.id == 576460042774118420 and message.channel.category:  # Sending modmails
            if message.channel.category.name.lower() == "comms" and not message.author.bot:
                if int(message.channel.topic) == message.author.id:
                    return
                else:
                    member = message.guild.get_member(int(message.channel.topic))
                    if message.content == ".sclose":
                        embed = discord.Embed(title="DM Channel Silently Closed",
                                            description=f"DM Channel with {member} has been closed by the moderators of r/IGCSE, without notifying the user.", colour=discord.Colour.green())
                        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                        await message.channel.delete()
                        await bot.get_channel(895961641219407923).send(embed=embed)
                        return
                    channel = await member.create_dm()
                    if message.content == ".close":
                        embed = discord.Embed(title="DM Channel Closed",
                                            description=f"DM Channel with {member} has been closed by the moderators of r/IGCSE.", colour=discord.Colour.green())
                        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                        await channel.send(embed=embed)
                        await message.channel.delete()
                        await bot.get_channel(895961641219407923).send(embed=embed)
                        return
                    embed = discord.Embed(title="Message from r/IGCSE Moderators",
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
    @discord.slash_command(description="Create a modmail channel for a user")
    async def create_modmail(self, interaction: discord.Interaction,
                            user: discord.Member = discord.SlashOption(name="user", description="User to create a modmail channel for", required=True)):
        category = discord.utils.get(interaction.guild.categories, name='COMMS')
        channel = discord.utils.get(category.channels, topic=str(user.id))
        if not channel:
            channel = await interaction.guild.create_text_channel(str(user).replace("#", "-"),
                                                                category=category, topic=str(user.id))
        await interaction.response.send_message(f"DM Channel has been created at {channel.mention}")
