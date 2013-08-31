import csv
import math
import copy
#import numpy as np

def sen_dis( VARIABLE_votes, VARIABLE_parameters ):

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

        def set_ballot_papers(self, ballot_papers):
            self.ballots = ballot_papers

        def recalculate_votes(self, transfer_value):
            # When overflow happens in the senate; every ballot paper gets the same transfer value.
            # This then modifies the number of votes for this candidate.
            self.total = self.ballots * transfer_value

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

        def set_original_packet(self, orig_pack):
            # Set the original vote packet, where the vote originally came from
            self.original_packet = orig_pack



    ## The Senate Race Class
    # Contains the electoral information at each step.

    class SenRace(object):
        def __init__(self, vote_array, cands, decpla):
            # Defined by the vote in the vote array
            self.round = 1
            self.dp = max(0,math.floor(decpla))
            self.candidates = len(vote_array[0].pref_list)
            self.cand_to_elect = cands
            self.votes = 0
            self.vote_array = vote_array
            for vote in vote_array:
                self.votes = self.votes + vote.total
                # If we're looking at senate style votes; we need to include ballot papers
                if VARIABLE_parameters[4] == 0:
                    # Initially, number of ballot papers = number of votes.
                    vote.set_ballot_papers(vote.total)
            self.votes_cand = []
            temp = 0
            self.elected = []
            self.eliminated = []
            self.most_recent_packet = []    # This is the array that dictates which vote packet is most recent
            self.candidate_elected_order = []   # The index of each candidate, in order of election.
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
            for temp in range(len(vote_array)):
                # Check if anyone's voted for the sucker yet!
                if self.most_recent_packet[vote_array[temp].current_cand_loc] == [-1]:
                    self.most_recent_packet[vote_array[temp].current_cand_loc] = [temp]
                # If they have, then make sure you append the other packet, since they have equal priority
                else:
                    self.most_recent_packet[vote_array[temp].current_cand_loc].append(temp)
                vote_array[temp].set_original_packet(temp)
            self.distribute_overflow_stack = []
            self.distribute_excluded_stack = []
            self.historical_votes_cand = []
            self.historical_votes_cand.append([copy.deepcopy(self.votes_cand),copy.deepcopy(self.elected),copy.deepcopy(self.eliminated)])
            # This is the Final structure that pass back to the main function at the end. It contains all of the relevant information about
            # the unfolding of events, and is updated every time someone gets distributed. self.FINAL
            self.FINAL = []
            self.FINAL.append(['init', self.votes_cand])

        def eliminate_candidate(self, cand_no):
            self.eliminated[cand_no-1] = 1

        def elect_candidate(self, cand_no):
            self.elected[cand_no-1] = 1

        def check_state(self):
            if 'static' in self.state:
                # Need to do a quick loop here to establish votes for people left in the race
                # =========  BAD CODE, SORRY IT'S STUCK HERE KINDA ==========
                votes_left_in_race = []
                for temp in range(self.candidates):
                    if self.elected[temp] == 0:
                        if self.eliminated[temp] == 0:
                            votes_left_in_race.append(self.votes_cand[temp])
                # ========= /BAD CODE, SORRY IT'S STUCK HERE KINDA ==========
                # Are there enough candidates left who are not eliminated?
                if self.candidates - sum(self.eliminated) <= self.cand_to_elect:
                    self.state = 'done'
                    # Vector to add for final exclusion
                    FINAL_exclusion = ['last']
                    FINAL_exclusion.append([]) # THEIR RANK IN THE BALLOT?
                    FINAL_exclusion.append([])  # 2: ELECTED CANDIDATE (evaluated below)

                    total_elected_now = 0
                    temp = 0
                    while temp < self.candidates:
                        if self.eliminated[temp] == 0 and self.elected[temp] == 0:
                            self.elected[temp] = 1
                            total_elected_now = total_elected_now + 1
                            if FINAL_exclusion[2] == []:
                                FINAL_exclusion[2] = [temp]
                            else:
                                FINAL_exclusion[2].append(temp)
                        temp = temp + 1
                    for i in range(self.cand_to_elect-total_elected_now+1,self.cand_to_elect+1):
                        if FINAL_exclusion[1] == []:
                            FINAL_exclusion[1] = [i]
                        else:
                            FINAL_exclusion[1].append(i)
                    print 'We ended up in here; dunno how!'
                    FINAL_exclusion.append(copy.deepcopy(self.votes_cand))
                    self.FINAL.append(copy.deepcopy(FINAL_exclusion))

                # Are there enough candidates left who have breached quota?
                elif sum(i >= self.quota for i in self.votes_cand) >= self.cand_to_elect:

                    self.state = 'done'

                    # First, find a list (through FINAL) of the candidates who have been elected thus far.
                    FINAL_exclusion = ['last']
                    temp_elected = []
                    for row in self.FINAL:
                        if row[0] == 'over':
                            temp_elected.append(copy.deepcopy(row[2][0]))
                    temp = len(temp_elected)
                    FINAL_exclusion.append([])
                    while temp < self.cand_to_elect:
                        FINAL_exclusion[1].append(temp+1)   # Their rank in the ballot.
                        temp = temp + 1

                    FINAL_exclusion.append([])
                    for temp in range(self.candidates):
                        if self.votes_cand[temp] >= self.quota:
                            self.elected[temp] = 1
                            if not temp in temp_elected:
                                # Then they've been elected without being added to FINAL
                                # TO DO: Append in the magnitude of quota break
                                FINAL_exclusion[2].append(temp)

                    temp_vote_count = [0] * self.candidates
                    for vote in self.vote_array:
                        temp_vote_count[vote.current_cand_loc] = temp_vote_count[vote.current_cand_loc] + vote.total
                    FINAL_exclusion.append(copy.deepcopy(temp_vote_count))
                    self.FINAL.append(copy.deepcopy(FINAL_exclusion))
                # Insert other elif to call it when the bottom candidates to be eliminated,
                # the sum of their votes is less than the next bottom candidate.
                # elif
                # Now that the default win conditions have been checked, check to see if there's
                # an overquota to be distributed for the next level
                elif max(votes_left_in_race) >= self.quota:
                    # Elect the people that have broken quota
                    # Firstly, establish the order in which they've broken quota (i.e. by magnitude)
                    temp_list_vote = copy.deepcopy(self.votes_cand) # Vote Count
                    temp_list_elec = copy.deepcopy(self.elected)    #
                    temp_list_vote, temp_list_elec, temp_list_index = (list(t) for t in zip(*sorted(zip(temp_list_vote, temp_list_elec,range(len(temp_list_vote))))))
                    # Largest first
                    temp_list_vote.reverse()
                    temp_list_elec.reverse()
                    temp_list_index.reverse()
                    for temp in range(len(temp_list_vote)):
                        if temp_list_vote[temp] >= self.quota and temp_list_elec[temp] == 0:
                            # Only do this if they're unelected, and over quota. Biggest first!
                            self.elected[temp_list_index[temp]] = 1
                            self.distribute_overflow_stack.append(temp_list_index[temp])
                            self.candidate_elected_order.append(temp_list_index[temp])
                    self.state = 'distover'
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
                        FINAL_exclusion = ['zero']
                        FINAL_exclusion.append([])
                        FINAL_exclusion.append([])
                        stop = self.candidates - sum(self.eliminated) + 1
                        to_exclude = [i for i, e in enumerate(self.votes_cand) if e == 0]
                        for temp in to_exclude:
                            # Eliminate them
                            FINAL_exclusion[2].append(copy.deepcopy(temp))
                            self.eliminated[temp] = 1
                        FINAL_exclusion[1] = range(self.candidates-sum(self.eliminated)+1,stop)
                        FINAL_exclusion.append(copy.deepcopy(self.votes_cand))
                        self.FINAL.append(copy.deepcopy(FINAL_exclusion))

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
                votes_that_have_moved = []
                while self.distribute_excluded_stack != []:
                    # Distribute them!
                    cand_to_distribute = self.distribute_excluded_stack[0]
                    self.most_recent_packet[self.distribute_excluded_stack[0]] = [-1]
                    # Now add this candidate to the FINAL result vector.
                    FINAL_exclusion = ['drop']
                    FINAL_exclusion.append(self.candidates - sum(self.eliminated)+1)   # THEIR RANK IN THE BALLOT?
                    FINAL_exclusion.append([])  # 2: OLD CANDIDATE (evaluated below)
                    FINAL_exclusion.append([])  # 3: NEW CANDIDATE (evaluated below)
                    FINAL_exclusion.append([])  # 4: NUMBER OF VOTES (evaluated below)
                    FINAL_exclusion.append([])  # 5: ORIGINAL VOTE PACKET
                    FINAL_exclusion.append([])  # 6: NUMBER OF QUOTAS
                    FINAL_exclusion.append([])  # 7: NUMBER OF BALLOT PAPERS.
                    FINAL_exclusion.append([])  # 8: UNUSED! Will be : NUMBER OF OVERFLOW VOTES [ONLY CALCULATED IN AUS SENATE | recalculated for AUS SENATE OVERFLOW) later
                    for temp in range(len(self.vote_array)):
                        vote = self.vote_array[temp]
                        # Check each vote to see if it's on the distributed candidate.
                        if vote.current_cand_loc == cand_to_distribute:
                            # Progress the vote in the array
                            votes_that_have_moved.append(temp)
                            FINAL_exclusion[2].append(copy.deepcopy(vote.current_cand_loc))
                            vote.next_valid_candidate(self.elected,self.eliminated)
                            FINAL_exclusion[3].append(copy.deepcopy(vote.current_cand_loc))
                            FINAL_exclusion[4].append(copy.deepcopy(vote.total))
                            FINAL_exclusion[5].append(copy.deepcopy(vote.original_packet))
                            FINAL_exclusion[6].append(float(float(copy.deepcopy(vote.total))/float(self.quota)))
                            if VARIABLE_parameters[4] == 0:
                                FINAL_exclusion[7].append(float(copy.deepcopy(vote.ballots)))
                            self.vote_array[temp] = vote



                    # Recount the vote (in an unused variable, so as not to fuck up the rest of the code)
                    temp_vote_count = [0] * self.candidates
                    for vote in self.vote_array:
                        temp_vote_count[vote.current_cand_loc] = temp_vote_count[vote.current_cand_loc] + vote.total
                    self.votes_cand = copy.deepcopy(temp_vote_count)

                    FINAL_exclusion.append(copy.deepcopy(self.votes_cand)) # Append the current vote count
                    # Append FINAL_exclusion, but make sure to deep copy, because this will change
                    self.FINAL.append(copy.deepcopy(FINAL_exclusion))

                    # Then pop them off the stack
                    self.distribute_excluded_stack = self.distribute_excluded_stack[1:]

                #############################  PERFORMING VOTE RECOUNT #######################################
                # Perform a vote recount now that the votes have been moved.
                # Be sure to change the "most recent vote packet" information as well!
                temp = 0
                self.votes_cand = []
                most_recent_packet = [] # Temporary check for most_recent_packet
                while temp < self.candidates:
                    most_recent_packet.append([-1])
                    self.votes_cand.append(0)
                    temp = temp + 1
                temp = 0
                # Recalculate the Votes
                for vote in self.vote_array:
                    self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
                # For any votes that have moved; overwrite and/or append to the given most recent packet list
                for vote_no in votes_that_have_moved:
                    vote = self.vote_array[vote_no]
                    if most_recent_packet[vote.current_cand_loc] == [-1]:
                        most_recent_packet[vote.current_cand_loc] = [vote_no]
                        # For senate style voting; all packets are equal and distributed
                        if VARIABLE_parameters[4] == 0:
                            if self.most_recent_packet[vote.current_cand_loc] == [-1]:
                                self.most_recent_packet[vote.current_cand_loc] = [vote_no]
                            else:
                                self.most_recent_packet[vote.current_cand_loc].append(vote_no)
                        # For Proportional Representation style; only recent packets matter.
                        elif VARIABLE_parameters[4] == 1:
                            self.most_recent_packet[vote.current_cand_loc] = [vote_no]
                    # If they have, then make sure you append the other packet, since they have equal priority
                    else:
                        most_recent_packet[vote.current_cand_loc].append(vote_no)
                        self.most_recent_packet[vote.current_cand_loc].append(vote_no)
                self.historical_votes_cand.append([copy.deepcopy(self.votes_cand),copy.deepcopy(self.elected),copy.deepcopy(self.eliminated)])
                ############################# /PERFORMING VOTE RECOUNT #######################################
            elif 'distover' in self.state:
                # In this function we need to work through all of the quotas to be overflowed
                # One parse of the 'distover' function will work through all of the overflows.
                # Useful here is the while stack != []
                # So we can keep adding to the stack, and modifying the stack, within the while loop.
                self.state = 'static'
                while self.distribute_overflow_stack != []:
                    # The first element is the next person in the quota breaking list.
                    quota_cand = self.distribute_overflow_stack[0]
                    # Firstly make sure they're noted as elected
                    self.elected[quota_cand] = 1
                    # Then find how much they're over quota by:
                    overflow = self.votes_cand[quota_cand] - self.quota
                    # Then establish the number of packets to distribute
                    vote_packets_to_distribute = self.most_recent_packet[quota_cand]

                    # The list of number of votes in each packet that needs to be distributed.
                    transferring_votes = []
                    for temp in range(len(vote_packets_to_distribute)):
                        transferring_votes.append(self.vote_array[vote_packets_to_distribute[temp]].total)

                    # Transfer Value to 6 Decimal Places (can change)
                    transfer_value = float(math.floor(float(float(overflow) / float(sum(transferring_votes))) * pow(10,self.dp)) / pow(10,self.dp))

                    # Now we need to rewrite the vote structures
                    most_recent_packet = []
                    temp = 0
                    while temp < self.candidates:
                        most_recent_packet.append([-1])
                        temp = temp + 1

                    # Vector to add for final exclusion
                    FINAL_exclusion = ['over']
                    if self.FINAL == []:
                        FINAL_exclusion.append(1)
                    else:
                        temp_max = 0
                        for row in self.FINAL:
                            if 'over' in row[0]:
                                temp_max = max(temp_max,row[1])
                        temp_max = temp_max + 1
                        FINAL_exclusion.append(temp_max) # THEIR RANK IN THE BALLOT?
                    FINAL_exclusion.append([])  # 2: ELECTED CANDIDATE (evaluated below)
                    FINAL_exclusion.append([])  # 3: NEW CANDIDATE (evaluated below)
                    FINAL_exclusion.append([])  # 4: NUMBER OF OVERFLOW VOTES (evaluated below)
                    FINAL_exclusion.append([])  # 5: ORIGINAL VOTE PACKET
                    FINAL_exclusion.append([])  # 6: NUMBER OF OVERFLOW VOTES (ratio of quota)
                    FINAL_exclusion.append([])  # 7: NUMBER OF BALLOT PAPERS [ONLY CALCULATED IN AUS SENATE]
                    FINAL_exclusion.append([])  # 8: NUMBER OF OVERFLOW VOTES [ONLY CALCULATED IN AUS SENATE | recalculated for AUS SENATE OVERFLOW)

                    # Begin Transferring all Votes in This Round
                    ballots_aussenate = 0
                    votes_aussenate = 0
                    original_votes = len(self.vote_array)
                    for temp in range(len(transferring_votes)):
                        FINAL_exclusion[2].append(copy.deepcopy(quota_cand))
                        vote_index = vote_packets_to_distribute[temp]
                        vote_total = transferring_votes[temp]
                        vote_total_static = float(float(1-transfer_value) * float(vote_total))
                        vote_total_transfer = float(float(transfer_value) * float(vote_total))
                        # NOTE: IN HERE WE CAN WORK OUT THE FRACTIONAL LOSS OF THE VOTES (IF WE WANTED TO)

                        # Now modify the votes:
                        # First, modify the vote amount of the first vote:
                        self.vote_array[vote_index].change_votes(vote_total_static)
                        # Create the new vote element:
                        new_vote = SenVote(self.vote_array[vote_index].pref_list,vote_total_transfer)
                        new_vote.set_candidate_index(self.vote_array[vote_index].current_cand_loc)
                        new_vote.next_valid_candidate(self.elected,self.eliminated)
                        if VARIABLE_parameters[4] == 0:
                            new_vote.set_ballot_papers(self.vote_array[vote_index].ballots)
                            ballots_aussenate = ballots_aussenate + new_vote.ballots
                            votes_aussenate = votes_aussenate + new_vote.total

                        FINAL_exclusion[3].append(copy.deepcopy(new_vote.current_cand_loc))
                        FINAL_exclusion[4].append(copy.deepcopy(new_vote.total))
                        FINAL_exclusion[6].append(float(float(copy.deepcopy(new_vote.total))/float(self.quota)))

                        # Work out the new vote index
                        new_vote_index = len(self.vote_array)# + 1
                        # Define this new vote packet as a new overflow packet for the next distribution:
                        if most_recent_packet[new_vote.current_cand_loc] == [-1]:
                            most_recent_packet[new_vote.current_cand_loc] = [new_vote_index]
                            # For senate style voting; all packets are equal and distributed
                            if VARIABLE_parameters[4] == 0:
                                if self.most_recent_packet[new_vote.current_cand_loc] == [-1]:
                                    self.most_recent_packet[new_vote.current_cand_loc] = [new_vote_index]
                                else:
                                    self.most_recent_packet[new_vote.current_cand_loc].append(new_vote_index)
                            # For Proportional Representation style; only recent packets matter.
                            elif VARIABLE_parameters[4] == 1:
                                self.most_recent_packet[new_vote.current_cand_loc] = [new_vote_index]
                        else:
                            most_recent_packet[new_vote.current_cand_loc].append(new_vote_index)
                            self.most_recent_packet[new_vote.current_cand_loc] = [new_vote_index]
                        # Set this packet as the new final packet for this candidate!
                        self.vote_array.append(new_vote)
                        # Set the origin of this split vote to the origin of the previous vote.
                        self.vote_array[new_vote_index].set_original_packet(self.vote_array[vote_index].original_packet)
                        FINAL_exclusion[5].append(copy.deepcopy(new_vote.original_packet))
                        #############################  PERFORMING VOTE RECOUNT #######################################
                        # Perform a vote recount now that the votes have been moved.
                        self.votes_cand = []
                        for temp2 in range(self.candidates):
                            self.votes_cand.append(0)
                        # Recalculate the Votes
                        for vote in self.vote_array:
                            self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
                        ############################# /PERFORMING VOTE RECOUNT #######################################

                    # NOW WE NEED TO RECOUNT THE VOTES ACCORDING TO THE STUPID SENATE COUNT
                    if VARIABLE_parameters[4] == 0:
                        # We have the total votes for all of the transfer (i.e. the surplus)
                        # We have the total number of ballot papers being transferred.
                        # Therefore:
                        new_transfer_value = float(math.floor(float(float(votes_aussenate)/float(ballots_aussenate)) * pow(10,self.dp)) / pow(10,self.dp))
                        for temp in range(len(transferring_votes)):
                            # Begin modifying the votes at the end of the new vote array.
                            new_index = original_votes + temp
                            self.vote_array[new_index].recalculate_votes(new_transfer_value)
                        # Perform a vote recount now that the votes have been moved.
                        self.votes_cand = []
                        for temp2 in range(self.candidates):
                            self.votes_cand.append(0)
                        # Recalculate the Votes
                        for vote in self.vote_array:
                            self.votes_cand[vote.current_cand_loc] = self.votes_cand[vote.current_cand_loc] + vote.total
                        for temp in range(len(transferring_votes)):
                            new_index = original_votes + temp
                            FINAL_exclusion[7].append(self.vote_array[new_index].ballots)
                            FINAL_exclusion[8].append(self.vote_array[new_index].total)


                    FINAL_exclusion.append(copy.deepcopy(self.votes_cand)) # 9: APPEND THE CURRENT VOTE COUNT
                    self.historical_votes_cand.append([copy.deepcopy(self.votes_cand),copy.deepcopy(self.elected),copy.deepcopy(self.eliminated)])
                    self.FINAL.append(copy.deepcopy(FINAL_exclusion))

                    # Now do a quick check of all unelected, and uneliminated candidates to see if any of them have broken quota
                    # If so, we need to append them to the self.distribute_overflow_stack.
                    # TO DO: MAKE IT OVERFLOW CORRECTLY, AND APPEND IN THE ORDER OF THE OVERFLOWS THAT HAPPEN
                    for temp in range(self.candidates):
                        if self.elected[temp] == 0:
                            if self.eliminated[temp] == 0:
                                if self.votes_cand[temp] >= self.quota:
                                    # APPEND TO LIST!
                                    self.elected[temp] = 1
                                    self.distribute_overflow_stack.append(temp)
                                    self.candidate_elected_order.append(temp)

                    self.distribute_overflow_stack = self.distribute_overflow_stack[1:]
                if sum(self.elected) >= self.cand_to_elect:
                    self.state = 'done'

    voting_structure = []
    for vote in VARIABLE_votes:
        voting_structure.append(SenVote(vote[0],vote[1]))

    cand_elec = VARIABLE_parameters[0]
    decimal_places = VARIABLE_parameters[1]
    total_race = SenRace(voting_structure,cand_elec,decimal_places)
    if VARIABLE_parameters[2] == 1:
        print "================================================"
        print "================                 ==============="
        print "==============     BEGIN RACE      ============="
        print "================                 ==============="
        print "================================================"
        print '==THE QUOTA IS: ' + str(total_race.quota) + '===='
    while total_race.state != 'done':
        total_race.check_state()
        if VARIABLE_parameters[2] == 1:
            print 'Current race state: ' + str(total_race.state)
            print 'Current elected: ' + str(sum(total_race.elected))
            print 'Current eliminated: ' + str(sum(total_race.eliminated))
            print 'Current Vote Count: ' + str(total_race.votes_cand)
            print "================================================"
    if VARIABLE_parameters[2] == 1:
        print "================                 ==============="
        print "==============      END RACE       ============="
        print "================                 ==============="
        print "================================================"
    return total_race


