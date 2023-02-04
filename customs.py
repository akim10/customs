# yustoms data
import os
import json
import datetime
import csv
import copy

import pygsheets

path_to_json = 'filepath'

def getTotalTeamKills(totalStats, team):
  kills = 0
  for player in totalStats:
    if player["team"] == team:
      for stat in player:
        if stat == "championsKilled":
          kills += float(player[stat])
  return kills

def getTotalGameKills(totalStats):
  kills = 0
  for player in totalStats:
    for stat in player:
      if stat == "championsKilled":
        kills += float(player[stat])
  return kills

def sanitizeName(enemyPlayer):
  if "Sasuke" in enemyPlayer or enemyPlayer in ["REPORT YUNGLER", "free sasuke", "THEDixieKong", "Lmarichinesi", "JUGK0NG", "JUGKONG", "TheobaldoAgK", "canyons father"]:
    return "JUGKONG"
  elif "SUBWAY" in enemyPlayer or enemyPlayer in "Malfo":
    return "clafton"
  elif enemyPlayer.startswith("C") and enemyPlayer.endswith("zy"):
    return "Cozy"
  elif (enemyPlayer.startswith("K") and enemyPlayer.endswith("ra")) or enemyPlayer in ["Astxra"]:
    return "Kira"
  elif enemyPlayer.startswith("S") and enemyPlayer.endswith("ng"):
    return "Sting"
  elif enemyPlayer in ["BLINK3R", "Grumpression", "SearedFlask", "sonar current", "sukhyun"]:
    return "Grumpression"
  elif enemyPlayer in ["T1 Jintae", "Matt Park"]:
    return "Matt Park"
  elif enemyPlayer in ["niba", "supa", "beaster12345"]:
    return "supa"
  elif enemyPlayer in ["beeezbutz", "ASTROBOY69"]:
    return "beeezbutz"
  elif enemyPlayer in ["NatxXmH", "yellowcone"]:
    return "yellowcone"
  elif enemyPlayer in ["THEDiddyKong", "Dyllan Kim", "juwahn"]:
    return "THEDiddyKong"
  else:
    return enemyPlayer

championRates = {}
# {"championName": [number of picks, winrate]}

minTime = 99999999999
maxTime = 0

maxKills = 0
timeOfMaxKills = 0

blueSideWins = 0
redSideWins = 0

worstSingleGameKP = 100

gameDurations = []

def getPlayerList(game):
  playerList = []
  for stat in game:
    playerList.append(stat["name"])
  for i in range(len(playerList)):
    playerList[i] = sanitizeName(playerList[i])
  return playerList

gameData = {}
headToHeadList = {}

def updateDict(dict1, dict2):
  for key in dict2:
    if key not in dict1:
      dict1[key] = dict2[key]
  return copy.deepcopy(headToHeadList)

