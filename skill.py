import csv
from trueskill import rate, TrueSkill, Rating

ranks = {}


def rowToDict(row):
    result = {}
    result['date'] = row[0]
    result['groupA'] = {p:playerRank(p) for p in splitPlayers(row[1])}
    result['groupB'] = {p:playerRank(p) for p in splitPlayers(row[2])}
    result['result'] = row[3]
    return result


def splitPlayers(group):
    return group.split('-')


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
    if match['result'] == 'win':
        updateRanks(rate([match['groupA'], match['groupB']]))
    if match['result'] == 'loss':
        updateRanks(rate([match['groupB'], match['groupA']]))

def toRankObject(rating):
    return {
        'name': rating.key,
        'rank': rating.rating.mu - rating.rating.sigma*3,
        'mu': rating.rating.mu,
        'sigma': rating.rating.sigma
    }

with open('data/history.csv', newline='') as datafile:
    reader = csv.reader(datafile, delimiter=',')
    # skip header row
    next(reader, None)
    matches = [processRanks(rowToDict(match)) for match in reader]
    print({p: rating for p, rating in sorted(ranks.items(), key=lambda item: item[1].mu - 3*item[1].sigma)})
