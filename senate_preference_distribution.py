import csv
import math
import numpy as np

# Application for checking senate allocations of the following parties.

## The Vote Class
# The vote class represents an individual vote; who it is currently for,
# as well at it's complete list of preferences.

class SenVote(object):
    def __init__(self, vote_pref, no_of_votes):
        # Indicate the number of votes for this given preference flow
        self.total = no_of_votes        # Integer
        self.pref_list = vote_pref      # A csv object
        # Find the current (i.e. initial candidate we're voting for)
        self.current_cand_loc   = self.pref_list.index(1)
        self.current_cand       = self.current_cand_loc + 1
    def drop_bottom(self, cand_2_dist_loc):
        # Check if this vote is currently sitting on "Cand_2_dist"
        # If so, we need to move these votes to candidates still remaining
        # I.e. candidates who are not elected, and candidates who are not eliminated
        cand_2_dist = cand_2_dist_loc + 1
    def change_votes(self, new_votes):
        self.total = new_votes
    def set_candidate(self, new_candidate):
        self.current_cand_loc = new_candidate - 1
        self.current_cand = new_candidate
    def set_candidate_index(self, new_candidate_index):
        self.current_cand_loc = new_candidate_index
        self.current_cand = new_candidate_index + 1
    def next_valid_candidate(self, elected, eliminated):
        current_preference_number = self.pref_list[self.current_cand_loc]
        # The current candidate is current_cand_loc, while their index down the
        # vote preference array (i.e. the number we're currently at in the counting in 
        # their preference form) is current_candidate_index
        found_candidate = 0
        while found_candidate == 0:
            # Increment the preference number
            current_preference_number = current_preference_number + 1
            # Find it
            current_cand_loc = self.pref_list.index(current_preference_number)
            # Check if this new candidate is valid
            if elected[current_cand_loc] + eliminated[current_cand_loc] == 0:
                found_candidate = 1
                self.current_cand_loc = current_cand_loc
                self.current_cand = self.current_cand_loc + 1
                
        

## The Senate Race Class
# Contains the electoral information at each step.

# TODO: Work out order of senate elect
        
class SenRace(object):
    def __init__(self, vote_array, cands):
        # Defined by the vote in the vote array
        self.round = 1
        self.candidates = len(vote_array[0].pref_list)
        self.cand_to_elect = cands
        self.votes = 0
        self.vote_array = vote_array
        for vote in vote_array:
            self.votes = self.votes + vote.total
        self.votes_cand = []
        temp = 0
        self.elected = []
        self.eliminated = []
        self.most_recent_packet = []    # This is the array that dictates which vote packet is most recent
        while temp < self.candidates:
            self.votes_cand.append(0)
            self.elected.append(0)
            self.eliminated.append(0)
            self.most_recent_packet.append([-1])
            temp = temp + 1
        for vote in vote_array:
            self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
        self.quota = int(math.floor(self.votes / (cands + 1)) + 1)
        self.state = 'static'
        # Now check each vote packet to populate the most_recent_packet array
        temp = 0
        for vote in vote_array:
            # Check if anyone's voted for the sucker yet!
            if self.most_recent_packet[vote.current_cand_loc] == [-1]:
                self.most_recent_packet[vote.current_cand_loc] = [temp]
            # If they have, then make sure you append the other packet, since they have equal priority
            else:
                self.most_recent_packet[vote.current_cand_loc].append(temp)
            temp = temp + 1
        self.distribute_overflow_stack = []
        self.distribute_excluded_stack = []
    def eliminate_candidate(self, cand_no):
        self.eliminated[cand_no-1] = 1
    def elect_candidate(self, cand_no):
        self.elected[cand_no-1] = 1
    def check_state(self):
        if 'static' in self.state:
            # Are there enough candidates left who are not eliminated?
            if self.candidates - sum(self.eliminated) <= self.cand_to_elect:
                self.state = 'done'
                temp = 0
                while temp < self.candidates:
                    if self.eliminated[temp] == 0:
                        self.elected[temp] = 1
                    temp = temp + 1
            # Are there enough candidates left who have breached quota?
            elif sum(i >= self.quota for i in self.votes_cand) >= self.cand_to_elect:
                self.state = 'done'
                temp = 0
                while temp < self.candidates:
                    if self.votes_cand[temp] >= self.quota:
                        self.elected[temp] = 1
                    temp = temp + 1
            # Insert other elif to call it when the bottom candidates to be eliminated,
            # the sum of their votes is less than the next bottom candidate.
            # elif
            # Now that the default win conditions have been checked, check to see if there's
            # an overquota to be distributed for the next level
            elif max(self.votes_cand) >= self.quota:
                # Find the member to distribute
                # TO DO: RANDOM CHOICE OF EQUAL TOP CANDIDATES
                self.distribute_overflow_stack.append(self.votes_cand.index(max(self.votes_cand)))
                # Elect the people that have broken quota
                temp = 0
                while temp < self.candidates:
                    if self.votes_cand[temp] > self.quota:
                        self.elected[temp] = 1
                    temp = temp + 1
                # Change the state to distribution of overflow stage
                self.state = 'distover'
                # TO DO: NEED TO ADD VECTOR FOR VOTE PACKETS THAT NEED TO BE DISTRIBUTED
                # IN THE ORDER IN WHICH THEY BREAK QUOTA
            # else we've got to drop from the bottom; so take the smallest person
            else:
                self.state = 'dropbott'
                # Candidates who have not been excluded:
                cand_not_excl = [i for i, e in enumerate(self.eliminated) if e == 0]
                min_votes = max(self.votes_cand)
                for temp in cand_not_excl:
                    min_votes = min(min_votes,self.votes_cand[temp])
                # Now min_votes is the minimum number of votes for a candidate who hasn't been eliminated.
                if min_votes == 0:
                    # I.e. there are candidates who are on zero votes? We need to exclude them from the race now.
                    to_exclude = [i for i, e in enumerate(self.votes_cand) if e == 0]
                    for temp in to_exclude:
                        # Eliminate them
                        self.eliminated[temp] = 1
                # Now that we've eliminated the candidates on zero votes; we can eliminate the next lowest
                # candidate, first check who that candidate is; by recalculating
                cand_not_excl = [i for i, e in enumerate(self.eliminated) if e == 0]
                min_votes = max(self.votes_cand)
                for temp in cand_not_excl:
                    min_votes = min(min_votes,self.votes_cand[temp])
                # TO DO: RANDOM CHOICE OF EQUAL BOTTOM CANDIDATES
                self.distribute_excluded_stack.append(self.votes_cand.index(min_votes))
                self.eliminated[self.votes_cand.index(min_votes)] = 1
        elif 'dropbott' in self.state:
            # Drop the candidate from the bottom, and then assign to the static state.
            self.state = 'static'
            self.round = self.round + 1
            # While there is someone to distribute
            while self.distribute_excluded_stack != []:
                # Distribute them!
                cand_to_distribute = self.distribute_excluded_stack[0]
                temp = 0
                while temp < len(self.vote_array):
                    vote = self.vote_array[temp]
                    # Check each vote to see if it's on the distributed candidate.
                    if vote.current_cand_loc == cand_to_distribute:
                        # Progress the vote in the array
                        vote.next_valid_candidate(self.elected,self.eliminated)
                        self.vote_array[temp] = vote
                    temp = temp + 1
                # Then pop them off the stack
                self.distribute_excluded_stack = self.distribute_excluded_stack[1:]
            
            # Perform a vote recount now that the votes have been moved.
            temp = 0
            self.votes_cand = []
            while temp < self.candidates:
                self.votes_cand.append(0)
                temp = temp + 1
            for vote in self.vote_array:
                self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
            