for file_name in [file for file in sorted(os.listdir(path_to_json)) if file.endswith('.json')]:
  with open(path_to_json + file_name) as json_file:
    data = json.load(json_file)

    # get each individual players' total stat dict
    totalStats = data["participants"]
    # create gameData and headToHead
    playerNames =  getPlayerList(totalStats)
    for player in playerNames:
        if player not in gameData:
            gameData[player] = {'assists': [], 'championsKilled': [], 'goldEarned': [], 'minionsKilled': [], 'neutralMinionsKilled': [], 'totalDamage':[],
                                'numDeaths': [], 'totalDamageDealtToChampions': [], 'visionScore': [],'visionScoreTotal': [], 'visionWardsBoughtInGame': [], 
                                'wardPlaced': [], 'KP': [], 'wins':0, 'losses':0, 'championsPlayed': [], 'rolesPlayed': [], 'headToHead': {}, 
                                'bestGame':[0,0,0,0,""], 'worstGame':[100,0,0,0,""], 'winList': [], 'KDAList':[[],[],[]], 'championWinrates':{}}

        if player not in headToHeadList:
            headToHeadList[player] = [0, 0, 0, 0]

    for player in playerNames:
        updateDict(gameData[player]["headToHead"], copy.deepcopy(headToHeadList))

    if totalStats[0]["win"] == "Win":
      blueSideWins += 1
    else:
      redSideWins += 1

    # get bloodiest game
    if getTotalGameKills(totalStats) > maxKills:
      maxKills = getTotalGameKills(totalStats)
      timeOfMaxKills = data["gameDuration"]
    # get shortest game
    if data["gameDuration"] < minTime:
      minTime = data["gameDuration"]
    # get longest game
    if data["gameDuration"] > maxTime:
      maxTime = data["gameDuration"]

    gameDurations.append(data["gameDuration"])
    playerList = getPlayerList(totalStats)

    for player in totalStats:
      sanitizedName = sanitizeName(player["name"])
      # for each individual player, get their individual stat values
      for stat in player:
        # skip name when adding to player stat arrays
        if stat not in ["name"]:


          if player["skin"] not in championRates:
            championRates[player["skin"]] = [0, []]

          # if the stat is tracked per minute
          if stat in ["minionsKilled", "goldEarned", "neutralMinionsKilled", "totalDamageDealtToChampions", "visionScore", "wardPlaced", "visionScoreTotal"]:
              if stat == "visionScore":
                gameData[sanitizedName]["visionScoreTotal"].append(float(player[stat]))
              if stat == "totalDamageDealtToChampions":
                gameData[sanitizedName]["totalDamage"].append(float(player[stat]))
              gameData[sanitizedName][stat].append(float(player[stat])/data["gameDuration"]*60000)

          # stats not tracked per minute (KDA)
          elif stat in ["championsKilled", "assists", "numDeaths", "visionWardsBoughtInGame"]:
              gameData[sanitizedName][stat].append(float(player[stat]))

          # W/L %
          elif stat == "win":
              if player["skin"] not in gameData[sanitizedName]["championWinrates"]:
                gameData[sanitizedName]["championWinrates"][player["skin"]] = [0, 0]
              if player["win"] == "Win":
                gameData[sanitizedName]["championWinrates"][player["skin"]][0] += 1
                # if they are in the second team, make wins/losses according to other team
                if playerList.index(sanitizedName) > 4:
                  for enemyPlayer in playerList[:5]:
                    gameData[sanitizedName]["headToHead"][enemyPlayer][0] += 1
                  for allyPlayer in playerList[5:]:
                    gameData[sanitizedName]["headToHead"][allyPlayer][2] += 1
                elif playerList.index(sanitizedName) < 5:
                  for enemyPlayer in playerList[5:]:
                    gameData[sanitizedName]["headToHead"][enemyPlayer][0] += 1
                  for allyPlayer in playerList[:5]:
                    gameData[sanitizedName]["headToHead"][allyPlayer][2] += 1
                gameData[sanitizedName]["wins"] += 1
                gameData[sanitizedName]["winList"].append(1)
                championRates[player["skin"]][1].append(1) # add to winList for this champion
              elif player["win"] == "Fail":
                gameData[sanitizedName]["championWinrates"][player["skin"]][1] += 1
                # if they are in the first team, make wins/losses according to other team
                if playerList.index(sanitizedName) > 4:
                  for enemyPlayer in playerList[:5]:
                    gameData[sanitizedName]["headToHead"][enemyPlayer][1] += 1
                  for allyPlayer in playerList[5:]:
                    gameData[sanitizedName]["headToHead"][allyPlayer][3] += 1
                elif playerList.index(sanitizedName) < 5:
                  for enemyPlayer in playerList[5:]:
                    gameData[sanitizedName]["headToHead"][enemyPlayer][1] += 1
                  for allyPlayer in playerList[:5]:
                    gameData[sanitizedName]["headToHead"][allyPlayer][3] += 1
                gameData[sanitizedName]["losses"] += 1
                gameData[sanitizedName]["winList"].append(0)
                championRates[player["skin"]][1].append(0) # add to winList for this champion

          # track unique champion picks
          elif stat == "skin":
              gameData[sanitizedName]["championsPlayed"].append(player["skin"])
              championRates[player["skin"]][0] += 1 # add to number of picks for this champion
          # track roles
          elif stat == "individualPosition":
              gameData[sanitizedName]["rolesPlayed"].append(player["individualPosition"])

          # KP% (stat == team)
          else:
            totalKills = getTotalTeamKills(totalStats, player["team"])
            gameData[sanitizedName]["KP"].append((float(player["championsKilled"]) + float(player["assists"])) / totalKills)
      gameKills = int(player["championsKilled"])
      gameDeaths = int(player["numDeaths"])
      gameAssists = int(player["assists"])
      gameData[sanitizedName]["KDAList"][0].append(gameKills)
      gameData[sanitizedName]["KDAList"][1].append(gameDeaths)
      gameData[sanitizedName]["KDAList"][2].append(gameAssists)
      if gameDeaths == 0:
        gameDeaths = 1
      gameKDA = (gameKills + gameAssists) / gameDeaths
      if gameKDA > gameData[sanitizedName]["bestGame"][0]:
        gameData[sanitizedName]["bestGame"][0] = gameKDA
        gameData[sanitizedName]["bestGame"][1] = player["championsKilled"]
        gameData[sanitizedName]["bestGame"][2] = player["numDeaths"]
        gameData[sanitizedName]["bestGame"][3] = player["assists"]
        gameData[sanitizedName]["bestGame"][4] = player["skin"]
      if gameKDA < gameData[sanitizedName]["worstGame"][0]:
        gameData[sanitizedName]["worstGame"][0] = gameKDA
        gameData[sanitizedName]["worstGame"][1] = player["championsKilled"]
        gameData[sanitizedName]["worstGame"][2] = player["numDeaths"]
        gameData[sanitizedName]["worstGame"][3] = player["assists"]
        gameData[sanitizedName]["worstGame"][4] = player["skin"]

def getLongestWinStreak(winList):
  streak = 0
  longestStreak = 0
  for outcome in winList:
    if outcome == 1:
      streak += 1
      if streak > longestStreak:
        longestStreak = streak
    else:
      streak = 0
  return longestStreak

def getLongestLossStreak(winList):
  streak = 0
  longestStreak = 0
  for outcome in winList:
    if outcome == 0:
      streak += 1
      if streak > longestStreak:
        longestStreak = streak
    else:
      streak = 0
  return longestStreak

