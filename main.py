import discord
import requests
import json

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from datetime import datetime

#REQUIREMENTS
api_key=""
region_choices=[
    Choice(
        name="EUW",
        value="euw1"
    ),
    Choice(
        name="KR",
        value="kr"
    ),
    Choice(
        name="BR",
        value="br1"
    ),
    Choice(
        name="EUN",
        value="eun1"
    ),
    Choice(
        name="JP",
        value="jp1"
    ),
    Choice(
        name="LA1",
        value="la1"
    ),
    Choice(
        name="LA2",
        value="la2"
    ),
    Choice(
        name="NA",
        value="na1"
    ),
    Choice(
        name="OC",
        value="oc1"
    ),
    Choice(
        name="TR",
        value="tr1"
    ),
    Choice(
        name="RU",
        value="ru"
    ),
    Choice(
        name="PH",
        value="ph2"
    ),
    Choice(
        name="SG",
        value="sg2"
    ),
    Choice(
        name="TH",
        value="th2",
    ),
    Choice(
        name="TW",
        value="tw2"
    ),
    Choice(
        name="VN",
        value="vn2"
    )
]

def get_summoner(name : str, region : str):
    request=requests.get("https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(region, name, api_key))
    return request

def get_league(name : str, region : str):
    request=requests.get("https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(region, get_summoner(name, region).json()["id"], api_key)).json()
    return request

def get_tft_league(name : str, region : str):
    request=requests.get("https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}".format(region, get_summoner(name, region).json()["id"], api_key)).json()
    return request

def get_mastery(name : str, region : str):
    request=requests.get("https://{}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{}?api_key={}".format(region, get_summoner(name, region).json()["puuid"], api_key)).json()
    return request

def correct_name(name : str):
    y=name.replace(" ", "")
    x=y.replace("'", "")
    w=x.lower()
    z=w.capitalize()
    return z

def get_versions():
    request=requests.get(url="https://ddragon.leagueoflegends.com/api/versions.json").json()
    return request

def get_champion_name_from_id(id : int):
    request=requests.get(url="https://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion.json".format(get_versions()[0])).json()
    for k in request["data"]:
        if request["data"][k]["key"]==str(id):
            return k

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.event   
async def on_ready():
    print(f"Le Bot {bot.user} est connecté !")
    await bot.change_presence(
        activity=discord.Game(
            name=f"Analyze LoL Stats."
        )
    )
    x = []
    for guild in bot.guilds:
        x.append(guild.id)
    print(len(x))
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

#account
@bot.tree.command(
    name="account",
    description="Gives you basic informations about a selected user."
)
@app_commands.describe(
    region="The region of the account.",
    name="The name of the account."
)
@app_commands.choices(
    region=region_choices
)
async def account(
    interaction : discord.Interaction,
    name : str,
    region : str
):
    request=get_summoner(name, region)
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        summoner=request.json()
        e = discord.Embed(
        title=summoner["name"],
        description="Informations about {}'s account.".format(summoner["name"])
        )
        e.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(get_versions()[0], summoner["profileIconId"])
        )
        e.add_field(
            name="Level",
            value=summoner["summonerLevel"],
            inline=False
        )
        e.add_field(
            name="ID",
            value=summoner["id"],
            inline=False
        )
        e.add_field(
            name="AccountID",
            value=summoner["accountId"],
            inline=False
        )
        e.add_field(
            name="PUUID",
            value=summoner["puuid"],
            inline=False
        )
        e.set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        await interaction.edit_original_response(content=None, embed=e)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])
#lol_rank
@bot.tree.command(
    name="lol_rank",
    description="Gives you the different ranks of a given player"
)
@app_commands.describe(
    name="The name of the player's account.",
    region="The region where the user is playing."
)
@app_commands.choices(
    region=region_choices
)
async def lol_rank(
    interaction : discord.Interaction,
    name : str,
    region : str
):
    request=get_summoner(name, region)
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        summoner=request.json()
        e=discord.Embed(
            title=summoner["name"],
            description="Informations about {}'s all ranked performances.".format(summoner["name"])
        )
        e.set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        e.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(get_versions()[0], summoner["profileIconId"])
        )
        league=get_league(name, region)+get_tft_league(name, region)
        list_embeds=[e]
        if league==[]:
            embed=discord.Embed(
                title="Rank"
            )
            embed.add_field(
                name="Rank of {}".format(summoner["name"]),
                value="UNRANKED"
            )
            with open("ranks.json", encoding="UTF-8") as f:
                data=json.load(f)
                embed.set_thumbnail(
                    url=data["UNRANKED"]
                )
            list_embeds.append(embed)
        else:
            for i in range(len(league)):
                embed=discord.Embed(
                    title=league[i]["queueType"],
                    description="Rank of {} in {}".format(summoner["name"], league[i]["queueType"])
                )
                embed.add_field(
                    name="Rank",
                    value="{} {} {}LP".format(league[i]["tier"], league[i]["rank"], league[i]["leaguePoints"])
                )
                embed.add_field(
                    name="Winrate",
                    value="{}% ({} wins out of {} games).".format(round(league[i]["wins"]/(league[i]["wins"]+league[i]["losses"])*100, 1), league[i]["wins"], league[i]["wins"]+league[i]["losses"])
                )
                embed.add_field(
                    name="Inactive",
                    value=league[i]["inactive"]
                )
                with open("ranks.json", encoding="UTF-8") as f:
                    data=json.load(f)
                    embed.set_thumbnail(
                        url=data[league[i]["tier"]]
                    )
                list_embeds.append(embed)
        await interaction.edit_original_response(content=None, embeds=list_embeds)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

