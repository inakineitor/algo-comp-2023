#!usr/bin/env python3
from collections import defaultdict
import json
import sys
import os
import statistics
import numpy as np
import scipy.stats

INPUT_FILE = 'testdata.json'  # Constant variables are usually in ALL CAPS

GRADUATION_YEAR_WEIGHT = 0.05
SURVERY_WEIGHT = 0.95


class User:
    def __init__(self, name, gender, preferences, grad_year, responses):
        self.name = name
        self.gender = gender
        self.preferences = preferences
        self.grad_year = grad_year
        self.responses = responses


class GlobalParameters:
    def __init__(self, users):
        assert(len(users) > 0)
        user_graduations_years = [user.grad_year for user in users]
        # Encode normal distribution mean
        graduation_year_mean = statistics.mean(
            user_graduations_years)
        # Encode normal distribution standard deviation
        graduation_year_std_dev = statistics.stdev(
            user_graduations_years)
        self.graduation_year_distribution = scipy.stats.norm(
            graduation_year_mean, graduation_year_std_dev)

        # Generate survey question weights
        self.number_of_survey_questions = len(users[0].responses)
        survey_question_response_frequency = [
            defaultdict(int) for _ in range(self.number_of_survey_questions)]
        for user in users:
            for i, answer in enumerate(user.responses):
                survey_question_response_frequency[i][answer] += 1

        self.survey_question_response_weights = [defaultdict(
            lambda: float(1)) for _ in range(self.number_of_survey_questions)]
        for i, response_frequency in enumerate(survey_question_response_frequency):
            total_responses = sum(response_frequency.values())
            for answer, frequency in response_frequency.items():
                self.survey_question_response_weights[i][answer] = 1 / \
                    (1 + frequency / total_responses)


def compute_score(user1, user2, global_parameters):  # Takes in two user objects and outputs a float denoting compatibility
    # Check for gender compatibility
    # I took gender compatibility to be a boolean factor. Either they are compatible or not,
    # but the number or order of preferences a user has does not impact the score.
    if user1.gender not in user2.preferences or user2.gender not in user1.preferences:
        return 0  # If genders are incompatible, then there is abolutely no compatibility

    # Check for graduation year compatibility
    # If the graduations years are close to the mean, then the score wil be sensitive to small differences, which reflects reality.
    # If you are still in school, each year matters a lot. It would be uncommon for a freshman to be compatible with a senior.
    # However if someone is a few years out of school, then the difference in graduation years is not as important.
    #! If everyone is guaranteed to still be in school, then a formula such as $abs(user2_year - user1_year)^2$ could be used.
    graduation_year_compatibility_score = 1 - abs(
        global_parameters.graduation_year_distribution.cdf(user1.grad_year)
        - global_parameters.graduation_year_distribution.cdf(user2.grad_year)
    )

    # Check for survey compatibility
    survey_compatibility_score = 0
    for i, (user1_answer, user2_answer) in enumerate(zip(user1.responses, user2.responses)):
        if user1_answer == user2_answer:
            survey_compatibility_score += global_parameters.survey_question_response_weights[i][user1_answer]

    # if '[TEST]' in user1.name:
    #     print(global_parameters.survey_question_response_weights)
    #     print(
    #         f'Graduation year compatibility score: {graduation_year_compatibility_score}')
    #     print(f'Survey compatibility score: {survey_compatibility_score}')
    
    survey_compatibility_score /= global_parameters.number_of_survey_questions # Normalize the score to [0, 1] #! It will actually never reach 1



    total_weights = GRADUATION_YEAR_WEIGHT + SURVERY_WEIGHT
    weighted_score = (graduation_year_compatibility_score * GRADUATION_YEAR_WEIGHT +
                      survey_compatibility_score * SURVERY_WEIGHT) / total_weights

    return weighted_score


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

    global_parameters = GlobalParameters(users)

    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            user1 = users[i]
            user2 = users[j]
            score = compute_score(user1, user2, global_parameters)
            print('Compatibility between {} and {}: {}'.format(
                user1.name, user2.name, score))