def getWinrateOverTime(winList):
  winrateList = []
  for i in range(len(winList)):
    winrateList.append((winList[i]+winList[:i].count(1)) / (i+1))
  return winrateList

def getKDAOverTime(KDAList):
  KDARatioList = []
  for i in range(len(KDAList[0])):
    if KDAList[1][i] == 0 and sum(KDAList[1][:i+1]) == 0:
      KDARatioList.append((sum(KDAList[0][:i+1]) + sum(KDAList[2][:i+1])) / 1)
    else: 
      KDARatioList.append((sum(KDAList[0][:i+1]) + sum(KDAList[2][:i+1])) / sum(KDAList[1][:i+1]))
  return KDARatioList

def average(array):
  return sum(array) / len(array)

topDamage = 0
topDPM = 0
topDPMPlayer = ""
topDPMChampion = ""

topVS = 0
topVSM = 0
topVSMPlayer = ""

minVS = 1000
minVSM = 1000
minVSMPlayer = ""


topKills = 0
topKillsPlayer = ""

topDeaths = 0
topDeathsPlayer = ""

topAssists = 0
topAssistsPlayer = ""

topChampionPicks = 0
topChampionPicksPlayer = ""

bestSingleGameKDA = 0
bestSingleGameKills = 0
bestSingleGameDeaths = 0
bestSingleGameAssists = 0

worstSingleGameKDA = 100
worstSingleGameKills = 0
worstSingleGameDeaths = 0
worstSingleGameAssists = 0

def getWinrate(winList):
  if len(winList) == 0:
    return 0
  else:
    return winList.count(1) / len(winList)


for player in gameData:
  if gameData[player]["assists"] != []:
    for i in range(len(gameData[player]["championsKilled"])):
      zeroDeaths = False
      singleGameKills = gameData[player]["championsKilled"][i]
      singleGameDeaths = gameData[player]["numDeaths"][i]
      singleGameAssists = gameData[player]["assists"][i]
      singleGameChampion = gameData[player]["championsPlayed"][i]
      singleGamePlayer = player
      if singleGameDeaths == 0:
        singleGameDeaths = 1
        zeroDeaths = True
      singleGameKDA = (singleGameKills + singleGameAssists) / singleGameDeaths
      if singleGameKDA > bestSingleGameKDA:
        bestSingleGameKDA = singleGameKDA
        bestSingleGameKills = singleGameKills
        bestSingleGameAssists = singleGameAssists
        bestSingleGameDeaths = singleGameDeaths
        bestSingleGameChampion = singleGameChampion
        bestSingleGamePlayer = singleGamePlayer
        if zeroDeaths:
          bestSingleGameDeaths = 0
      if singleGameKDA <= worstSingleGameKDA:
        if singleGameKDA == 0 and worstSingleGameKDA == 0:
          if singleGameDeaths > worstSingleGameDeaths:
            worstSingleGameKDA = singleGameKDA
            worstSingleGameKills = singleGameKills
            worstSingleGameAssists = singleGameAssists
            worstSingleGameDeaths = singleGameDeaths
            worstSingleGameChampion = singleGameChampion
            worstSingleGamePlayer = singleGamePlayer
        else:
          worstSingleGameKDA = singleGameKDA
          worstSingleGameKills = singleGameKills
          worstSingleGameAssists = singleGameAssists
          worstSingleGameDeaths = singleGameDeaths
          worstSingleGameChampion = singleGameChampion
          worstSingleGamePlayer = singleGamePlayer

for player in gameData:
  if gameData[player]["assists"] != []:
    for stat in gameData[player]:
      if stat == "totalDamageDealtToChampions":
        if max(gameData[player][stat]) > topDPM:
          topDPM = max(gameData[player][stat])
          topDPMPlayer = player
          topDPMChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topDPM)]
          topDamage = max(gameData[player]["totalDamage"])
      elif stat == "visionScore":
        if max(gameData[player][stat]) > topVSM:
          topVSM = max(gameData[player][stat])
          topVSMPlayer = player
          topVSMChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topVSM)]
          topVS = max(gameData[player]["visionScoreTotal"])
          topVSPlayer = player
        if min(gameData[player][stat]) < minVSM: 
          minVSM = min(gameData[player][stat])
          minVSMPlayer = player
          minVSMChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(minVSM)]
          minVS = min(gameData[player]["visionScoreTotal"])
          minVSPlayer = player
      # elif stat == "visionScoreTotal":
      #   if max(gameData[player][stat]) > topVS:
      #     topVS = max(gameData[player][stat])
      #     topVSPlayer = player
      #   if min(gameData[player][stat]) < minVS: 
      #     minVS = min(gameData[player][stat])
      #     minVSPlayer = player
      elif stat == "championsKilled":
        if max(gameData[player][stat]) > topKills:
          topKills = max(gameData[player][stat])
          topKillsPlayer = player
          topKillsChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topKills)]
          topKillsDeaths = gameData[player]["numDeaths"][(gameData[player][stat]).index(topKills)]
          topKillsAssists = gameData[player]["assists"][(gameData[player][stat]).index(topKills)]
      elif stat == "numDeaths":
        if max(gameData[player][stat]) > topDeaths:
          topDeaths = max(gameData[player][stat])
          topDeathsPlayer = player
          topDeathsChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topDeaths)]
          topDeathsKills = gameData[player]["championsKilled"][(gameData[player][stat]).index(topDeaths)]
          topDeathsAssists = gameData[player]["assists"][(gameData[player][stat]).index(topDeaths)]
      elif stat == "assists":
        if max(gameData[player][stat]) > topAssists:
          topAssists = max(gameData[player][stat])
          topAssistsPlayer = player
          topAssistsChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topAssists)]
          topAssistsKills = gameData[player]["championsKilled"][(gameData[player][stat]).index(topAssists)]
          topAssistsDeaths = gameData[player]["numDeaths"][(gameData[player][stat]).index(topAssists)]
      elif stat == "":
        if max(gameData[player][stat]) > topAssists:
          topAssists = max(gameData[player][stat])
          topAssistsPlayer = player
          topAssistsChampion = gameData[player]["championsPlayed"][(gameData[player][stat]).index(topAssists)]
          topAssistsKills = gameData[player]["championsKilled"][(gameData[player][stat]).index(topAssists)]
          topAssistsDeaths = gameData[player]["numDeaths"][(gameData[player][stat]).index(topAssists)]

