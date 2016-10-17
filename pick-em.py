import pandas as pd
import pulp
import numpy as np

# used in the dataframe later,
def weigh(x):
    if x != 0.0: return np.log(x)
    else: return -1000000000000

# also used in the dataframe later.
def dual(x):
    if x != 0: return np.log(1 - x)
    else: return -100000000000

def kkey(x):
    if x[0]== "_": return int(x[-1])
    else: return int(x)

# teams go on bye weeks. this needs to be checked so that i can deal with it later.
MASTER_NAMES_LIST = ['OAK', 'ARI', 'CHI', 'CIN', 'DEN', 'HOU',
                     'MIN', 'NO', 'PIT', 'SD', 'WSH', 'NYJ', 'ATL', 'SEA', 'DAL',
                     'BAL', 'KC', 'MIA', 'DET', 'CLE', 'TEN', 'IND', 'JAX', 'TB',
                     'BUF', 'CAR', 'PHI', 'SF', 'LA', 'GB', 'NYG', 'NE']

# going to have to fill up a list on a per-week basis, then concat.
data_frame_list = []

# making the csv for each week is a ltitle bit tedious. All this baloney is to deal with the
# fact that it's really difficult to find free probability predictions for the nfl online.
for i in range(1, 18):
    filename = 'week{0}'.format(str(i))
    file = open(filename)
    # WHO NEEDS REGEX ANYWAY
    week_string = file.read().replace("     ", "\n")
    total_list = week_string.split("\n")
    total_list = [t for t in total_list if t != '' and len(t) < 6]

    names = []
    probs = []
    digits = '1234567890'

    for entry in total_list:
        if entry[0] in digits: probs.append(float(entry[:-1]) / 100.0)
        else: names.append(entry)


    week_dict = dict(zip(names, probs))
    for team in MASTER_NAMES_LIST:
        if team not in week_dict.keys():
            week_dict[team] = 0

    # print i, week_dict
    data_frame_list.append(pd.DataFrame(week_dict, index=[i]))

results = pd.concat(data_frame_list)

for team in results.columns.values.tolist():
    variables = []
    for i in range(1, 18):
        variables.append(pulp.LpVariable('{team}_week_{week}'.format(team=team, week=i), cat=pulp.LpBinary))
    results['{team}_var'.format(team=team, week=i)] = variables

# make the 'win' probability column
for team in MASTER_NAMES_LIST:
    results['{team}_WIN'.format(team=team)] = results[team].apply(lambda x: weigh(x))

# make the 'lose' probability column
for team in MASTER_NAMES_LIST:
    results['{team}_LOSE'.format(team=team)] = results[team].apply(lambda x: dual(x))

problem = pulp.LpProblem('WIN SOME PICKEEEEM', pulp.LpMaximize)

X = []
Y = []

for week in range(1, 18):
    temp = results[results.index == week]
    survive = pulp.LpAffineExpression([])
    die = pulp.LpAffineExpression([])
    for team in MASTER_NAMES_LIST:
        survive += temp['{team}_var'.format(team=team)] * temp['{team}_WIN'.format(team=team)]
        die += temp['{team}_var'.format(team=team)] * temp['{team}_LOSE'.format(team=team)]
    temp_x = pulp.LpVariable('W{0}'.format(week))
    X.append(temp_x)
    temp_y = pulp.LpVariable('L{0}'.format(week))
    Y.append(temp_y)
    # let W{i} be the probability (well, log-sum probability) that you win in week i
    problem += temp_x == survive
    # let L{i} be the probability (well, log-sum probability) that you lose in week i
    problem += temp_y == die
    # you must chose a team each week

for team in MASTER_NAMES_LIST:
    # you may only use each team once
    problem += pulp.lpSum(results['{team}_var'.format(team=team)]) <= 1

for i in range(1, 18):
    # you may only use one team per week
    problem += pulp.lpSum(results.transpose()[i][32:64]) == 1

# we're looking to maximize the expected value. This is how we do that:
optimize = pulp.LpAffineExpression([])

# i think that the sums of these logs is equivalent to maximizing the expected value in this case.
problem += pulp.lpSum(X)
problem.solve(pulp.GUROBI())

# Let's go ahead and actually get these things
results = [str(i) for i in problem.variables() if i.value() != 0 and i.name[0] not in 'LW']
results = sorted(results, key=lambda x: kkey(x[-2:]))
for team in results: print team

import pdb; pdb.set_trace()
