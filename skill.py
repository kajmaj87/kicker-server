import csv
import json
import argparse
import os
import sys

from trueskill import rate, TrueSkill, Rating


p = argparse.ArgumentParser(
    description="Converts raw csv input to a json with trueskill ratings"
)
p.add_argument("files", help="input files in csv format with raw scores", nargs="*")
p.add_argument("-o", "--output", help="output json with true skill ratings")

config = p.parse_args()


def rowToDict(row, ranks):
    result = {}
    result["date"] = row[0]
    result["groupA"] = {p: playerRank(p, ranks) for p in splitPlayers(row[1])}
    result["groupB"] = {p: playerRank(p, ranks) for p in splitPlayers(row[2])}
    result["result"] = row[3]
    return result


def splitPlayers(group):
    return group.split("-")


def playerRank(player, ranks):
    if player not in ranks:
        ranks[player] = Rating()
    return ranks[player]


def updateRanks(groups, ranks):
    for group in groups:
        for player, ranking in group.items():
            ranks[player] = ranking
    return ranks


def processRanks(match, ranks):
    if match["result"] == "win":
        return updateRanks(rate([match["groupA"], match["groupB"]]), ranks)
    if match["result"] == "loss":
        return updateRanks(rate([match["groupB"], match["groupA"]]), ranks)


def toRankObject(name, rating):
    return {
        "name": name,
        "rank": rating.mu - rating.sigma * 3,
        "mu": rating.mu,
        "sigma": rating.sigma,
    }


def processOneCsv(csvPath):
    with open(csvPath, newline="") as datafile:
        reader = csv.reader(datafile, delimiter=",")
        # skip header row
        next(reader, None)
        ranks = {}

        for match in reader:
            ranks = processRanks(rowToDict(match, ranks), ranks)

        result = []
        for k, v in sorted(
            ranks.items(), key=lambda item: 3 * item[1].sigma - item[1].mu
        ):
            result.append(toRankObject(k, v))
        return result


result = {}

for f in config.files:
    base = os.path.basename(f)
    name = os.path.splitext(base)[0]
    result[name] = processOneCsv(f)

if config.output is not None:
    with open(config.output, "w") as outputjson:
        json.dump(result, outputjson, indent=4)
else:
    json.dump(result, sys.stdout, indent=4)
