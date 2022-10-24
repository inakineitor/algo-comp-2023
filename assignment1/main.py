#!usr/bin/env python3
import json
import sys
import os
import statistics

INPUT_FILE = 'testdata.json'  # Constant variables are usually in ALL CAPS

GRADUATION_YEAR_WEIGHT = 0.1
SURVERY_WEIGHT = 0.9


class User:
    def __init__(self, name, gender, preferences, grad_year, responses):
        self.name = name
        self.gender = gender
        self.preferences = preferences
        self.grad_year = grad_year
        self.responses = responses


class GlobalParameters:
    def __init__(self, users):
        user_graduations_years = [user.grad_year for user in users]
        self.graduation_year_dist_parameters = {}
        # Encode normal distribution mean
        self.graduation_year_dist_parameters['mean'] = statistics.mean(user_graduations_years)
        # Encode normal distribution standard deviation
        self.graduation_year_dist_parameters['std_dev'] = statistics.stdev(
            user_graduations_years)


def compute_global_parameters(global_parameters, users):
    # YOUR CODE HERE
    return 0

# Takes in two user objects and outputs a float denoting compatibility


def compute_score(user1, user2):
    # Check for gender compatibility
    # I took gender compatibility to be a boolean factor. Either they are compatible or not,
    # but the number or order of preferences a user has does not impact the score.
    if user1.gender not in user2.preferences or user2.gender not in user1.preferences:
        return 0  # If genders are incompatible, then there is abolutely no compatibility

    # Check for graduation year compatibility
    graduation_year_compatibility_score = 1 - \
        abs(user1.grad_year - user2.grad_year) / \
        global_parameters.avg_grad_year

    # Check for survey compatibility
    survey_compatibility_score = 0

    total_weights = GRADUATION_YEAR_WEIGHT + SURVERY_WEIGHT
    weighted_score = (graduation_year_compatibility_score * GRADUATION_YEAR_WEIGHT +
                      survey_compatibility_score * SURVERY_WEIGHT) / total_weights
    # YOUR CODE HERE
    return 0


if __name__ == '__main__':
    # Make sure input file is valid
    if not os.path.exists(INPUT_FILE):
        print('Input file not found')
        sys.exit(0)

    users = []
    with open(INPUT_FILE) as json_file:
        data = json.load(json_file)
        for user_obj in data['users']:
            new_user = User(user_obj['name'], user_obj['gender'],
                            user_obj['preferences'], user_obj['gradYear'],
                            user_obj['responses'])
            users.append(new_user)

    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            user1 = users[i]
            user2 = users[j]
            score = compute_score(user1, user2)
            print('Compatibility between {} and {}: {}'.format(
                user1.name, user2.name, score))
