import io
import nextcord as discord
from nextcord.ext import commands
import plotly.express as px
import functions


class Reputation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repDB = functions.rep_funcs.repDB

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            if functions.preferences.gpdb.get_pref('rep_enabled', message.guild.id):
                await functions.rep_funcs.repMessages(message)

    @discord.slash_command(description="View someone's current rep")
    async def rep(self, interaction: discord.Interaction,
                  user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=False)):
        await interaction.response.defer()
        if user is None:
            user = interaction.user
        rep = self.repDB.get_rep(user.id, str(interaction.guild.id))
        if rep is None:
            rep = 0

        embed = discord.Embed(
            title=f"{user.display_name}'s Reputation", description=f"{user} has {rep} rep.")

        async def graph_callback(interaction):
            await interaction.response.edit_message(content="Generating graph...", embed=None, view=None)

            df = self.repDB.graph_rep(user.id, str(interaction.guild.id))
            fig = px.line(df, x="date", y="rep",
                          title=f"{user.display_name}'s Reputation Over Time")
            fig.update_layout(xaxis_title="Date", yaxis_title="Reputation")

            buf = io.BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            file = discord.File(buf, filename="repgraph.png")

            embed = discord.Embed(
                title=f"{user.display_name}'s Reputation Over Time")
            embed.set_image(url="attachment://repgraph.png")

            await interaction.edit_original_message(embed=embed, file=file, content=None, view=None)

        graphit = discord.ui.Button(
            label="Graph it!", style=discord.ButtonStyle.primary, emoji="📈")
        graphit.callback = graph_callback

        view = discord.ui.View(timeout=120)
        view.add_item(graphit)

        await interaction.send(embed=embed, view=view, ephemeral=False)

    @discord.slash_command(description="Change someone's current rep (for mods)")
    async def change_rep(self, interaction: discord.Interaction,
                         user: discord.User = discord.SlashOption(name="user", description="User to view rep of",
                                                                  required=True),
                         new_rep: int = discord.SlashOption(name="new_rep", description="New rep amount", required=True,
                                                            min_value=0, max_value=9999)):
        if await functions.utility.isModerator(interaction.user):
            await interaction.response.defer()
            rep = self.repDB.change_rep(user.id, new_rep, str(
                interaction.guild.id), interaction.created_at)
            await interaction.send(f"{user} now has {rep} rep.", ephemeral=False)
        else:
            await interaction.send("You are not authorized to use this command.", ephemeral=True)

    @discord.slash_command(description="View the current rep leaderboard")
    async def leaderboard(self, interaction: discord.Interaction,
                          page: int = discord.SlashOption(name="page", description="Page number to to display",
                                                          required=False, min_value=1, max_value=99999),
                          user_to_find: discord.User = discord.SlashOption(name="user",
                                                                           description="User to find on the leaderboard",
                                                                           required=False)
                          ):
        await interaction.response.defer()
        leaderboard = self.repDB.rep_leaderboard(
            str(interaction.guild.id))  # Rep leaderboard
        # Changing format of leaderboard
        leaderboard = [item.values() for item in leaderboard]
        chunks = [leaderboard[x:x + 9] for x in
                  range(0, len(leaderboard), 9)]  # Split into groups of 9

        pages = []
        for n, chunk in enumerate(chunks):
            embed = discord.Embed(title="Reputation Leaderboard", description=f"Page {n + 1} of {len(chunks)}",
                                  colour=discord.Colour.green())
            for user, rep in chunk:
                if user_to_find:
                    if user_to_find.id == user:
                        page = n + 1
                user_name = interaction.guild.get_member(user)
                if rep == 0 or user_name is None:
                    self.repDB.delete_user(user, str(interaction.guild.id))
                else:
                    embed.add_field(name=user_name, value=str(
                        rep) + "\n", inline=True)
            pages.append(embed)

        if not page:
            page = 1

        first, prev = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.blurple), discord.ui.Button(
            emoji="⬅️", style=discord.ButtonStyle.blurple)
        if page == 1:
            first.disabled, prev.disabled = True, True

        nex, last = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.blurple), discord.ui.Button(
            emoji="⏩", style=discord.ButtonStyle.blurple)
        view = discord.ui.View(timeout=120)

        async def timeout():
            nonlocal message
            disabled = discord.ui.View()
            for b in view.children:
                d = b
                d.disabled = True
                disabled.add_item(d)
            await message.edit(view=disabled)
        view.on_timeout = timeout

        async def f_callback(b_interaction):
            if b_interaction.user != interaction.user:
                await b_interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            nonlocal page
            view = discord.ui.View(timeout=None)
            first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
            view.add_item(first)
            view.add_item(prev)
            view.add_item(nex)
            view.add_item(last)
            page = 1
            await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

        async def p_callback(b_interaction):
            if b_interaction.user != interaction.user:
                await b_interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            nonlocal page
            page -= 1
            view = discord.ui.View(timeout=None)
            if page == 1:
                first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
            else:
                first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
            view.add_item(first)
            view.add_item(prev)
            view.add_item(nex)
            view.add_item(last)
            await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

        async def n_callback(b_interaction):
            if b_interaction.user != interaction.user:
                await b_interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            nonlocal page
            page += 1
            view = discord.ui.View(timeout=None)
            if page == len(pages):
                first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
            else:
                first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
            view.add_item(first)
            view.add_item(prev)
            view.add_item(nex)
            view.add_item(last)
            await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

        async def l_callback(b_interaction):
            if b_interaction.user != interaction.user:
                await b_interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            nonlocal page
            view = discord.ui.View(timeout=None)
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
            view.add_item(first)
            view.add_item(prev)
            view.add_item(nex)
            view.add_item(last)
            page = len(pages)
            await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

        first.callback, prev.callback, nex.callback, last.callback = f_callback, p_callback, n_callback, l_callback
        view.add_item(first)
        view.add_item(prev)
        view.add_item(nex)
        view.add_item(last)

        message = await interaction.send(embed=pages[page - 1], view=view)


def setup(bot):
    bot.add_cog(Reputation(bot))