for player in gameData:
  # if the player has played at least one game
  # (if they have no empty stats, assists here is arbitrary)
  if gameData[player]["assists"] != []:
    for stat in gameData[player]:
      # average the stats that need to be averaged
      if stat not in ["championsPlayed", "wins", "losses", "headToHead", "rolesPlayed", "bestGame", "worstGame", "winList", "KDAList", "championWinrates"]:
        values = gameData[player][stat]
        average = sum(values)/float(len(values))
        gameData[player][stat] = average
      elif stat in ["championsPlayed"]:
        freq2 = {} 
        for item in gameData[player]["championsPlayed"]: 
            if (item in freq2): 
                freq2[item] += 1
            else: 
                freq2[item] = 1
        # print(freq)
        if len(freq2) >= topChampionPicks:
          topChampionPicks = len(freq2)
          topChampionPicksPlayer = player
          topChampionPicksList = freq2
        # gameData[player]["championsPlayed"] = freq

# print(championRates)

gc = pygsheets.authorize(client_secret='client_secret.json')

# Open spreadsheet and then worksheet
sh = gc.open('Customs Template')

# change title of sheet for new season
# open worksheet
wks = sh.worksheet('title','Season #')

# write header
# header = [["Player", "W", "L", "%", "# Games", "", "KDA Ratio", "Kills", "Deaths", "Assists", "", "Kill Participation %", "DMG/min", "CS/min", "Vision Score/min", "", "Best Game (KDA)", "Worst Game (KDA)",  "", "Longest Win Streak", "Longest Loss Streak", "", "Roles Played", "Champions Played"]]
header = [["Player", "W", "L", "%", "# Games", "", "KDA Ratio", "Kills", "Deaths", "Assists", "", "Kill Participation %", "DMG/min", "CS/min", "", "Vision Score/min", "Vision Score", "Vision Wards Purchased", "", "Best Game (KDA)", "Worst Game (KDA)", "", "Unique Picks", "Unique Pickrate"]]
wks.update_values('A1:Z1', header)

# start at row 2 (after header)
rowNumber = 2

# write stats player by player
coreData = []
for player in gameData:
    # print(gameData[player])
    row = []
    row.append(player)
    row.append(gameData[player]["wins"])
    row.append(gameData[player]["losses"])
    row.append(gameData[player]["wins"] / (gameData[player]["wins"] + gameData[player]["losses"]))
    row.append(gameData[player]["wins"] + gameData[player]["losses"])
    row.append("")
    row.append((gameData[player]["championsKilled"]+gameData[player]["assists"]) / gameData[player]["numDeaths"])
    row.append(gameData[player]["championsKilled"])
    row.append(gameData[player]["numDeaths"])
    row.append(gameData[player]["assists"])
    row.append("")
    row.append( str(round((gameData[player]["KP"])*100, 1)) +"%")
    row.append(gameData[player]["totalDamageDealtToChampions"])
    row.append(gameData[player]["minionsKilled"] + gameData[player]["neutralMinionsKilled"])
    row.append("")
    row.append(gameData[player]["visionScore"])
    row.append(gameData[player]["visionScoreTotal"])
    row.append(gameData[player]["visionWardsBoughtInGame"])
    row.append("")
    bestGameRow = "{}/{}/{} on {}".format(gameData[player]["bestGame"][1], gameData[player]["bestGame"][2], gameData[player]["bestGame"][3], gameData[player]["bestGame"][4])
    row.append( bestGameRow )
    worstGameRow = "{}/{}/{} on {}".format(gameData[player]["worstGame"][1], gameData[player]["worstGame"][2], gameData[player]["worstGame"][3], gameData[player]["worstGame"][4])
    row.append( worstGameRow )
    # row.append("")
    # row.append(getLongestWinStreak(gameData[player]["winList"]))
    # row.append(getLongestLossStreak(gameData[player]["winList"]))
    row.append("")

    freq1 = {}
    for item in gameData[player]["championsPlayed"]: 
        if (item in freq1): 
            freq1[item] += 1
        else: 
            freq1[item] = 1
    if "MonkeyKing" in freq1:
        freq1["Wukong"] = freq1.pop("MonkeyKing")

    marklist1 = sorted(freq1.items(), key=lambda x:x[1], reverse=True)
    sortdict1 = dict(marklist1)

    # row.append(str(sortdict1)[1:-1].replace("'", ""))
    # value = "{} picks in {} games".format(len(sortdict1), gameData[player]["wins"] + gameData[player]["losses"])
    # row.append(len(sortdict1))
    value = "{} picks in {} games".format(len(sortdict1), gameData[player]["wins"] + gameData[player]["losses"])
    row.append(value)
    row.append(len(sortdict1)/(gameData[player]["wins"] + gameData[player]["losses"]))

    # row.append("")
    # freq = {} 
    # for item in gameData[player]["rolesPlayed"]: 
    #     if (item in freq): 
    #         freq[item] += 1
    #     else: 
    #         freq[item] = 1

    # # sanitize role names
    # freq["Top"] = freq.pop("TOP", 0)
    # freq["Jungle"] = freq.pop("JUNGLE", 0)
    # freq["Mid"] = freq.pop("MIDDLE", 0)
    # freq["Bot"] = freq.pop("BOTTOM", 0)
    # freq["Sup"] = freq.pop("UTILITY", 0)

    # del_keys= []
    # for key, value in freq.items():
    #     if value == 0:
    #         del_keys.append(key)
    # for key in del_keys:
    #     freq.pop(key)

    # marklist = sorted(freq.items(), key=lambda x:x[1], reverse=True)
    # sortdict = dict(marklist)

    # row.append(str(sortdict)[1:-1].replace("'", ""))
    # print(row)
    # wks.update_values('A'+str(rowNumber)+':S'+str(rowNumber), [row])
    rowNumber += 1
    coreData.append(row)

