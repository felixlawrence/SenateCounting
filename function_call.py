import pandas as pd
from pandas import DataFrame

from sen_dis import sen_dis
from votes_for_party import party_vote
from votes_for_party import party_vote_adjusted
from votes_for_party import candidates_elected
from votes_for_party import frac_loss
from votes_for_party import final_party_count
from votes_for_party import final_party_count_to_list
from votes_for_party import total_election
from votes_for_party import group_setup
from votes_for_party import group_batch_from_list
from votes_for_party import group_batch_from_iterable
from votes_for_party import group_setup_from_list
import csv
import math
import copy
import gc

state_i = 0
# State List
ausst = []
ausst.append(['New South Wales','Victoria','Queensland','Western Australia','South Australia','Tasmania','Australian Capital Territory','Northern Territory'])
ausst.append(['NSW','VIC','QLD','WA','SA','TAS','ACT','NT'])
ausst.append([6,6,6,6,6,6,2,2])
## Source files.
# Preference flows for above the line votes sorted by party letter.
# Each row is of the form:
# Party Group , How Many Forms? , Preferences by ballot.
prefs = ausst[1][state_i] + '_Senate_Preferences.csv'
# List of Candidates for the Senate sorted by ballot position
cands = ausst[1][state_i] + '_Senate_Candidates.csv'
# A list of the letter Groups along with the
gpptv_data = pd.read_csv(ausst[1][state_i] + '_Groups_Parties_Votes.csv', header=None)

# Iterable type
primaries = [
    [1.89, 2.31],       #Liberal Democrats
    [0.05],             #No Carbon Tax Climate Sceptics
    [0.54, 0.66],       #Democratic Labour Party (DLP)
    [0.05],             #Senator Online (Internet Voting Bills/Issues)
    [0.05],             #Voluntary Euthanasia Party
    [0.01],             #
    [0.05],             #Help End Marijuana Prohibition (HEMP) Party
    [0.28],             #Carers Alliance
    [0.8, 1.8, 2.8],    #The Wikileaks Party
    [0.68],             #Rise Up Australia Party
    [0.03],             #Future Party
    [2.25, 2.75],       #Christian Democratic Party (Fred Nile Group)
    [27, 29, 31],       #Labor
    [0.9, 1.9, 3.1],    #Katter's Australian Party
    [0.05],             #Australian Voice
    [1.8, 2.2],         #Sex Party
    [1.197, 1.463],     #Australian Fishing and Lifestyle Party
    [8, 9, 10],         #The Greens
    [0.9, 1.9, 3.1],    #Palmer United Party
    [0.23],             #Building Australia Party
    [0.1],              #Uniting Australia Party
    [0.5],              #Stop The Greens
    [0.1],              #Smokers Rights
    [0.08],             #Bullet Train For Australia
    [39, 41, 43],       #Liberal
    [0.05],             #Australian Protectionist Party
    [0.65],             #Animal Justice Party
    [0.3],              #Australia First Party
    [0.06],             #Australian Independents
    [0.07],             #Drug Law Reform
    [0.05],             #Socialist Equality Party
    [0.6],              #Australian Democrats
    [0.02],             #
    [1.26, 1.54],       #Family First Party
    [0.1],              #Stable Population Party
    [2.88, 3.52],       #Shooters and Fishers
    [0.15],             #Stop CSG
    [0.13],             #The Australian Republicans
    [0.1],              #Socialist Alliance
    [0.09],             #Non-Custodial Parents Party (Equal Parenting)
    [0.5],              #Pirate Party
    [0.1],              #Secular Party of Australia
    [0.05],             #Australian Motoring Enthusiast Party
    [1.6, 2.8, 4],      #One Nation
]
product = 1
for elt in primaries:
    product = product * len(elt)
print product
# Regular type
#primaries = []
#primaries.append([2.31,0.21,0.75,0.07,0,0,0,0.28,0,0,0,1.94,34.54,0,0,1.77,0,9.69,0,0.26,0,0,0,0,40.95,0,0,0,0,0,0.09,0.68,0,0.94,0,2.33,0,0,0.56,0.09,0,0.1,0,2.3])
#primaries.append([2.31,0.21,0.75,0.07,0,0,0,0.28,0,0,0,1.94,34.54,0,0,1.77,0,9.69,0,0.26,0,0,0,0,40.95,0,0,0,0,0,0.09,0.68,0,0.94,0,2.33,0,0,0.56,0.09,0,0.1,0,4.3])

## Other Variables
no_of_electors = 100000; # For each state define number of electors

# Define the parameters to be passed into the function
# First is the number of people to be elected
# Second is the number of decimal places to take overflow to
# Third is verbose (or not) (1 for verbose, anything for not)
# Fourth is the state number. [From the list above]
# Fifth is the flag for Senate Style overflow (0) vs. Proportional Rep Overflow (1) vs. others?
parameters = [ausst[2][state_i],6,0,0,0]

