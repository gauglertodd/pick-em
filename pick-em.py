import pandas as pd
import pulp
import numpy as np


def weigh(x):
    if x!=0.0: return np.log(x)
    else: return -1000000000000

def dual(x):
    if x!=0: return np.log(1-x)
    else: return -100000000000

# teams go on bye weeks. this needs to be checked so that i can deal with it later.
MASTER_NAMES_LIST = ['OAK', 'ARI', 'CHI', 'CIN', 'DEN', 'HOU',
'MIN', 'NO', 'PIT', 'SD', 'WSH', 'NYJ', 'ATL', 'SEA', 'DAL',
'BAL', 'KC', 'MIA', 'DET', 'CLE', 'TEN', 'IND', 'JAX', 'TB',
'BUF', 'CAR', 'PHI', 'SF', 'LA', 'GB', 'NYG', 'NE']

# going to have to fill up a list on a per-week basis, then concat.
data_frame_list = []

# making the csv for each week is a ltitle bit tedious....
for i in range(1,18):
    filename = 'week{0}'.format(str(i))
    file = open(filename)
    # WHO NEEDS REGEX ANYWAY
    week_string = file.read().replace("     ","\n")
    total_list = week_string.split("\n")
    total_list = [t for t in total_list if t != '' and len(t) < 6]

    names =[]
    probs =[]
    digits = '1234567890'

    for entry in total_list:
        if entry[0] in digits: probs.append(float(entry[:-1])/100.0)
        else: names.append(entry)

    # print len(names)
    # print len(probs)
    # print probs
    # print names
    week_dict = dict(zip(names,probs))
    for team in MASTER_NAMES_LIST:
        if team not in week_dict.keys():
            week_dict[team]=0

    # print i, week_dict
    data_frame_list.append(pd.DataFrame(week_dict, index =[i]))

results = pd.concat(data_frame_list)

lp_variables = pd.DataFrame([])

for team in results.columns.values.tolist():
    variables = []
    for i in range(1,18):
        variables.append(pulp.LpVariable('{team}_week_{week}'.format(team=team, week=i), cat=pulp.LpBinary))
    results['{team}_var'.format(team=team, week=i)] = variables


for team in MASTER_NAMES_LIST:
    results['{team}_WIN'.format(team=team)] = results[team].apply(lambda x: weigh(x))

for team in MASTER_NAMES_LIST:
    results['{team}_LOSE'.format(team=team)] = results[team].apply(lambda x: dual(x))

# keep everything in the same frame, it'll be fine...
trans = results.transpose()


problem = pulp.LpProblem('WIN SOME PICKEEEEM', pulp.LpMaximize)

X = []
Y = []

for week in range(1,18):
    temp = results[results.index == week]
    survive = pulp.LpAffineExpression([])
    die = pulp.LpAffineExpression([])
    for team in MASTER_NAMES_LIST:
        survive += temp['{team}_var'.format(team=team)] * temp['{team}_WIN'.format(team=team)]
        die += temp['{team}_var'.format(team=team)] * temp['{team}_LOSE'.format(team=team)]
    temp_x = pulp.LpVariable('W{0}'.format(week), lowBound=0, upBound=1, cat='Continuous')
    X.append(temp_x)
    temp_y = pulp.LpVariable('L{0}'.format(week), lowBound=0, upBound=1)
    Y.append(temp_y)
    # let W{i} be the probability (well, log-sum probability) that you win in week i
    problem += temp_x == survive
    # let L{i} be the probability (well, log-sum probability) that you lose in week i
    problem += temp_y == die
    # you must chose a team each week
    problem += survive != 0

for team in MASTER_NAMES_LIST:
    # you may only use each team once
    problem += pulp.lpSum(results['{team}_var'.format(team=team)]) <= 1

for i in range(1,18):
    # you may only use one team per week
    problem += pulp.lpSum(results.transpose()[i][32:64]) <= 1


# we're looking to maximize the expected value. This is how we do that:
optimize = pulp.LpAffineExpression([])

# this is the expression for the expected number of weeks you last.
for i in range(2,17):
    optimize += (i-1)*pulp.lpSum(X[:i-1]) + (i-1)* Y[i]
optimize += 17 * pulp.lpSum(X)

problem += optimize

problem.solve(pulp.GUROBI())

import pdb; pdb.set_trace()

# problem = pulp.LpProblem('WIN SOME PICKEEEEM', pulp.LpMaximize)


# # creating the variables; integer type with upper bound = number of available units.
# overall_df['Variable'] = overall_df.apply(lambda row: pulp.LpVariable('x{0}'.format(row.name),
#                                                                       lowBound=0,
#                                                                       upBound=row['units'],
#                                                                       cat='Integer'), axis=1)

# # adding the expression that gives us the predicted quantity of impressions.
# # overall_df['Variables_With_Coefficients'] = overall_df.apply(lambda row: row['prediction'] * row['Variable'], axis=1)
# overall_df['Variables_With_Coefficients'] = overall_df.apply(lambda row: row['prediction'] *
#                                                              row['Variable'] *
#                                                              get_prop(file_id, row['reservedby'], intersection_df), axis=1)

# # adding a cost expression
# overall_df['Campaign_Cost'] = overall_df.apply(lambda row: row['Variable'] * row['price'], axis=1)

# # the expected impressions must meet the impression goal
# problem += pulp.lpSum(overall_df['Variables_With_Coefficients'].tolist()) >= impression_goal

# # the problem should minimize the expected cost, while still managing to meet an impression goal.
# problem += pulp.lpSum(overall_df['Campaign_Cost'].tolist()) <= budget

# # this is the total number of units used.
# problem += pulp.lpSum(overall_df['Variable'].tolist())

# # solve the problem.
# problem.solve(pulp.GUROBI())
















