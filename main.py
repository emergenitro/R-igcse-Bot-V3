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


@bot.slash_command(name="unload", description="Unload")
async def unload(interaction: discord.Interaction, extension: str = discord.SlashOption(name="extension", description="The Extension to unload", required=True)):
    bot.unload_extension(f"commands.{extension}")
    await interaction.send("Extension unloaded")


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
                          log_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="log_channel",
                              description="Channel for bot logs to be logged.",
                              required=False),
                          emote_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="emote_channel",
                              description="Channel for emote voting to take place.",
                              required=False)):
    gpdb = functions.preferences.gpdb
    if not await functions.utility.isModerator(interaction.user):
        await interaction.send("You are not authorized to perform this action", ephemeral=True)
        return
    await interaction.response.defer()
    if modlog_channel:
        gpdb.set_pref('modlog_channel', modlog_channel.id,
                      interaction.guild.id)
    if rep_enabled:
        gpdb.set_pref('rep_enabled', rep_enabled, interaction.guild.id)
    if suggestions_channel:
        gpdb.set_pref("suggestions_channel",
                      suggestions_channel.id, interaction.guild.id)
    if warnlog_channel:
        gpdb.set_pref("warnlog_channel", warnlog_channel.id,
                      interaction.guild.id)
    if log_channel:
        gpdb.set_pref("log_channel", log_channel.id, interaction.guild.id)
    if emote_channel:
        gpdb.set_pref("emote_channel", emote_channel.id, interaction.guild.id)
    await interaction.send("Done.")

bot.run(TOKEN)
