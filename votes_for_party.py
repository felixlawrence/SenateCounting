# This function will determine votes per party based on each state during the election.
# It will return a sorted list of party by number of votes / quotas.
from sen_dis import sen_dis
import csv
import math
import copy
import itertools
from itertools import permutations, islice
#import numpy as np

def group_setup ( gpptv ):
    # Create a dictionary of votes for all of the groups that have GVTs
    vote_dictionary = {}    # Dictionary of vote values for each group
    name_dictionary = {}    # Dictionary of names for each group
    group_list      = []
    short_group_list = []
    t_votes = 0             # Sum of all votes in the file (should be greater than 0)
    with open(gpptv,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=',')
        temp1 = 0
        for row in spamreader:
            t_votes = float(float(t_votes) + float(row[2].strip()))
            vote_dictionary[row[0].strip()] = row[2].strip()
            name_dictionary[row[0].strip()] = row[1].strip()
            group_list.append(row[0].strip())
            temp1 = temp1 + 1
    for group in group_list:
        if not group in short_group_list:
            short_group_list.append(group)
    if not 'Ungrouped' in short_group_list:
        short_group_list.append('Ungrouped')
    vote_dictionary['Ungrouped'] = '0'
    return vote_dictionary, name_dictionary, group_list, t_votes
    
def group_batch_from_list ( list, index ):
    return list[index]

def group_batch_from_iterable ( list_to_iterate, index ):
    default = None
    iter_input = itertools.product(*list_to_iterate)
    #temp = list(next(islice(iter_input,index,None),default))    # I HAVE NO FUCKING IDEA WHY THIS WORKS; BUT EVERY SO OFTEN SOMETHING BREAKS WITHOUT IT
    #temp2 = list(next(islice(iter_input,index,None),default))
    #temp3 = list(next(islice(iter_input,index,None),default))
    #temp4 = list(next(islice(iter_input,index,None),default))
    #temp5 = list(next(islice(iter_input,index,None),default))
    #temp6 = list(next(islice(iter_input,index,None),default))
    #temp7 = list(next(islice(iter_input,index,None),default))
    #temp8 = list(next(islice(iter_input,index,None),default))
    #temp9 = list(next(islice(iter_input,index,None),default))
    #temp10 = list(next(islice(iter_input,index,None),default))
    #temp11 = list(next(islice(iter_input,index,None),default))
    #temp12 = list(next(islice(iter_input,index,None),default))
    #temp13 = list(next(islice(iter_input,index,None),default))
    #temp14 = list(next(islice(iter_input,index,None),default))
    #temp15 = [0]*len(temp)
    #for i in range(len(temp15)): temp15[i] = float(copy.deepcopy(temp[i]))
    #return temp15
    return list(next(islice(iter_input,index,None),default))
    
def group_setup_from_list ( gpptv , list ):
    # Create a dictionary of votes for all of the groups that have GVTs
    vote_dictionary = {}    # Dictionary of vote values for each group
    name_dictionary = {}    # Dictionary of names for each group
    group_list      = []
    short_group_list = []
    t_votes = 0             # Sum of all votes in the file (should be greater than 0)
    with open(gpptv,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=',')
        temp1 = 0
        for row in spamreader:
            t_votes = float(float(t_votes) + float(row[2].strip()))
            vote_dictionary[row[0].strip()] = row[2].strip()
            name_dictionary[row[0].strip()] = row[1].strip()
            group_list.append(row[0].strip())
            temp1 = temp1 + 1
    for group in group_list:
        if not group in short_group_list:
            short_group_list.append(group)
    if not 'Ungrouped' in short_group_list:
        short_group_list.append('Ungrouped')
    vote_dictionary['Ungrouped'] = '0'
    index = 0
    t_votes = 0
    for group in group_list:
        if index < len(list):
            vote_dictionary[group] = list[index]
            t_votes = t_votes + list[index]
        index = index + 1
    
    return vote_dictionary, name_dictionary, group_list, t_votes