# Run the election once, to set a baseline for our analysis.
vote_dictionary, name_dictionary, group_list, t_votes = group_setup(gpptv_data)
senate_array = []
senate_count = []
#for i in range(1):
#    vote_dictionary, name_dictionary, group_list, t_votes = group_setup(gpptv)
for i in range(100):#range(product):
    # Want to move the setup out of the loop
    vote_dictionary, name_dictionary, group_list, t_votes = group_setup_from_list(gpptv_data,group_batch_from_iterable(primaries,i))
    (votes, vote_list_ticket_data,
        cand_to_group, final_state, output, quota, output_party, output_party2,
        fractional_loss, curr_elected, party_elected, party_elected_list
        ) = total_election(prefs,cands,ausst,no_of_electors,parameters,vote_dictionary,name_dictionary,group_list,t_votes)
    #print quota
    if sum(party_elected) < 6:
        print 'ERROR AT: ' + str(i)
    if party_elected in senate_array:
        state_i = senate_array.index(party_elected)
        senate_count[state_i] = senate_count[state_i] + 1
    else:
        senate_array.append(copy.deepcopy(party_elected))
        senate_count.append(1)
    if int(math.floor(i/100))*100 == int(i):
        print i

print senate_array
print senate_count
with open(ausst[1][state_i] + "_output.csv", "w") as text_file:
    for i in range(len(senate_count)):
        to_print = str(senate_count[i])
        for element in senate_array[i]: to_print = to_print + ',' + str(element)
        text_file.write('{0}\n'.format(to_print, end='\n'))
        print to_print
#####################################################################################################################
##### NOW THAT WE HAVE A BASELINE; WE NOW WANT TO RUN ANALYSIS FOR EVERY GROUP RUNNING AS TO HOW MUCH MORE VOTE #####
##### THEY NEED IN ORDER TO ELECT ONE MORE CANDIDATE THAN THEY CURRENTLY HAVE ELECTED                           #####
##### HOWEVER, WE ALSO WANT TO BE LOOKING FOR INTERESTING DILEMMAS; I.E. FOR CASES WHERE INCREASED VOTE LEADS   #####
##### TO DIFFERENT CANDIDATES BEING ELECTED FROM OTHER GROUPS                                                   #####
#####################################################################################################################

# For each party in party; check the amount of votes needed for something interesting to happen
# Simple algorithm; increase the number of votes one by one.
# Way to do this; copy the senate file and modify the entries, resave it and run the analysis.



# The construction array for the text we will display:
text_construction = []
text_construction.append(['heading1','Senate Results for ' + ausst[0][parameters[3]] + ' (' + ausst[1][parameters[3]] + ')'])
text_construction.append(['heading3','List of Elected Candidates'])
text_construction.append(['winarray',['Election Order','Party Name','Candidate']])
index2 = len(text_construction)-1
for line in output:
    if 'over' in line[0]:
        text_construction[index2].append([str(line[1]),str(name_dictionary[str(cand_to_group[line[2][0]][0])]),str(cand_to_group[line[2][0]][1])])
    elif 'last' in line[0]:
        for index in range(len(line[1])):
            text_construction[index2].append([str(line[1][index]),str(name_dictionary[str(cand_to_group[line[2][index]][0])]),str(cand_to_group[line[2][index]][1])])
text_construction.append(['heading2','Detailed Count and Distribution'])

# Man, how good is the O.C.
# I really hope someone error checks this and thinks about watching the O.C. season 1. I'm watching episode 4 right now.
# I miss the old days.
# Life was simpler.
# sigh.
# Back to work.

# Now we run the text analysis of the
allocation_round = 0
for line in output:
    # Begin the printing / output of the relevant data
    #print line
    allocation_round += 1
    if 'init' in line[0]:
        text_construction.append(['heading3', 'Round ' + str(allocation_round) + '. The initial allocation of votes is as follows:'])
        # Create the matrix of results.

    elif 'over' in line[0]:
        rand = 0
    elif 'last' in line[0]:
        for index in range(len(line[1])):
            rand = 0
    elif 'drop' in line[0]:
        rand = 0

    elif 'zero' in line[0]:
        allocation_round -= 1



#print text_construction

# Variables needed for the output:
allocation_round = 0
for line in output:
    # Begin the printing / output of the relevant data
    #print line
    allocation_round = allocation_round + 1
    if 'init' in line[0]:
        print 'Round: ' + str(allocation_round) + ' | Initial vote allocation'
    elif 'over' in line[0]:
        print 'Round: ' + str(allocation_round) + ' | Elected No. ' + str(line[1]) + ' | Group ' + str(cand_to_group[line[2][0]][0]) + ' | ' + str(name_dictionary[str(cand_to_group[line[2][0]][0])]) + ' | ' + str(cand_to_group[line[2][0]][1])
    elif 'last' in line[0]:
        for index in range(len(line[1])):
            print 'Round: ' + str(allocation_round) + ' | Elected No. ' + str(line[1][index]) + ' | Group ' + str(cand_to_group[line[2][index]][0]) + ' | ' + str(name_dictionary[str(cand_to_group[line[2][index]][0])]) + ' | ' + str(cand_to_group[line[2][index]][1])
    elif 'drop' in line[0]:
        print 'Round: ' + str(allocation_round) + ' | Excluded in place: ' + str(line[1]) + ' | Group ' + str(cand_to_group[line[2][0]][0]) + ' | ' + str(name_dictionary[str(cand_to_group[line[2][0]][0])]) + ' | ' + str(cand_to_group[line[2][0]][1])
        # There may be more than one candidate elected in this last overflow. So be sure to get it right.
    elif 'zero' in line[0]:
        allocation_round = allocation_round - 1
        print str(len(line[1])) + ' candidates eliminated with zero votes.'
