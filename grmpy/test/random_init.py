"""The module provides a random dictionary generating process for test purposes."""
import uuid

import numpy as np


def constraints(probability=0.1, is_zero=True, agents=None, seed=None):
    """The constraints function returns an dictionary that provides specific characteristics for the
    random dictionary generating process.
    """
    constraints_dict = dict()
    constraints_dict['DETERMINISTIC'] = np.random.random_sample() < probability
    if not constraints_dict['DETERMINISTIC'] and is_zero:
        constraints_dict['IS_ZERO'] = np.random.random_sample() < probability / (1 - probability)
    else:
        constraints_dict['IS_ZERO'] = False
    if agents is None:
        constraints_dict['AGENTS'] = np.random.randint(1, 1000)
    else:
        constraints_dict['AGENTS'] = agents
    if seed is None:
        constraints_dict['SEED'] = np.random.randint(1, 10000)
    else:
        constraints_dict['SEED'] = seed

    return constraints_dict


def generate_random_dict(constraints_dict=None):
    """The function generates a random initialization dictionary."""

    if constraints_dict is not None:
        assert isinstance(constraints_dict, dict)
    else:
        constraints_dict = constraints()

    is_deterministic = constraints_dict['DETERMINISTIC']

    is_zero = constraints_dict['IS_ZERO']

    agents = constraints_dict['AGENTS']

    seed = constraints_dict['SEED']

    source = my_random_string(8)

    dict_ = {}
    treated_num = np.random.randint(1, 10)
    cost_num = np.random.randint(1, 10)
    # Coefficients
    for key_ in ['UNTREATED', 'TREATED', 'COST']:

        dict_[key_] = {}

        if key_ in ['UNTREATED', 'TREATED']:

            if not is_zero:
                dict_[key_]['coeff'] = np.random.normal(
                    0.0, 2., [treated_num]).tolist()
            else:
                dict_[key_]['coeff'] = np.array([0] * treated_num).tolist()
        else:

            if not is_zero:
                dict_[key_]['coeff'] = np.random.normal(0., 2., [cost_num]).tolist()
            else:
                dict_[key_]['coeff'] = np.array([0] * cost_num).tolist()

    # Simulation parameters
    dict_['SIMULATION'] = {}
    for key_ in ['agents', 'source', 'seed']:
        if key_ == 'seed':
            dict_['SIMULATION'][key_] = seed
        elif key_ == 'agents':
            dict_['SIMULATION'][key_] = agents
        else:
            dict_['SIMULATION'][key_] = source

    dict_['DIST'] = {}

    # Variance and covariance parameters
    if not is_deterministic:
        a = np.random.rand(3, 3)
        b = np.dot(a, a.transpose())
    else:
        b = np.zeros((3, 3))

    dict_['DIST']['coeff'] = []

    for i in range(3):
        dict_['DIST']['coeff'].append(b[i, i])

    dict_['DIST']['coeff'].append(b[1, 0])
    dict_['DIST']['coeff'].append(b[2, 0])
    dict_['DIST']['coeff'].append(b[2, 1])

    dict_['DIST']['coeff'] = np.asarray(dict_['DIST']['coeff']).tolist()

    print_dict(dict_)

    return dict_


def print_dict(dict_, file_name='test'):
    """The function creates an init file from a given dictionary."""

    labels = ['SIMULATION', 'TREATED', 'UNTREATED', 'COST', 'DIST']

    with open(file_name + '.grmpy.ini', 'w') as file_:

        for label in labels:

            file_.write(label + '\n\n')

            if label == 'SIMULATION':

                structure = ['agents', 'seed', 'source']

                for key_ in structure:

                    if key_ == 'source':
                        str_ = '{0:<25} {1:20}\n'

                        file_.write(str_.format(key_, dict_[label][key_]))
                    else:
                        str_ = '{0:<10} {1:20}\n'

                        file_.write(str_.format(
                            key_, dict_['SIMULATION'][key_]))

            elif label in ['TREATED', 'UNTREATED', 'COST', 'DIST']:
                key_ = 'coeff'

                for i in range(len(dict_[label][key_])):
                    str_ = '{0:<10} {1:20.4f}\n'
                    file_.write(str_.format(key_, dict_[label]['coeff'][i]))

            file_.write('\n')


def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.
