import csv
import math

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
    def distribute_candidate(self, cand_2_dist, cand_votes, cand_elected_eliminated):
        # Check if this vote is currently sitting on "Cand_2_dist"
        # If so, we need to move these votes to candidates still remaining
        # I.e. candidates who are not elected, and candidates who are not eliminated
        self.random = 1
        
class SenRace(object):
    def __init__(self, vote_array, cands):
        # Defined by the vote in the vote array
        self.candidates = len(vote_array[0].pref_list)
        self.cand_to_elect = cands
        self.votes = 0
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
            self.most_recent_packet.append(0)
            temp = temp + 1
        for vote in vote_array:
            self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
        self.quota = int(math.floor(self.votes / (cands + 1)) + 1)
        self.state = 'static'
        #for vote in vote_array:
        #    self.most_recent_packet
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
            #elif 
            
            


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
voting_structure.append(SenVote([3,1,2,4],400))
voting_structure.append(SenVote([4,2,1,3],370))
voting_structure.append(SenVote([1,2,3,4],230))
voting_structure.append(SenVote([3,2,4,1],100))

# Candidates to be elected
cand_elec = 2
total_race = SenRace(voting_structure,cand_elec)
total_race.check_state()

print voting_structure[1].total
print voting_structure[1].pref_list
print voting_structure[1].current_cand
print total_race.votes
print total_race.candidates
print total_race.votes_cand
print total_race.quota
print total_race.elected



