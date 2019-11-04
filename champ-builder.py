#!/usr/bin/env python3
# python -m pip install -U pip
# python -m pip install -U selenium webdriverdownloader textdistance

# search region
# role
# lane

from webdriverdownloader import GeckoDriverDownloader
gdd = GeckoDriverDownloader()
gdd.download_and_install()
from pathlib import Path
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import textdistance
import requests
import json

API_KEY = "RGAPI-4b46cead-4de4-47e0-b2b9-ac12e27325af"

if not API_KEY:
    API_KEY = input('API key: ')
    
champName = ''.join([i for i in input('Champion name: ') if i.isalpha()])

lolVer = json.loads(requests.get(
    "http://ddragon.leagueoflegends.com/api/versions.json").content)[0]
champDict = json.loads(requests.get(
    "https://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json"
    .format(lolVer)).content)['data']

champDists = {champId:textdistance.damerau_levenshtein(champName.lower(), champId.lower()) for champId in champDict }

if champName in champDict.keys():
    print('{} found'.format(champName))
else:
    closestChamp = min(champDists.keys(), key=(lambda dist: champDists[dist]))
    print('Champion {} not found, using closest champion: {}'.format(champName, closestChamp))
    champName = closestChamp

driverPath = str(tuple(Path(str(Path.home()) + '\webdriver\gecko')
                       .glob('**/geckodriver.exe'))[0])
opt = Options()
opt.set_headless()
print('Initializing web-scraper')
driver = Firefox(options=opt, executable_path=driverPath)

print('Fetching top 50 player list for {}'.format(champName))
driver.get('https://www.op.gg/ranking/champions/name={}'.format(champName))
users = [result.text for result in driver.find_elements_by_class_name(
    'ranking-summary-summoner__name')] + [result.text for result in driver.find_elements_by_class_name(
    'champion-ranking-table__cell--summoner')]
driver.close()

for user in users[:1]:
    accData = json.loads(requests.get(
        "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}"
        .format(user, API_KEY)).content)
    matchHistory = json.loads(requests.get(
        "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?champion={}&queue=420&endIndex=10&api_key={}"
        .format(accData['accountId'], champDict[champName]['key'], API_KEY)).content)['matches']
    for matchSummary in matchHistory:
        match = json.loads(requests.get(
            "https://kr.api.riotgames.com/lol/match/v4/matches/{}?api_key={}"
            .format(matchSummary['gameId'], API_KEY)).content)

# http://ddragon.leagueoflegends.com/api/versions.json
# https://ddragon.leagueoflegends.com/cdn/9.20.1/data/en_US/champion.json
# https://na1.api.riotgames.com/api/lol/summoner/v4/summoners/by-name/{summonerName}
# https://na1.api.riotgames.com/api/lol/match/v4/matchlists/by-account/{encryptedAccountId}
# https://na1.api.riotgames.com/api/lol/match/v4/matches/{matchId}

#response = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={})")
#htmlData = response.content.decode("utf-8")
