import requests
api_key="RGAPI-74bfc086-48f0-4791-a18a-4ac37a4dd14b"

def get_summoner(name : str, region : str):
    summoner=requests.get("https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(region, name, api_key)).status_code
    return summoner

def get_league(name : str, region : str):
    league=requests.get("https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(region, get_summoner(name, region)["id"], api_key))
    return league

def get_tft_league(name : str, region : str):
    tft_league=requests.get("https://{}.api.riotgames.com/tft/league/v1/entries/by-summoner/{}?api_key={}".format(region, get_summoner(name, region)["id"], api_key))
    return tft_league

def correct_name(name : str):
    y=name.replace(" ", "")
    x=y.replace("'", "")
    w=x.lower()
    z=w.capitalize()
    return z

def get_latest_version():
    request=requests.get(url="https://ddragon.leagueoflegends.com/api/versions.json").json()
    return request[0]

def get_champion_name_from_id(id : str):
    request=requests.get(url="https://ddragon.leagueoflegends.com/cdn/{}/data/fr_FR/champion.json".format(get_latest_version())).json()
    for k in request["data"]:
        if request["data"][k]["key"]==id:
            return k

for i in range(1):
    print(i)