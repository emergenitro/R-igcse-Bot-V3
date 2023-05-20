from nextcord.ext import commands
import nextcord as discord
import os
from dotenv import load_dotenv

load_dotenv()

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

bot.run(TOKEN)