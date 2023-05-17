import nextcord as discord

async def isModerator(member: discord.Member):
    roles = [role.id for role in member.roles]
    if 578170681670369290 in roles or 784673059906125864 in roles:  # r/igcse moderator role ids
        return True
    elif member.guild_permissions.administrator:
        return True
    return False

async def hasRole(member: discord.Member, role_name: str):
    roles = [role.name.lower() for role in member.roles]
    for role in roles:
        if role_name.lower() in role:
            return True
    return False

async def getRole(role_name: str):
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name = role_name)
    return role

async def is_banned(user, guild):
    try:
        await guild.fetch_ban(user)
        return True
    except discord.NotFound:
        return False

async def isServerBooster(member: discord.Member):
    return await hasRole(member, "Server Booster")

async def isHelper(member: discord.Member):
    if await hasRole(member, "IGCSE Helper") or await hasRole(member, 'AS/AL Helper'):
        return True
    return False