#lol_mastery
@bot.tree.command(
    name="lol_mastery",
    description="Showing how much mastery a given player has on different champions (showing 3 of them)."
)
@app_commands.describe(
    name="The name of the player.",
    region="The region you would like to see free champions.",
    number="The number the bot will start counting from."
)
@app_commands.choices(
    region=region_choices
)
async def lol_mastery(
    interaction : discord.Interaction,
    name : str,
    region : str,
    number : int = None
):
    request = get_summoner(name, region)
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        summoner=request.json()
        mastery=get_mastery(name, region)
        if number==None:
            number=0
        else:
            number-=1
        try:
            list_embeds=[]
            for i in range(number, number+3):
                champion=get_champion_name_from_id(mastery[i]["championId"])
                embed=discord.Embed(
                    title=champion,
                    description="Mastery {} with {} points.".format(mastery[i]["championLevel"], mastery[i]["championPoints"])
                )
                embed.set_thumbnail(
                    url="https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(get_versions()[0], champion)
                )
                embed.add_field(
                    name="Tokens earned",
                    value=mastery[i]["tokensEarned"]
                )
                embed.add_field(
                    name="Chest granted ?",
                    value=mastery[i]["chestGranted"]
                )
                embed.add_field(
                    name="Points until next level",
                    value=mastery[i]["championPointsUntilNextLevel"]
                )
                list_embeds.append(embed)
            list_embeds[-1].set_footer(
                text=f"Command made by {interaction.user}",
                icon_url=interaction.user.avatar
            )
            await interaction.edit_original_response(content=None, embeds=list_embeds)
        except IndexError:
            await interaction.edit_original_response(content=f"❌ Out of range, the number {number+1} is too high or too low.")
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

#lol_champion
@bot.tree.command(
    name="lol_champion",
    description="Gives you informations about a given champion."
)
@app_commands.describe(
    champion="The champion you want to get informations about."
)
async def lol_champion(
    interaction : discord.Interaction,
    champion : str
):
    correct_champion=correct_name(champion)
    request=requests.get("https://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion/{}.json".format(get_versions()[0], correct_champion))
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        champion_data=request.json()["data"][correct_champion]
        e=discord.Embed(
            title="{}, {}".format(correct_champion, champion_data["title"]),
            description=f"Informations about {correct_champion}"
        )
        e.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(get_versions()[0], correct_champion)
        )
        e.add_field(
            name="Description",
            value=champion_data["blurb"],
            inline=False
        )
        e.add_field(
            name="Type",
            value=champion_data["partype"]
        )
        e.add_field(
            name="Roles",
            value=", ".join(champion_data["tags"])
        )
        passive=discord.Embed(
            title="Passive",
            description=champion_data["passive"]["name"]
        )
        passive.add_field(
            name="Description",
            value=champion_data["passive"]["description"]
        )
        passive.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/passive/{}".format(get_versions()[0], champion_data["passive"]["image"]["full"])
        )
        list_embeds=[e, passive]
        for i in range(len(champion_data["spells"])):
            spell_data=champion_data["spells"][i]
            embed=discord.Embed(
                title=spell_data["id"],
                description=spell_data["name"]
            )
            embed.set_thumbnail(
                url="https://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}".format(get_versions()[0], spell_data["image"]["full"])
            )
            embed.add_field(
                name="Description",
                value=spell_data["description"],
                inline=False
            )
            embed.add_field(
                name="Cost",
                value=spell_data["costBurn"]
            )
            embed.add_field(
                name="Range",
                value=spell_data["rangeBurn"]
            )
            embed.add_field(
                name="Cooldown",
                value=spell_data["cooldownBurn"]
            )
            list_embeds.append(embed)
        list_embeds[-1].set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        await interaction.edit_original_response(content=None, embeds=list_embeds)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