wks.update_values('A2:Z99', coreData)

wks.sort_range("A2", "Z99", 4, "DESCENDING")
wks.sort_range("A2", "Z99", 3, "DESCENDING")
print("stats updated")
print("")
print("")

# open worksheet
wks = sh.worksheet('title','Season # fun facts')

factsData = []

value = "{}/{}/{} by {} on {}".format(int(bestSingleGameKills), int(bestSingleGameDeaths), int(bestSingleGameAssists), bestSingleGamePlayer, bestSingleGameChampion)
row = ["Best KDA", value]
factsData.append(row)
print(row)
value = "{}/{}/{} by {} on {}".format(int(worstSingleGameKills), int(worstSingleGameDeaths), int(worstSingleGameAssists), worstSingleGamePlayer, worstSingleGameChampion)
row = ["Worst KDA", value]
factsData.append(row)
print(row)

row = ["", ""]
factsData.append(row)
print(row)

value = "{}/{}/{} by {} on {}".format(int(topKills), int(topKillsDeaths), int(topKillsAssists), topKillsPlayer, topKillsChampion)
row = ["Top kills", value]
factsData.append(row)
print(row)
value = "{}/{}/{} by {} on {}".format(int(topDeathsKills), int(topDeaths), int(topDeathsAssists), topDeathsPlayer, topDeathsChampion)
row = ["Top deaths", value]
factsData.append(row)
print(row)
value = "{}/{}/{} by {} on {}".format(int(topAssistsKills), int(topAssistsDeaths), int(topAssists), topAssistsPlayer, topAssistsChampion)
row = ["Top assists", value]
factsData.append(row)
print(row)

row = ["", ""]
factsData.append(row)
print(row)


# value = "{} by {} on {} ({} in {})".format(int(topDPM), topDPMPlayer, topDPMChampion, int(topDamage), topDamageDuration)
# row = ["Top Damage %", value]
# factsData.append(row)
# print(row)
topDamageDuration = str(datetime.timedelta(minutes=(topDamage/topDPM)))[2:7]
value = "{} by {} on {} ({} in {})".format(int(topDPM), topDPMPlayer, topDPMChampion, int(topDamage), topDamageDuration)
row = ["Top DPM", value]
factsData.append(row)
print(row)
topVSMDuration = str(datetime.timedelta(minutes=(topVS/topVSM)))[2:7]
value = "{} by {} on {} ({} in {})".format(str(topVSM)[:4], topVSMPlayer, topVSMChampion, int(topVS), topVSMDuration)
row = ["Top VSM", value]
factsData.append(row)
print(row)
minVSMDuration = str(datetime.timedelta(minutes=minVS/minVSM))[2:7]
value = "{} by {} on {} ({} in {})".format(str(minVSM)[:4], minVSMPlayer, minVSMChampion, int(minVS), minVSMDuration)
row = ["Min VSM", value]
factsData.append(row)
print(row)

row = ["", ""]
factsData.append(row)
print(row)

# longest win and loss streak

# maxWinStreak = 0
# maxWinStreakPlayer = ""
# maxLossStreak = 0
# maxLossStreakPlayer = ""
# for player in gameData:
#   if getLongestWinStreak(gameData[player]["winList"]) >= maxWinStreak:
#     maxWinStreak = getLongestWinStreak(gameData[player]["winList"])
#     maxWinStreakPlayer = player
#   if getLongestLossStreak(gameData[player]["winList"]) >= maxLossStreak:
#     maxLossStreak = getLongestLossStreak(gameData[player]["winList"])
#     maxLossStreakPlayer = player

