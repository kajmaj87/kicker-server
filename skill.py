import csv
import json
import argparse
from trueskill import rate, TrueSkill, Rating


p = argparse.ArgumentParser(
    description="Converts raw csv input to a json with trueskill ratings"
)
p.add_argument("-i", "--input", help="input csv with raw scores", required=True)
p.add_argument("-o", "--output", help="output json with true skill ratings")

config = p.parse_args()

ranks = {}


def rowToDict(row):
    result = {}
    result["date"] = row[0]
    result["groupA"] = {p: playerRank(p) for p in splitPlayers(row[1])}
    result["groupB"] = {p: playerRank(p) for p in splitPlayers(row[2])}
    result["result"] = row[3]
    return result


def splitPlayers(group):
    return group.split("-")


def playerRank(player):
    global ranks
    if player not in ranks:
        ranks[player] = Rating()
    return ranks[player]


def updateRanks(groups):
    global ranks
    for group in groups:
        for player, ranking in group.items():
            ranks[player] = ranking


def processRanks(match):
    if match["result"] == "win":
        updateRanks(rate([match["groupA"], match["groupB"]]))
    if match["result"] == "loss":
        updateRanks(rate([match["groupB"], match["groupA"]]))


def toRankObject(name, rating):
    return {
        "name": name,
        "rank": rating.mu - rating.sigma * 3,
        "mu": rating.mu,
        "sigma": rating.sigma,
    }


with open(config.input, newline="") as datafile:
    reader = csv.reader(datafile, delimiter=",")
    # skip header row
    next(reader, None)
    matches = [processRanks(rowToDict(match)) for match in reader]
    result = []
    for k, v in sorted(ranks.items(), key=lambda item: 3 * item[1].sigma - item[1].mu):
        result.append(toRankObject(k, v))

    if config.output is not None:
        with open(config.output, "w") as outputjson:
            json.dump({"rankings": result}, outputjson, indent=4)
    else:
        print(result)
