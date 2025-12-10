import nextcord, asyncio
from nextcord.ext import commands
from nextcord import Interaction

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True

bot = commands.Bot("!", intents=intents)

# yeah yeah global list, fight me
ban_list = []


@bot.slash_command(name="add_to_banwave", description="throw some IDs in the ban pile")
async def add_ban(interaction: Interaction, user_ids: str):
    added = []
    for raw in user_ids.replace(" ", "").split(","):
        if not raw.isdigit(): continue
        uid = int(raw)
        if uid not in ban_list:
            ban_list.append(uid)
            added.append(uid)

    if added:
        await interaction.response.send_message(f"added {len(added)} scumbag(s): {', '.join(map(str, added))}")
    else:
        await interaction.response.send_message("lol none of those were new or valid")


@bot.slash_command(name="start_banwave", description="unleash the ban hammer")
async def go_nuclear(interaction: Interaction):
    if not ban_list:
        await interaction.response.send_message("ban list empty bro")
        return

    await interaction.response.send_message("here we go...")

    for uid in ban_list.copy():
        user = interaction.guild.get_member(uid)
        if not user:
            try: user = await bot.fetch_user(uid)
            except: user = None

        name = user.name if user else f"<@{uid}>"

        # progress
        e = nextcord.Embed(title="ban wave", description=f"hitting **{name}**...", color=0xff0000)
        m = await interaction.channel.send(embed=e)
        await asyncio.sleep(1.5 + (0.3 if len(ban_list) > 5 else 0))  # fake "work"

        try:
            await interaction.guild.ban(discord.Object(uid), reason="banwave go brrr")
            e.description = f"**{name}** got yeeted."
            e.color = 0x00ff00
        except Exception as err:
            e.description = f"**{name}** survived. ({err})"
            e.color = 0xffaa00
        await m.edit(embed=e)

    # donezo
    done = nextcord.Embed(title="ban wave over", description="**purged** all of 'em.", color=0x00ff00)
    fin = await interaction.channel.send(embed=done)
    await fin.add_reaction("skull")

    ban_list.clear()


@bot.slash_command(name="list_banwave", description="who's next?")
async def show_queue(interaction: Interaction):
    if not ban_list:
        await interaction.response.send_message("nobody in the chamber")
        return

    txt = "\n".join(f"`{x}`" for x in ban_list)
    e = nextcord.Embed(title=f"{len(ban_list)} in queue", description=txt, color=0x3498db)
    await interaction.response.send_message(embed=e)


@bot.slash_command(name="remove_from_banwave", description="let someone off the hook")
async def unqueue(interaction: Interaction, user_ids: str):
    removed = []
    for raw in user_ids.replace(" ", "").split(","):
        if not raw.isdigit(): continue
        uid = int(raw)
        if uid in ban_list:
            ban_list.remove(uid)
            removed.append(uid)

    if removed:
        await interaction.response.send_message(f"spared: {', '.join(map(str, removed))}")
    else:
        await interaction.response.send_message("none of those were even in there")


@bot.slash_command(name="clear_banwave", description="nuke the list")
async def wipe(interaction: Interaction):
    ban_list.clear()
    await interaction.response.send_message("list gone. fresh start.")


@bot.event
async def on_ready():
    print(f"bot up - {bot.user} ready to ban")


bot.run("insert token here")