# value = "{} by {}".format(maxWinStreak, maxWinStreakPlayer)
# row = ["Longest win streak", value]
# factsData.append(row)
# print(row)
# value = "{} by {}".format(maxLossStreak, maxLossStreakPlayer)
# row = ["Longest loss streak", value]
# factsData.append(row)
# print(row)

# row = ["", ""]
# factsData.append(row)
# print(row)

if "MonkeyKing" in topChampionPicksList:
    topChampionPicksList["Wukong"] = topChampionPicksList.pop("MonkeyKing")

marklist2 = sorted(topChampionPicksList.items(), key=lambda x:x[1], reverse=True)
sortdict2 = dict(marklist2)

value = "{} picks by {}".format(topChampionPicks, topChampionPicksPlayer)
row = ["Most unique picks", value]
factsData.append(row)
print(row)
row = ["", str(sortdict2)[1:-1].replace("'", "")]
factsData.append(row)
print(row)

row = ["", ""]
factsData.append(row)
print(row)

row = ["Longest game", str(datetime.timedelta(milliseconds=maxTime))[2:7]]
factsData.append(row)
print(row)
row = ["Shortest game", str(datetime.timedelta(milliseconds=minTime))[2:7]]
factsData.append(row)
print(row)
value = "{} kills in {}".format(int(maxKills), str(datetime.timedelta(milliseconds=timeOfMaxKills))[2:7])
row = ["Bloodiest game", value]
factsData.append(row)
print(row)

row = ["", ""]
factsData.append(row)
print(row)

value = "{}% ({})".format(   round(blueSideWins / (blueSideWins + redSideWins)*100, 2)   , blueSideWins)
row = ["Blue side winrate", value]
factsData.append(row)
print(row)
value = "{}% ({})".format(      round(redSideWins / (blueSideWins + redSideWins)*100, 2)   , redSideWins)
row = ["Red side winrate", value]
factsData.append(row)
print(row)
value = blueSideWins + redSideWins
row = ["Total games played", value]
factsData.append(row)
print(row)

# print(factsData)
wks.update_values('A1:B99', factsData)

print("fun facts updated")
print("")
print("")

# open worksheet
wks = sh.worksheet('title','Season # champion data')

wks.frozen_rows = 1

# write header
header = [["Champion", "W", "L", "%", "# of Picks"]]
wks.update_values('A1:E1', header)
championCol = list(championRates.keys())
picksAndRates = list(championRates.values())
picksCol = []
winsCol = []
lossesCol = []
ratesCol = []
for valuePair in picksAndRates:
  picksCol.append(valuePair[0])
  winsCol.append(valuePair[1].count(1))
  lossesCol.append(valuePair[1].count(0))

for champion in championRates:
  championRates[champion][1] = getWinrate(championRates[champion][1])

for valuePair in picksAndRates:
  ratesCol.append(valuePair[1])

wks.update_values(  'A2:E199', list    (map     (list,    zip(*[championCol, winsCol, lossesCol, ratesCol, picksCol])   )     )    )
wks.sort_range("A2", "E199", 4, "DESCENDING")

print("champion data updated")
print("")
print("")

# Open h2h spreadsheet
sh = gc.open('Head to Head Template')
# wks = sh.worksheet('title','data')
# header = [["player", "game", "win rate", "KDA"]]

# start at row 2 (after header)
rowNumber = 2
columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'av', 'aw', 'ax', 'ay', 'az', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bk', 'bl', 'bm', 'bn', 'bo', 'bp', 'bq', 'br', 'bs', 'bt', 'bu', 'bv', 'bw', 'bx', 'by', 'bz', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'cg', 'ch', 'ci', 'cj', 'ck', 'cl', 'cm', 'cn', 'co', 'cp', 'cq', 'cr', 'cs', 'ct', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'da', 'db', 'dc', 'dd', 'de', 'df', 'dg', 'dh', 'di', 'dj', 'dk', 'dl', 'dm', 'dn', 'do', 'dp', 'dq', 'dr', 'ds', 'dt', 'du', 'dv', 'dw', 'dx', 'dy', 'dz']
i = 0
# k=1
for player in gameData:
  updateDict(gameData[player]["headToHead"], headToHeadList)

sorted_gameData = dict(  sorted( gameData.items(), key=lambda x: x[0].lower())  )


# # write stats player by player
# for player in sorted_gameData:
#   columnLetters = [columns[i], columns[i+3]]
#   playerCol = [player]*len(gameData[player]["winList"])
#   gameCol = list(range(1,len(gameData[player]["winList"])+1))
#   winrateCol = getWinrateOverTime(gameData[player]["winList"])
#   KDACol = getKDAOverTime(gameData[player]["KDAList"])
#   wks.update_values(str(columnLetters[0])+ '1:'+ str(columnLetters[1]) +'99', list(map(list, zip(*[playerCol, gameCol, winrateCol, KDACol]))))
#   i += 4

