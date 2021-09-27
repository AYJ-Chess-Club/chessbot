import os
import discord
import json
from discord.ext import commands
from discord.ext.commands.core import has_any_role
from discord.utils import get
from dotenv import load_dotenv
from discord_slash import SlashCommand

intents = discord.Intents.all()
intents.members = True
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
    users[str(user.id)]["guild_id"] = 0
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


loggin_channel = 891774186371027004


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
            description="""
To help you get started, we'd like you to verifiy.

Please use the following command **in the chess server channel** to verify: `+verify <First Name> <Last Name> <School>`

It will not work in DMs.
          
Example: `+verify John Doe Deere Public School`

You will recieve a DM from this bot when you have been approved.

Thank you, A.Y. Jackson Chess Club.
[Website](https://ayjchess.pythonanywhere.com) | [Instagram](https://www.instagram.com/ayjchessclub/)""",
        )
        join_embed.set_thumbnail(
            url="https://ayjchess.pythonanywhere.com/static/AYJ_Chess_Logo.svg"
        )
        await dm_target.send(embed=join_embed)
    except:
        pass


admins = [
    819673575799128095,
    523265083741306918,
    502962137472303114,
    724029571774808104,
    320963227163033601,
    621478653955538983,
    273155974179586048,
    463417330244780042,
    716001095872282745,
]


@bot.command()
async def verify(ctx, first_name, last_name, *, school):

    chess_guild = await bot.fetch_guild(777192115951763468)
    reactions = {"✅": "allow", "❎": "disallow"}

    verified_role = get(chess_guild.roles, name="Verified")
    member = await chess_guild.fetch_member(ctx.message.author.id)
    if verified_role in member.roles:
        await ctx.send("Stop! You're already verified!")
        return

    def check_response(reaction, user):
        return user.id in admins and reaction.emoji in reactions

    if first_name and last_name and school is not None:
        admin_channel = 891774186371027004
        # admin_channel = 891789171956543511
        channel_object = await bot.fetch_channel(admin_channel)
        verify_embed = discord.Embed(
            title=f"Verification of user {ctx.message.author.name}",
            description=f"""
First Name: {first_name}
Last Name: {last_name}
School: {school}
    """,
        )

        while True:
            sent_message = await channel_object.send(embed=verify_embed)
            for emoji in reactions:
                await sent_message.add_reaction(emoji)

            reaction, user = await bot.wait_for("reaction_add", check=check_response)

            if reactions[reaction.emoji] == "allow":
                await ctx.send(
                    "You have been verified. Have fun at the A.Y. Jackson Chess Club!"
                )
                await ctx.message.author.add_roles(verified_role)
                break
            elif reactions[reaction.emoji] == "disallow":
                await ctx.send("Sorry, you are not allowed in this server.")
                await channel_object.send(
                    f"User is disallowed by an Admin. Please kick <@{ctx.message.author.id}>"
                )
                break
    else:
        await ctx.send("Incorrect format.")


guild_ids = [777192115951763468]


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
async def dump(ctx, user: discord.User = None):
    def parse_user(raw_user):
        if raw_user is not None:
            return raw_user.id
        elif raw_user is None:
            return ctx.message.author.id

    user_id = parse_user(user)
    user = await bot.fetch_user(user_id)
    await open_account(user)
    users = await get_user_data()
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
            with open("users.json", "w") as f:
                json.dump(users, f)
        except:
            users[str(user.id)]["who_invited"] = "Alex"
            with open("users.json", "w") as f:
                json.dump(users, f)
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
