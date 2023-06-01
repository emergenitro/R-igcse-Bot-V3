import os
from nextcord.ext import commands
import nextcord as discord
import functions

TOKEN = os.getenv("IGCSEBOT_TOKEN")

intents = discord.Intents().all()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

for fn in os.listdir("./commands"):
    if fn.endswith(".py"):
        bot.load_extension(f"commands.{fn[:-3]}")
        print(fn[:-3])


@bot.slash_command(name="load", description="Load")
async def load(interaction: discord.Interaction, extension: str = discord.SlashOption(name="extension", description="The Extension to load", required=True)):
    bot.load_extension(f"commands.{extension}")
    await interaction.send("Extension loaded")


@bot.slash_command(name="reload", description="Reload")
async def load(interaction: discord.Interaction, extension: str = discord.SlashOption(name="extension", description="The Extension to load", required=True)):
    bot.reload_extension(f"commands.{extension}")
    await interaction.send("Extension reloaded")


@bot.slash_command(description="Set server preferences (for mods)")
async def set_preferences(interaction: discord.Interaction,
                          modlog_channel: discord.abc.GuildChannel = discord.SlashOption(name="modlog_channel",
                                                                                         description="Channel for log of timeouts, bans, etc.",
                                                                                         required=False),
                          rep_enabled: bool = discord.SlashOption(name="rep_enabled",
                                                                  description="Enable the reputation system?",
                                                                  required=False),
                          suggestions_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="suggestions_channel",
                              description="Channel for new server suggestions to be displayed and voted upon.",
                              required=False),
                          warnlog_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="warnlog_channel",
                              description="Channel for warns to be logged.",
                              required=False),
                          emote_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="emote_channel",
                              description="Channel for emote voting to take place.",
                              required=False),
                          modmail_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="modmail_channel",
                              description="Channel for modmail to take place.",
                              required=False)):
    gpdb = functions.preferences.gpdb
    if not await functions.utility.isModerator(interaction.user):
        options = {
                "modlog_channel": modlog_channel,
                "rep_enabled": rep_enabled,
                "suggestions_channel": suggestions_channel,
                "warnlog_channel": warnlog_channel,
                "emote_channel": emote_channel,
                "modmail_channel": modmail_channel
            }

        for pref_name, option in options.items():
            if option is not None:
                if isinstance(option, discord.abc.GuildChannel):
                    gpdb.set_pref(pref_name, option.id, interaction.guild.id)
                elif isinstance(option, bool):
                    gpdb.set_pref(pref_name, option, interaction.guild.id)
    await interaction.send("Done.")

bot.run(TOKEN)