#   # wks.add_chart(  (columns[k] + "1", columns[k] + "99")  ,  [(columns[k+1] + "1", columns[k+1] + "99")]  , "Winrate Over Time", pygsheets.ChartType.LINE, "J2")
#   # wks.add_chart(  (columns[k] + "1", columns[k] + "99")  ,  [(columns[k+2] + "1", columns[k+2] + "99")]  , "KDA Over Time", pygsheets.ChartType.LINE, "J16")
#   break
#   k += 4


# write stats player by player
data = []


for player in sorted_gameData:
    try:
      # go to this player's sheet
      wks = sh.worksheet('title', player)
    except pygsheets.WorksheetNotFound as error:
      # create sheet for player if it doesn't exist yet
      sh.add_worksheet(player)
      wks = sh.worksheet('title', player)
      wks.adjust_column_width(1, 1, 130)
      wks.frozen_rows = 1
  
      # write header
      header = [["Player", "Wins with", "Losses with", "Winrate with", "", "Wins vs", "Losses vs", "Winrate vs"]]
      wks.update_values('A1:H1', header)

      model_cell = wks.cell('A2').set_text_format('fontFamily', "Roboto")
      pygsheets.DataRange('A1', 'H99' , worksheet = wks).apply_format(model_cell)

      # format header and columns
      wks.cell('A1').set_text_format('bold', True)
      model_cell2 = wks.cell('B1')
      model_cell2.set_text_format('bold', True)
      model_cell2.set_horizontal_alignment(pygsheets.custom_types.HorizontalAlignment.RIGHT)
      pygsheets.DataRange('B1','H1', worksheet=wks).apply_format(model_cell2)

      model_cell3 = wks.cell('D2')
      model_cell3.set_number_format(format_type = pygsheets.FormatType.PERCENT, pattern = "0.00%")
      pygsheets.DataRange('D2', 'D99' , worksheet = wks).apply_format(model_cell3)
      pygsheets.DataRange('H2', 'H99' , worksheet = wks).apply_format(model_cell3)

      # gray_cell = pygsheets.Cell("A3")
      # gray_cell.color = (0.95, 0.95, 0.95, 0)

      # for r in range(3, 40, 2):
      #   wks.get_row(r, returnas = "range").apply_format(gray_cell)

      # for i in range(3, 40, 2):
      #   wks.cell('D'+str(i)).set_number_format(format_type = pygsheets.FormatType.PERCENT, pattern = "0.00%")
      #   wks.cell('H'+str(i)).set_number_format(format_type = pygsheets.FormatType.PERCENT, pattern = "0.00%")

    # wks = sh.worksheet('title', player)
    print(player)
    # print(gameData[player]["headToHead"])
    # print("")

    # start at row 2 (after header)
    rowNumber = 2
    data = []
    for otherPlayer in sorted_gameData:
      if otherPlayer != player:
        row = []
        row.append(otherPlayer)
        row.append(gameData[player]["headToHead"][otherPlayer][2])
        row.append(gameData[player]["headToHead"][otherPlayer][3])
        if (gameData[player]["headToHead"][otherPlayer][2] + gameData[player]["headToHead"][otherPlayer][3]) == 0:
          row.append(0)
        else:
          row.append(gameData[player]["headToHead"][otherPlayer][2] / (gameData[player]["headToHead"][otherPlayer][2] + gameData[player]["headToHead"][otherPlayer][3]) )
        row.append("")
        row.append(gameData[player]["headToHead"][otherPlayer][0])
        row.append(gameData[player]["headToHead"][otherPlayer][1])
        if (gameData[player]["headToHead"][otherPlayer][0] + gameData[player]["headToHead"][otherPlayer][1]) == 0:
          row.append(0)
        else:
          row.append(gameData[player]["headToHead"][otherPlayer][0] / (gameData[player]["headToHead"][otherPlayer][0] + gameData[player]["headToHead"][otherPlayer][1]) )
        data.append(row)
    data.append(["", "", "", "", "", "", "", "", "", "", ])
    data.append(["", "", "", "", "", "", "", "", "", "", ])
    data.append(["", "", "", "", "", "", "", "", "", "", ])
    data.append(["", "", "", "", "", "", "", "", "", "", ])
    wks.update_values('A2:Y99', data)

print("head to head updated")
print("")
print("")









# Open charts spreadsheet
sh = gc.open('Individual Picks Template')
# start at row 2 (after header)
rowNumber = 2
i = 0
for player in gameData:
  updateDict(gameData[player]["headToHead"], headToHeadList)

sorted_gameData = dict(  sorted( gameData.items(), key=lambda x: x[0].lower())  )