#lol_status
@bot.tree.command(
    name="lol_status",
    description="Gives you informations about LoL server status."
)
@app_commands.describe(
    region="The region you're playing in."
)
@app_commands.choices(
    region=region_choices
)
async def lol_status(
    interaction : discord.Interaction,
    region : str
):
    request=requests.get("https://{}.api.riotgames.com/lol/status/v4/platform-data?api_key={}".format(region, api_key))
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        data=request.json()
        list_embeds=[]
        for i in range(len(data["incidents"])):
            for k in range(len(data["incidents"][i]["titles"])):
                if data["incidents"][i]["titles"][k]["locale"]=="en_US":
                    index=k
            embed=discord.Embed(
                title=data["incidents"][i]["titles"][index]["content"],
                description=data["incidents"][i]["updates"][0]["translations"][index]["content"],
                color=0xFF0000
            )
            date=data["incidents"][i]["created_at"]
            date_obj = datetime.fromisoformat(date)
            date_readable = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(
                name="Started at",
                value=date_readable
            )
            embed.add_field(
                name="Severity",
                value=data["incidents"][i]["incident_severity"]
            )
            list_embeds.append(embed)
        for i in range(len(data["maintenances"])):
            for k in range(len(data["maintenances"][i]["titles"])):
                if data["maintenances"][i]["titles"][k]["locale"]=="en_US":
                    index=k
            embed=discord.Embed(
                title=data["maintenances"][i]["titles"][index]["content"],
                description=data["maintenances"][i]["updates"][0]["translations"][index]["content"],
                color=0xFF0000
            )
            date=data["maintenances"][i]["created_at"]
            date_obj = datetime.fromisoformat(date)
            date_readable = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(
                name="Started at",
                value=date_readable
            )
            embed.add_field(
                name="Severity",
                value=data["maintenances"][i]["incident_severity"]
            )
            list_embeds.append(embed)
        list_embeds[-1].set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        if list_embeds==[]:
            e=discord.Embed(
                title="No issues ✅",
                description="There are currently no issues on these servers.",
                color=0x00FF0D
            )
            list_embeds.append(e)
        await interaction.edit_original_response(content=None, embeds=list_embeds)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

@bot.tree.command(
    name="lol_match",
    description="Gives you informations about the current match."
)
@app_commands.describe(
    name="The username.",
    region="The region you're playing in."
)
@app_commands.choices(
    region=region_choices
)
async def lol_status(
    interaction : discord.Interaction,
    name : str,
    region : str
):
    request=requests.get("https://{}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{}?api_key={}".format(region, get_summoner(name, region).json()["id"], api_key))
    if request.status_code==200:
        await interaction.response.send_message("Please wait... ⏳")
        game_data=request.json()
        list_embeds=[]
        for i in range(len(game_data["participants"])):
            if i<=4:
                color=0x0080FF
            else:
                color=0xFF0000
            summoner=get_summoner(game_data["participants"][i]["summonerName"], region).json()
            league=get_league(game_data["participants"][i]["summonerName"], region)
            mastery_data=get_mastery(game_data["participants"][i]["summonerName"], region)
            champion=get_champion_name_from_id(game_data["participants"][i]["championId"])
            for j in range(len(mastery_data)):
                if mastery_data[j]["championId"]==game_data["participants"][i]["championId"]:
                    mastery="Mastery {}, {} points.".format(mastery_data[j]["championLevel"], mastery_data[j]["championPoints"])
            embed=discord.Embed(
                title=game_data["participants"][i]["summonerName"],
                description="Level {}".format(summoner["summonerLevel"]),
                color=color
            )
            tier="UNRANKED"
            rank="UNRANKED"
            for k in range(len(league)):
                if league[k]["queueType"]=="RANKED_SOLO_5x5":
                    tier=league[k]["tier"]
                    rank="{} {} {}LP".format(tier, league[k]["rank"], league[k]["leaguePoints"])
                    winrate="{}% ({} wins out of {} games).".format(round(league[k]["wins"]/(league[k]["wins"]+league[k]["losses"])*100, 1), league[k]["wins"], league[k]["wins"]+league[k]["losses"])
            embed.add_field(
                name="Rank",
                value=rank
            )
            embed.add_field(
                name="Winrate",
                value=winrate
            )
            embed.add_field(
                name="Mastery",
                value=mastery
            )
            embed.set_thumbnail(
                url="https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(get_versions()[0], champion)
            )
            list_embeds.append(embed)
        list_embeds[-1].set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        await interaction.edit_original_response(content=None, embeds=list_embeds)  
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

bot.run("")