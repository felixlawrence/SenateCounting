from sen_dis import sen_dis
import csv
import math
import copy

## Source files.
# Preference flows for above the line votes sorted by party letter.
# Each row is of the form:
# Party Group , How Many Forms? , Preferences by ballot. 
prefs = 'NSW_Senate_Preferences.csv'
# List of Candidates for the Senate sorted by ballot position
cands = 'NSW_Senate_Candidates.csv'
# A list of the letter Groups along with the
gpptv = 'NSW_Groups_Parties_Votes.csv'


# Create a dictionary of votes for all of the groups that have GVTs
no_of_electors = 1000; # For each state define number of electors
vote_dictionary = {}
t_votes = 0
with open(gpptv,'rb') as csvfile:
    spamreader = csv.reader(csvfile,delimiter=',')
    temp1 = 0
    for row in spamreader:
        t_votes = float(float(t_votes) + float(row[2].strip()))
        vote_dictionary[row[0].strip()] = row[2].strip()
        temp1 = temp1 + 1
        
# Create the vote list to pass into the algorithm; appending all of
# the preference data.
votes = []
with open(prefs,'rb') as csvfile:
    spamreader = csv.reader(csvfile,delimiter=',')
    temp1 = 0
    for row in spamreader:
        no_of_votes = int(math.floor(float(float(float(vote_dictionary[row[0].strip()]) / float(row[1])) * float(no_of_electors) / float(t_votes))))
        print no_of_votes
        votes.append([[],no_of_votes])
        temp2 = 2
        while temp2 < len(row):
            votes[temp1][0].append(int(row[temp2]))
            temp2 = temp2 + 1
        temp1 = temp1 + 1
        
# Define the parameters to be passed into the function
# First is the number of people to be elected
# Second is the number of decimal places to take overflow to
parameters = [6,6]

# Run the election
final_state = sen_dis(votes,parameters)

# Working out the fractional vote loss, and printing each vote round.
fractional_vote_loss = 0
for vote_round in final_state.historical_votes_cand:
    #print vote_round
    candidate = 0
    fractional_vote_loss = 0
    while candidate < len(vote_round[0]):
        if vote_round[0][candidate] >= final_state.quota and vote_round[0][candidate] <= final_state.quota + 0.1:
            fractional_vote_loss = fractional_vote_loss + vote_round[0][candidate] - final_state.quota
        candidate = candidate + 1
    #print fractional_vote_loss

# Extract final information (i.e. who got elected)
final_information = final_state.historical_votes_cand[-1]

# List of all people elected
temp = 0
elected_candidates = []
while temp < len(final_information[1]):
    if final_information[1][temp] == 1 or final_information[0][temp] >= final_state.quota:
        elected_candidates.append(temp)
    temp = temp + 1

# Correct the order, accounting for the final elected person who may not appear!
elected_candidates_correct_order = final_state.candidate_elected_order    
for candidate in elected_candidates:
    if not candidate in elected_candidates_correct_order:
        elected_candidates_correct_order.append(candidate)
elected_candidates = elected_candidates_correct_order

# Print out their parties and names
elected_dictionary = {}
with open(cands,'rb') as csvfile:
    spamreader = csv.reader(csvfile,delimiter=',')
    temp1 = -1
    elected = 0
    for row in spamreader:
        if temp1 in elected_candidates:
            elected_dictionary[temp1] = ' | ' + str(row[6]) + ' | ' + str(row[4]) + ', ' + str(row[5])
        temp1 = temp1 + 1

print elected_candidates        
for temp in range(len(elected_candidates)):
    print 'Elected No. ' + str(temp + 1) + elected_dictionary[elected_candidates[temp]]