for player in sorted_gameData:
    try:
      # go to this player's sheet
      wks = sh.worksheet('title', player)
    except pygsheets.WorksheetNotFound as error:
      # create sheet for player if it doesn't exist yet
      sh.add_worksheet(player)
      wks = sh.worksheet('title', player)
      # wks.adjust_column_width(1, 1, 60)
      wks.adjust_column_width(5, 1, 60)
      wks.frozen_rows = 1
  
      # write header
      header = [["Champion", "# of Picks", "Record", "Winrate"]]
      wks.update_values('A1:H1', header)

      model_cell = wks.cell('A2').set_text_format('fontFamily', "Roboto")
      pygsheets.DataRange('A1', 'H99' , worksheet = wks).apply_format(model_cell)

      formatChartCell = wks.cell('B99')
      # formatChartCell.set_value(1)
      # formatChartCell.set_text_format('foregroundColor', (255,255,255, 1))
      
      # format header and columns
      wks.cell('A1').set_text_format('bold', True)
      model_cell0 = wks.cell('A2')
      model_cell0.set_horizontal_alignment(pygsheets.custom_types.HorizontalAlignment.LEFT)
      pygsheets.DataRange('A2','A99', worksheet=wks).apply_format(model_cell0)
      model_cell3 = wks.cell('C1')
      model_cell3.set_horizontal_alignment(pygsheets.custom_types.HorizontalAlignment.RIGHT)
      pygsheets.DataRange('C1','D99', worksheet=wks).apply_format(model_cell3)

      model_cell4 = wks.cell('D2')
      model_cell4.set_number_format(format_type = pygsheets.FormatType.PERCENT, pattern = "0.00%")
      pygsheets.DataRange('D2','D99', worksheet=wks).apply_format(model_cell4)
      model_cell2 = wks.cell('B1')
      model_cell2.set_text_format('bold', True)
      model_cell2.set_horizontal_alignment(pygsheets.custom_types.HorizontalAlignment.RIGHT)
      pygsheets.DataRange('B1','H1', worksheet=wks).apply_format(model_cell2)


    championsPlayedChartData = {}

    for item in gameData[player]["championsPlayed"]:
        if (item in championsPlayedChartData): 
            championsPlayedChartData[item] += 1
        else: 
            championsPlayedChartData[item] = 1

    # print(championsPlayedChartData)
    marklist2 = sorted(championsPlayedChartData.items(), key=lambda x:x[1], reverse=True)
    championDict = dict(marklist2)
    # print(marklist2)


    championsWinratesList = list(gameData[player]["championWinrates"].values())
    championsWinratesListNames =list(gameData[player]["championWinrates"].keys())
    for i in range(len(championsWinratesList)):
      listWins = championsWinratesList[i][0]
      listLosses = championsWinratesList[i][1]
      championsWinratesList[i] = [[championsWinratesListNames[i], str(listWins) + " - " + str(listLosses), listWins/(listWins+listLosses)], 0  ]


    for championPlayedName in championsPlayedChartData:
      for championWinrateName in championsWinratesList:
        if championPlayedName == championWinrateName[0][0]:
          championWinrateName[1] = championsPlayedChartData[championPlayedName]


    marklist2 = sorted(  [item for item in championsWinratesList]  , key=lambda x:x[1], reverse=True)

    rolesPlayedChartData = {} 
    for item in gameData[player]["rolesPlayed"]: 
        if (item in rolesPlayedChartData): 
            rolesPlayedChartData[item] += 1
        else: 
            rolesPlayedChartData[item] = 1

    # sanitize role names
    rolesPlayedChartData["Top"] = rolesPlayedChartData.pop("TOP", 0)
    rolesPlayedChartData["Jungle"] = rolesPlayedChartData.pop("JUNGLE", 0)
    rolesPlayedChartData["Mid"] = rolesPlayedChartData.pop("MIDDLE", 0)
    rolesPlayedChartData["Bot"] = rolesPlayedChartData.pop("BOTTOM", 0)
    rolesPlayedChartData["Sup"] = rolesPlayedChartData.pop("UTILITY", 0)

    del_keys1 = []
    for key, value in rolesPlayedChartData.items():
        if value == 0:
            del_keys1.append(key)
    for key in del_keys1:
        rolesPlayedChartData.pop(key)

    marklist3 = sorted(rolesPlayedChartData.items(), key=lambda x:x[1], reverse=True)
    rolesDict = dict(marklist3)

    for role in ["Top", "Jungle", "Mid", "Bot", "Sup"]:
      if role not in rolesDict:
        rolesDict[role] = 0

    # print(gameData[player]["winList"])
    # start at row 2 (after header)
    rowNumber = 2
    data = []
    gameCol = list(range(1,len(gameData[player]["winList"])+1))
    winrateCol = getWinrateOverTime(gameData[player]["winList"])
    # print(winrateCol)
    KDACol = getKDAOverTime(gameData[player]["KDAList"])



    # wks.update_values(  'A2:C99', list    (map     (list,    zip(*[gameCol, winrateCol, KDACol])   )     )    )
    # wks.add_chart(  ("A1", "A99")  ,  [("B1", "B99")]  , "Winrate Over Time", pygsheets.ChartType.LINE, "E2")
    # wks.add_chart(  ("A1", "A99")  ,  [("C1", "C99")]  , "KDA Over Time", pygsheets.ChartType.LINE, "E20")
    wks.update_values(  'A2:D99', list    (map     (list,    zip(*   [[item[0][0] for item in marklist2],    [item[1] for item in marklist2], [item[0][1] for item in marklist2] , [item[0][2] for item in marklist2]     ])   )     )    )
    wks.add_chart(  ("A2", "A99")  ,  [("B2", "B99")]  , "Champion Picks", pygsheets.ChartType.BAR, "F2")

    print(player)