a = [0,0,1,3]
b = [i for i, e in enumerate(a) if e != 0]
c = min(b)
print a[c]
for i in b:
    print a[i]
    
stack = []
stack.append(1)
stack.append(2)
stack.append(3)
while stack != []:
    stack = stack[1:]
    print "Stack: " + str(stack)
           
            
            


## Source files.
# Preference flows for above the line votes sorted by party letter.
# Each row is of the form:
# Party Group , How Many Forms? , Preferences by ballot. 
prefs = 'NSW_Senate_Preferences.csv'
# List of Candidates for the Senate sorted by ballot position
cands = 'NSW_Senate_Candidates.csv'
# A list of the letter Groups along with the
gpptv = 'NSW_Groups_Parties_Votes.csv'



# Let us create a temporary voting structure for the senate        
voting_structure = []
voting_structure.append(SenVote([3,1,2,4],202))
voting_structure.append(SenVote([4,2,1,3],201))
voting_structure.append(SenVote([1,2,3,4],200))
voting_structure.append(SenVote([3,2,4,1],51))
voting_structure.append(SenVote([3,4,2,1],50))

# Candidates to be elected
cand_elec = 2
total_race = SenRace(voting_structure,cand_elec)
total_race.check_state()

print voting_structure[1].total
print voting_structure[1].pref_list
print voting_structure[1].current_cand
print total_race.most_recent_packet
print total_race.votes
print total_race.candidates
print total_race.votes_cand
print total_race.quota
print total_race.elected
print total_race.state

total_race.check_state()

print total_race.state

print voting_structure[1].total
print voting_structure[1].pref_list
print voting_structure[1].current_cand
print total_race.most_recent_packet
print total_race.votes
print total_race.candidates
print total_race.votes_cand
print total_race.quota
print total_race.elected
print total_race.state

#a = [0,0,1,3]
#anp = np.array(a)
#val = np.min(anp[np.nonzero(anp)])
#print str(val)
#print a.index(val)

test_vote = SenVote([3,2,1,4],400)
test_vote.next_valid_candidate([0,0,0,0],[0,0,0,0])
print "New Candidadte: " + str(test_vote.current_cand)
test_vote.set_candidate(2)
print "New Candidadte: " + str(test_vote.current_cand)
test_vote.set_candidate_index(3)
print "New Candidadte: " + str(test_vote.current_cand)