def total_election ( prefs, cands, gpptv, ausst, no_of_electors, parameters, vote_dictionary, name_dictionary, group_list, t_votes):
    
    # Create the vote list to pass into the algorithm; appending all of
    # the preference data.
    votes = []
    vote_list_ticket_data = []
    with open(prefs,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=',')
        temp1 = 0
        ticket_of_total = 1
        last_group = '0'
        for row in spamreader:
            no_of_votes = int(math.floor(float(float(float(vote_dictionary[row[0].strip()]) / float(row[1])) * float(no_of_electors) / float(t_votes))))
            votes.append([[],no_of_votes])
            temp2 = 2
            while temp2 < len(row):
                votes[temp1][0].append(int(row[temp2]))
                temp2 = temp2 + 1
            temp1 = temp1 + 1
            # Check if the last group was the same
            if row[0].strip() in last_group:
                ticket_of_total = ticket_of_total + 1
            else:
                ticket_of_total = 1
            last_group = row[0].strip()
            vote_list_ticket_data.append([last_group,ticket_of_total,int(row[1])])

    # Create a dictionary of the candidates by their group letter.
    cand_to_group = []
    current_group = '0'
    with open(cands,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=',')
        first_row = 0
        index = -1
        for row in spamreader:
            if first_row == 1:
                if '1' in row[3]:
                    index = index + 1
                    if index >= len(group_list):
                        current_group = 'Ungrouped'
                    else:
                        current_group = group_list[index]
                cand_to_group.append([copy.deepcopy(current_group),str(row[5]) + ' ' + str(row[4])])
            first_row = 1

    # Run the election
    final_state = sen_dis(votes,parameters)

    # The only arrays to pull out are:
    output  = final_state.FINAL
    quota   = final_state.quota

    #####  WORK OUT THE PARTY VOTE  #####

    # Party Vote Output
    output_party        = [] # Includes current overflows and quotas
    output_party2       = [] # Removes quotas that have been distributed
    f_loss              = 0
    fractional_loss     = [] # Calculation of Fractional Loss at each iteration
    curr_elected        = [] # List of currently elected people
    for line in output:
        # Candidates who are currently elected
        curr_elected = candidates_elected(line,curr_elected)    
        # Work out the fractional loss
        f_loss = frac_loss(line,curr_elected,f_loss,quota)
        fractional_loss.append(f_loss)
        # Now work out the total party vote
        output_party.append(party_vote(line, cand_to_group, name_dictionary, quota))
        # Now work out the total party vote, ignoring those candidates who have been elected.
        output_party2.append(party_vote_adjusted(line, cand_to_group, name_dictionary, quota, output_party[len(output_party)-1]))
        ##### TO DO HERE: CONSTRUCT THE DATA WE NEED TO PRESENT FOR THE SENATE CALCULATION OUTPUT ONLINE (i.e. to copy Antony green's)  ########

    # Output the number candidates elected for each party
    party_elected       = final_party_count(curr_elected, cand_to_group, name_dictionary)
    party_elected_list  = final_party_count_to_list(party_elected, cand_to_group, name_dictionary)
    
    return vote_dictionary, name_dictionary, group_list, votes, vote_list_ticket_data, cand_to_group, final_state, output, quota, output_party, output_party2, fractional_loss, curr_elected, party_elected, party_elected_list



