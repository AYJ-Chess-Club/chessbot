import os
import discord
import json
from discord.ext import commands
from discord.ext.commands.core import has_any_role
from dotenv import load_dotenv
from discord_slash import SlashCommand

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

load_dotenv()
token = os.getenv("token")

cogs = []
invites = {}


@bot.event
async def on_ready():
    print("Hello World!")
    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()
    print("tasks done")
    print(f"Username: {bot.user.name} | Logged in successfully")
    activity = discord.Activity(type=discord.ActivityType.listening, name="+help")
    await bot.change_presence(status=discord.Status.online, activity=activity)


async def open_account(user):
    users = await get_user_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}

    users[str(user.id)]["who_invited"] = ""
    users[str(user.id)]["user_id"] = 0
    users[str(user.id)]["name"] = ""
    users[str(user.id)]["invite_used"] = ""
    users[str(user.id)]["member_joined_at"] = 0
    users[str(user.id)]["guild_name"] = ""
    with open("users.json", "w") as f:
        json.dump(users, f)
    return True


async def get_user_data():
    with open("users.json", "r") as f:
        users = json.load(f)
    return users


for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as e:
        print(f"Could not load cog {cog}: {str(e)}")


# load and unload cogs for modularity purposes
@bot.command()
@commands.is_owner()
async def loadcog(ctx, cogname=None):
    if cogname is None:
        return
    try:
        bot.load_extension(cogname)
    except Exception as e:
        print(f"Could not load cog {cogname}: {str(e)}")
        await ctx.send(f"Could not load cog {cogname}: {str(e)}")
    else:
        print(f"Loaded cog: {cogname} sucessfully")
        await ctx.send(f"Loaded cog: {cogname} sucessfully")


@bot.command()
@commands.is_owner()
async def unloadcog(ctx, cogname=None):
    if cogname is None:
        return
    try:
        bot.unload_extension(cogname)
    except Exception as e:
        print(f"Could not unload cog {cogname}: {str(e)}")
        await ctx.send(f"Could not unload cog {cogname}: {str(e)}")
    else:
        print(f"Unloaded cog: {cogname} sucessfully")
        await ctx.send(f"Unloaded cog: {cogname} sucessfully")


def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv


# loggin_channel = 891774186371027004
loggin_channel = 891789171956543511


@bot.event
async def on_member_join(member):

    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()

    logging_channel = await bot.fetch_channel(loggin_channel)
    await open_account(member)
    users = await get_user_data()
    user = member
    member_joined_at = member.joined_at
    member_string = (
        str(member_joined_at.strftime("%A"))
        + " "
        + str(member_joined_at.strftime("%B"))
        + " "
        + str(member_joined_at.day)
        + ", "
        + str(member_joined_at.year)
    )

    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            await logging_channel.send(
                f"User `{member.name}` with id `{member.id}` joined.\nInvite code used: `https://discord.gg/{invite.code}`\nInviter is: {invite.inviter}\nData logged."
            )
            invites[member.guild.id] = invites_after_join
            users[str(user.id)]["who_invited"] = str(invite.inviter)
            break

    try:
        users[str(user.id)]["member_joined_at"] = member_string
        users[str(user.id)]["name"] = user.name
        users[str(user.id)]["user_id"] = user.id
        users[str(user.id)]["guild_name"] = member.guild.name
        users[str(user.id)]["guild_id"] = member.guild.id
        with open("users.json", "w") as f:
            json.dump(users, f)
        dm_target = await bot.fetch_user(member.id)
        join_embed = discord.Embed(
            title="Welcome to the AYJ Chess Club",
            description="""To help you get started, we'd like to verifiy you.\n
          Please use the following command to verify: `/verify` or `+verify`\n\n
          [Make an account on the club website](https://ayjchess.pythonanywhere.com)""",
        )
        join_embed.set_thumbnail(
            url="https://ayjchess.pythonanywhere.com/static/AYJ_Chess_Logo.svg"
        )
        await dm_target.send(embed=join_embed)
    except:
        pass


guild_ids = [777192115951763468]


@bot.command()
async def whois(ctx, username):
    await ctx.send("")


@bot.command()
async def me(ctx):
    await open_account(ctx.message.author)
    users = await get_user_data()
    user = ctx.message.author
    user_joined_at = ctx.message.author.joined_at

    joined_string = (
        str(user_joined_at.strftime("%A"))
        + " "
        + str(user_joined_at.strftime("%B"))
        + " "
        + str(user_joined_at.day)
        + ", "
        + str(user_joined_at.year)
        + "| Time: "
        + str(user_joined_at.strftime("%H"))
        + ":"
        + str(user_joined_at.strftime("%M"))
        + ":"
        + str(user_joined_at.strftime("%S"))
    )
    guild = await bot.fetch_guild(guild_ids[0])

    users[str(user.id)]["member_joined_at"] = joined_string
    users[str(user.id)]["name"] = user.name
    users[str(user.id)]["user_id"] = user.id
    users[str(user.id)]["guild_name"] = guild.name
    users[str(user.id)]["guild_id"] = guild.id

    with open("users.json", "w") as f:
        json.dump(users, f)
    await ctx.send(
        f"""
```
Your profile:

Name: {users[str(user.id)]["name"]}
Guild: {users[str(user.id)]["guild_name"]} with id of {users[str(user.id)]["guild_id"]}
Joined guild: {users[str(user.id)]["member_joined_at"]} 
Who invited you: {users[str(user.id)]["who_invited"]}

```
  """
    )


@bot.command()
async def dump(ctx):
    await open_account(ctx.message.author)
    users = await get_user_data()
    user = ctx.message.author
    await ctx.send(
        f"""
```json
{json.dumps(users[str(user.id)], indent=4, sort_keys=True)}
```
  """
    )


@bot.command()
@has_any_role("Admin")
async def setinvitefrom(ctx, person):

    if person is not None:
        await open_account(ctx.message.author)
        users = await get_user_data()
        user = ctx.message.author
        try:
            users[str(user.id)]["who_invited"] = str(person)
        except:
            users[str(user.id)]["who_invited"] = "Alex"
        await ctx.send("Updated your profile")
        await ctx.send(
            f"""
<@{ctx.message.author.id}>
```json
{json.dumps(users[str(user.id)], indent=4, sort_keys=True)}
```
"""
        )


@bot.event
async def on_member_remove(member):
    invites[member.guild.id] = await member.guild.invites()


bot.run(token)
