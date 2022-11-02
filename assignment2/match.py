import numpy as np
from typing import List, Tuple
from collections import deque
from itertools import combinations

PREFERENCE_CAN_MATCH = {
    'Men': ['Male'],
    'Women': ['Female'],
    'Bisexual': ['Male', 'Female', 'Nonbinary']
}

def gale_shapley(proposers: List, receivers: List, proposer_rankings, receiver_rankings):
    receiver_matches = {receiver: None for receiver in receivers}
    matches = {proposer: None for proposer in proposers}

    remaining_proposers = deque(proposers)
    while len(remaining_proposers) > 0: # While a proposer is free and they haven't proposed to everyone
        current_proposer = remaining_proposers.popleft()
        current_receiver = proposer_rankings[current_proposer].popleft()
        if receiver_matches[current_receiver] is None:
            receiver_matches[current_receiver] = current_proposer
            matches[current_proposer] = current_receiver
        elif receiver_rankings[current_receiver].index(current_proposer) < receiver_rankings[current_receiver].index(receiver_matches[current_receiver]):
            displaced_proposer = receiver_matches[current_receiver]
            remaining_proposers.append(displaced_proposer)
            receiver_matches[current_receiver] = current_proposer
            matches[current_proposer] = current_receiver
        else:
            remaining_proposers.append(current_proposer)

    return matches


def generate_rankings(choosers: List[List], scores: List[List]) -> List[List]:
    """
    Takes in the score matrix and returns a matrix of rankings where rankings[i] is a list of indices of users sorted by decreasing preference
    """
    n = len(scores)

    def generate_rankings_for_user(user_id: int) -> deque[int]:
        ordered_list = sorted(range(n), key=lambda j: scores[user_id][j], reverse=True)
        return deque(filter(lambda receiver_id: receiver_id not in choosers, ordered_list))
        #return deque(ordered_list)

    rankings = {proposer_id: generate_rankings_for_user(proposer_id) for proposer_id in choosers}

    return rankings


def run_matching(og_scores: List[List], gender_id: List, gender_pref: List) -> List[Tuple]:
    """
    :param scores: raw N x N matrix of compatibility scores. Use this to derive a preference rankings.
    :param gender_id: list of N gender identities (Male, Female, Non-binary) corresponding to each user
    :param gender_pref: list of N gender preferences (Men, Women, Bisexual) corresponding to each user
    :return: `matches`, a List of (Proposer, Acceptor) Tuples representing monogamous matches

    Some Guiding Questions/Hints:
        - This is not the standard Men proposing & Women receiving scheme Gale-Shapley is introduced as ✅
        - Instead, to account for various gender identity/preference combinations, it would be better to choose a random half of users to act as "Men" (proposers) and the other half as "Women" (receivers) ✅
            - From there, you can construct your two preferences lists (as seen in the canonical Gale-Shapley algorithm; one for each half of users ✅
        - Before doing so, it is worth addressing incompatible gender identity/preference combinations (e.g. gay men should not be matched with straight men). ✅
            - One easy way of doing this is setting the scores of such combinations to be 0 ✅
            - Think carefully of all the various (Proposer-Preference:Receiver-Gender) combinations and whether they make sense as a match ✅
        - How will you keep track of the Proposers who get "freed" up from matches? ✅ deque
        - We know that Receivers never become unmatched in the algorithm. ✅
            - What data structure can you use to take advantage of this fact when forming your matches? ✅ a dictionary with the form { proposer: ordered list of unproposed people }
        - This is by no means an exhaustive list, feel free to reach out to us for more help!
    """

    #? Why is scores != score^T? It should be symmetric over the diagonal.

    n = len(og_scores)

    for proposers_tuple in combinations(range(n), n//2):
        proposers = np.array(proposers_tuple)
        receivers = np.array([i for i in range(n) if i not in proposers]) # List of people to be considered as receivers

        scores = np.copy(og_scores)

        for i in range(n - 1):
            for j in range(i + 1, n):
                gender_preference_mismatch = (gender_id[i] not in PREFERENCE_CAN_MATCH[gender_pref[j]]) or (gender_id[j] not in PREFERENCE_CAN_MATCH[gender_pref[i]])
                role_mismatch = (i in proposers and j in proposers) or (i in receivers and j in receivers)
                if gender_preference_mismatch or role_mismatch:
                    scores[i][j] = 0 # Used to check for incompatible matches at the end
                    scores[j][i] = 0 # Used to check for incompatible matches at the end

        proposer_rankings = generate_rankings(proposers, scores)
        receiver_rankings = generate_rankings(receivers, scores)

        matches = gale_shapley(proposers, receivers, proposer_rankings, receiver_rankings)

        valid = True
        for proposer_id, receiver_id in matches.items():
            if scores[proposer_id][receiver_id] == 0:
                valid = False
                break
        
        if valid:
            return matches
        # Else it will continue to a new possibility

    return None


def check_matching(matches, gender_id, gender_pref):
    incompatible = False
    for proposer_id, receiver_id in matches.items():
        gender_preference_mismatch = gender_id[proposer_id] not in PREFERENCE_CAN_MATCH[gender_pref[receiver_id]] or gender_id[receiver_id] not in PREFERENCE_CAN_MATCH[gender_pref[proposer_id]]
        if gender_preference_mismatch:
            print(f'Proposer {proposer_id} and Receiver {receiver_id} have incompatible gender preferences')
            incompatible = True
    if not incompatible:
        print(f'Valid matching found!')
        for proposer_id, receiver_id in matches.items():
            print(f'Proposer {proposer_id} matched with Receiver {receiver_id}')
    


if __name__ == "__main__":
    raw_scores = np.loadtxt('raw_scores.txt').tolist()
    genders = []
    with open('genders.txt', 'r') as file:
        for line in file:
            curr = line[:-1]
            genders.append(curr)

    gender_preferences = []
    with open('gender_preferences.txt', 'r') as file:
        for line in file:
            curr = line[:-1]
            gender_preferences.append(curr)

    gs_matches = run_matching(raw_scores, genders, gender_preferences)

    if gs_matches is None:
        print(f'No possible matchings were found')
    else:
        check_matching(gs_matches, genders, gender_preferences)