def party_vote( LINE, CAND_TO_GROUP, GROUP_TO_PARTY, QUOTA ):
    # LINE is an output line from a function call to the senate calculator.
    # CAND_TO_GROUP[candidate][0] = group
    # CAND_TO_GROUP[candidate][1] = name of candidate
    # GROUP_TO_PARTY[group] = party
    
    # Firstly; construct a list of all of the groups:
    GROUP_LIST = []
    for group in CAND_TO_GROUP:
        if not group[0] in GROUP_LIST: GROUP_LIST.append(group[0])
    
    
    # We want to return the current vote count for each party; as a list of lists.
    vote_count = []
    for group in GROUP_LIST: vote_count.append([0,0,0])
    if 'init' in LINE[0]:
        total_votes = sum(LINE[1])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[1][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'last' in LINE[0]:
        total_votes = sum(LINE[3])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[3][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'zero' in LINE[0]:
        total_votes = sum(LINE[3])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[3][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'over' in LINE[0]:
        total_votes = sum(LINE[9])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[9][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'drop' in LINE[0]:
        total_votes = sum(LINE[9])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[9][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    else:
        vote_count = 'ERROR'
        
    return vote_count

def party_vote_adjusted( LINE, CAND_TO_GROUP, GROUP_TO_PARTY, QUOTA , OUTPUT_PARTY):
    # LINE is an output line from a function call to the senate calculator.
    # CAND_TO_GROUP[candidate][0] = group
    # CAND_TO_GROUP[candidate][1] = name of candidate
    # GROUP_TO_PARTY[group] = party
    
    # Firstly; construct a list of all of the groups:
    GROUP_LIST = []
    for group in CAND_TO_GROUP:
        if not group[0] in GROUP_LIST: GROUP_LIST.append(group[0])
    
    # Now subtract off the quotas on a per group basis.
    
    
    # We want to return the current vote count for each party; as a list of lists.
    vote_count = []
    for group in GROUP_LIST: vote_count.append([0,0,0])
    if 'init' in LINE[0]:
        total_votes = sum(LINE[1])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[1][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'last' in LINE[0]:
        total_votes = sum(LINE[3])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[3][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'zero' in LINE[0]:
        total_votes = sum(LINE[3])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[3][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'over' in LINE[0]:
        total_votes = sum(LINE[9])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[9][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    elif 'drop' in LINE[0]:
        total_votes = sum(LINE[9])
        for candidate in range(len(CAND_TO_GROUP)):
            new_index = GROUP_LIST.index(CAND_TO_GROUP[candidate][0])
            # Total Number of Votes
            vote_count[new_index][0] = vote_count[new_index][0] + LINE[9][candidate]
            # Total Number of Quotas
            vote_count[new_index][1] = float(float(vote_count[new_index][0])/float(QUOTA))
            # Total % of the Vote.
            vote_count[new_index][2] = float(float(vote_count[new_index][0])/float(total_votes)*100)
    else:
        vote_count = 'ERROR'
        
    return vote_count
    
def candidates_elected ( LINE , CURR_ELECTED ):
    # Returns a list of all candidates that have been elected / distributed during this line
    candidates = CURR_ELECTED
    if 'last' in LINE[0]:
        for element in LINE[2]:
            candidates.append(element)
    elif 'over' in LINE[0]:
        candidates.append(LINE[2][0])
    return candidates
    
def frac_loss ( LINE , CURR_ELECTED , FRACTIONAL_LOSS , QUOTA):
    # Run through the people currently elected, and look at their fractional losses in the vote matrix.
    f_loss = FRACTIONAL_LOSS
    if 'last' in LINE[0]:
        f_loss = 0
        for candidate in CURR_ELECTED:
            if not candidate in LINE[2]:    # Ignore finally elected candidates
                if LINE[3][candidate] > QUOTA:
                    f_loss = f_loss + LINE[3][candidate] - QUOTA
    elif 'over' in LINE[0]:
        f_loss = 0
        for candidate in CURR_ELECTED:
            if LINE[9][candidate] > QUOTA:
                f_loss = f_loss + LINE[9][candidate] - QUOTA
    elif 'drop' in LINE[0]:
        f_loss = 0
        for candidate in CURR_ELECTED:
            if LINE[9][candidate] > QUOTA:
                f_loss = f_loss + LINE[9][candidate] - QUOTA
    return f_loss
    
    
def final_party_count( FINAL_CANDIDATES, CAND_TO_GROUP, GROUP_TO_PARTY ):
    # FINAL_CANDIDATES
    # CAND_TO_GROUP[candidate][0] = group
    # CAND_TO_GROUP[candidate][1] = name of candidate
    # GROUP_TO_PARTY[group] = party
    
    # Firstly; construct a list of all of the groups:
    GROUP_LIST = []
    for group in CAND_TO_GROUP:
        if not group[0] in GROUP_LIST: GROUP_LIST.append(group[0])
        
    # And the output array
    FINAL_COUNT = []
    for group in GROUP_LIST: FINAL_COUNT.append(0)
    print FINAL_CANDIDATES
    print CAND_TO_GROUP
    for candidate in FINAL_CANDIDATES:
        print candidate
        FINAL_COUNT[GROUP_LIST.index(CAND_TO_GROUP[candidate][0])] = FINAL_COUNT[GROUP_LIST.index(CAND_TO_GROUP[candidate][0])] + 1
    
    return FINAL_COUNT
    
def final_party_count_to_list( PARTY_ELECTED, CAND_TO_GROUP, GROUP_TO_PARTY ):
    # Firstly; construct a list of all of the groups:
    GROUP_LIST = []
    for group in CAND_TO_GROUP:
        if not group[0] in GROUP_LIST: GROUP_LIST.append(group[0])
    
    list1, list2 = (list(t) for t in zip(*sorted(zip(PARTY_ELECTED, GROUP_LIST))))
    list1.reverse()
    list2.reverse()
    
    for index in range(len(list1)):
        party = list1[index]
        group = list2[index]
        if party > 0:
            GROUP_LIST.append([group,party])
        
        
    return GROUP_LIST
