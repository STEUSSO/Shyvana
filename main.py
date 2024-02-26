import discord
import requests
import json

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

#REQUIREMENTS
api_key="RGAPI-74bfc086-48f0-4791-a18a-4ac37a4dd14b"
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

def get_latest_version():
    request=requests.get(url="https://ddragon.leagueoflegends.com/api/versions.json").json()
    return request[0]

def get_champion_name_from_id(id : int):
    request=requests.get(url="https://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion.json".format(get_latest_version())).json()
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
        summoner=request.json()
        e = discord.Embed(
        title=summoner["name"],
        description="Informations about **{}**'s account.".format(summoner["name"])
        )
        e.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(get_latest_version(), summoner["profileIconId"])
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
        await interaction.response.send_message(embed=e)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])
    
#lol_rank
@bot.tree.command(
    name="lol_rank",
    description="Gives you the LoL rank of a given user."
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
        summoner=request.json()
        e=discord.Embed(
            title=summoner["name"],
            description="Informations about **{}**'s ranked performances.".format(summoner["name"])
        )
        e.set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        league=get_league(name, region)
        if league==[]:
            e.add_field(
                name="Rank",
                value="**UNRANKED**"
            )
            with open("ranks.json", encoding="UTF-8") as f:
                data=json.load(f)
                e.set_thumbnail(
                    url=data["UNRANKED"]
                )
            await interaction.response.send_message(embed=e)
        for i in range(len(league)):
            e.add_field(
                name="Mode",
                value=league[i]["queueType"],
                inline=False
            )
            e.add_field(
                name="Rank",
                value="**{} {} {}LP**".format(league[i]["tier"], league[i]["rank"], league[i]["leaguePoints"])
            )
            e.add_field(
                name="Winrate",
                value="**{}%** ({} wins out of {} games).".format(round(league[i]["wins"]/(league[i]["wins"]+league[i]["losses"])*100, 1), league[i]["wins"], league[i]["wins"]+league[i]["losses"])
            )
            e.add_field(
                name="Inactive",
                value=league[i]["inactive"]
            )
            with open("ranks.json", encoding="UTF-8") as f:
                data=json.load(f)
                e.set_thumbnail(
                    url=data[league[i]["tier"]]
                )
        await interaction.response.send_message(embed=e)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

#tft_rank
@bot.tree.command(
    name="tft_rank",
    description="Gives you the TFT rank of a given player."
)
@app_commands.describe(
    name="The name of the player's account.",
    region="The region where the user plays."
)
@app_commands.choices(
    region=region_choices
)
async def tft_rank(
    interaction : discord.Interaction,
    name : str,
    region : str
):
    request=get_summoner(name, region)
    if request.status_code==200:
        summoner = get_summoner(name, region).json()
        e=discord.Embed(
            title=summoner["name"],
            description="Informations about **{}**'s TFT ranked performances.".format(summoner["name"])
        )
        e.set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        league=get_tft_league(name, region)
        if league==[]:
            e.add_field(
                name="Rank",
                value="**UNRANKED**"
            )
            with open("ranks.json", encoding="UTF-8") as f:
                data=json.load(f)
                e.set_thumbnail(
                    url=data["UNRANKED"]
                )
            await interaction.response.send_message(embed=e)
        for i in range(len(league)):
            e.add_field(
                name="Mode",
                value=league[i]["queueType"],
                inline=False
            )
            e.add_field(
                name="Rank",
                value="**{} {} {}LP**".format(league[i]["tier"], league[i]["rank"], league[i]["leaguePoints"])
            )
            e.add_field(
                name="Winrate",
                value="**{}%** ({} wins out of {} games).".format(round(league[i]["wins"]/(league[i]["wins"]+league[i]["losses"])*100, 1), league[i]["wins"], league[i]["wins"]+league[i]["losses"])
            )
            e.add_field(
                name="Inactive",
                value=league[i]["inactive"]
            )
            with open("ranks.json", encoding="UTF-8") as f:
                data=json.load(f)
                e.set_thumbnail(
                    url=data[league[i]["tier"]]
                )
        await interaction.response.send_message(embed=e)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

#lol_mastery
@bot.tree.command(
    name="lol_mastery",
    description="Showing how much mastery a given player has on different champions."
)
@app_commands.describe(
    name="The name of the player.",
    region="The region you would like to see free champions.",
    number="The ranking of the champion (starting from the best, number 1 if none is given)."
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
        summoner=request.json()
        e=discord.Embed(
            title=summoner["name"],
            description="Informations about {}'s masteries.".format(summoner["name"])
        )
        e.set_footer(
            text=f"Command made by {interaction.user}",
            icon_url=interaction.user.avatar
        )
        mastery=get_mastery(name, region)
        if number==None:
            number=0
        else:
            number-=1
        e.set_thumbnail(
            url="https://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png".format(get_latest_version(), get_champion_name_from_id(mastery[number]["championId"]))
        )
        e.add_field(
            name=get_champion_name_from_id(mastery[number]["championId"]),
            value="Mastery **{}** with **{}** points.".format(mastery[number]["championLevel"], mastery[number]["championPoints"]),
            inline=False
        )
        e.add_field(
            name="Tokens earned",
            value=mastery[number]["tokensEarned"]
        )
        e.add_field(
            name="Chest granted ?",
            value=mastery[number]["chestGranted"]
        )
        e.add_field(
            name="Points until next level",
            value=mastery[number]["championPointsUntilNextLevel"]
        )
        await interaction.response.send_message(embed=e)
    else:
        with open("errors.json", encoding="UTF-8") as f:
            data=json.load(f)
            await interaction.response.send_message(data[str(request.status_code)])

bot.run("")
