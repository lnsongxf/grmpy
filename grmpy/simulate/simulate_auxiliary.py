""" This module provides auxiliary functions for the simulate.py module. It includes simulation
processes of the unobservable and endogeneous variables of the model as well as functions regarding
the info file output.
"""
import pandas as pd
import numpy as np
from scipy.stats import norm


def simulate_covariates(init_dict, cov_type, num_agents):
    """The function simulates the covariate variables for the cost and the output."""
    num_covar = init_dict[cov_type]['all'].shape[0]

    means = np.tile(0.0, num_covar)
    covs = np.identity(num_covar)
    X = np.random.multivariate_normal(means, covs, num_agents)
    X[:, 0] = 1.0
    for i in range(num_covar):
        if isinstance(init_dict[cov_type]['types'][i], list):
            if i != 0:
                frac = init_dict[cov_type]['types'][i][1]
                binary = np.random.binomial(1, frac, size=num_agents)
                X[:, i] = binary
    return X


def simulate_unobservables(covar, vars_, num_agents):
    """The function simulates the unobservable error terms."""
    # Create a Covariance matrix
    cov_ = np.diag(vars_)

    cov_[0, 1], cov_[1, 0] = covar[0], covar[0]
    cov_[0, 2], cov_[2, 0] = covar[1], covar[1]
    cov_[1, 2], cov_[2, 1] = covar[2], covar[2]

    assert np.all(np.linalg.eigvals(cov_) >= 0)
    U = np.random.multivariate_normal([0.0, 0.0, 0.0], cov_, num_agents)

    V = U[0:, 2] - U[0:, 1] + U[0:, 0]
    return U, V


def simulate_outcomes(exog, err, coeff):
    """The function simulates the potential outcomes Y0 and Y1, the resulting treatment dummy D and
    the realized outcome Y.
    """
    # individual outcomes
    Y_0, Y_1 = np.add(
        np.dot(coeff[0], exog[0].T), err[0:,0]), np.add(np.dot(coeff[1], exog[0].T), err[0:, 1])
    cost = np.add(np.dot(coeff[2], exog[1].T), err[0:, 2])

    # Calculate expected benefit and the resulting treatment dummy
    benefits = np.subtract(Y_1, Y_0)
    D = np.array((benefits - cost > 0).astype(int))

    # Observed outcomes
    Y = D * Y_1.T + (1 - D) * Y_0.T

    return Y, D, Y_1, Y_0

def write_output(end, exog, err, source):
    """The function converts the simulated variables to a panda data frame and saves the data in a
    txt and a pickle file.
    """
    column = ['Y', 'D']

    # Stack arrays
    data = np.column_stack((end[0], end[1], exog[0], exog[1], end[2], end[3]))
    data = np.column_stack((data, err[0][0:, 0], err[0][0:, 1], err[0][0:, 2], err[1]))

    # List of column names
    for i in range(exog[0].shape[1]):
        str_ = 'X_' + str(i)
        column.append(str_)
    for i in range(exog[1].shape[1]):
        str_ = 'Z_' + str(i)
        column.append(str_)
    column += ['Y1', 'Y0', 'U0', 'U1', 'UC', 'V']

    # Generate data frame, save it with pickle and create a txt file
    df = pd.DataFrame(data=data, columns=column)
    df['D'] = df['D'].apply(np.int64)
    df.to_pickle(source + '.grmpy.pkl')

    with open(source + '.grmpy.txt', 'w') as file_:
        df.to_string(file_, index=False, header=True, na_rep='.', col_space=15)

    return df


def print_info(data_frame, coeffs, file_name):
    """The function writes an info file for the specific data frame."""

    with open(file_name + '.grmpy.info', 'w') as file_:

        # First we note some basic information ab out the dataset.
        header = '\n\n Number of Observations \n\n'
        file_.write(header)

        info_ = [data_frame.shape[0], (data_frame['D'] == 1).sum(), (data_frame['D'] == 0).sum()]

        fmt = '  {:<10}' + ' {:>20}' * 1 + '\n\n'
        file_.write(fmt.format(*['', 'Count']))

        for i, label in enumerate(['All', 'Treated', 'Untreated']):
            str_ = '  {:<10} {:20}\n'
            file_.write(str_.format(*[label, info_[i]]))

        # Second, we describe the distribution of outcomes and effects.
        for label in ['Outcomes', 'Effects']:

            header = '\n\n Distribution of ' + label + '\n\n'
            file_.write(header)

            fmt = '  {:<10}' + ' {:>20}' * 5 + '\n\n'
            args = ['', 'Mean', 'Std-Dev.', '25%', '50%', '75%']
            file_.write(fmt.format(*args))

            for group in ['All', 'Treated', 'Untreated']:

                if label == 'Outcomes':
                    object = data_frame['Y']
                elif label == 'Effects':
                    object = data_frame['Y1'] - data_frame['Y0']
                else:
                    raise AssertionError

                if group == 'Treated':
                    object = object[data_frame['D'] == 1]
                elif group == 'Untreated':
                    object = object[data_frame['D'] == 0]
                else:
                    pass
                fmt = '  {:<10}' + ' {:>20.4f}' * 5 + '\n'
                info = list(object.describe().tolist()[i] for i in [1, 2, 4, 5, 6])
                if 0 in info_:
                    for i in range(2):
                        if i == 0:
                            zero = 'Treated'
                        elif i == 1:
                            zero= 'Untreated'
                        if info_[i+1] == 0:
                            if group == zero:
                                fmt = '  {:<10}' + ' {:>20}' * 5 + '\n'
                                info = ['---'] * 5
                            else:
                                fmt = '  {:<10}' + ' {:>20.4f}' + ' {:>20}' + ' {:>20.4f}' * 3 \
                                      + '\n'
                                info[1] = '---'
                            file_.write(fmt.format(*[group] + info))
                else:
                    file_.write(fmt.format(* [group] + info))

        # Implement MTE information
        header ='\n\n MTE Information \n\n'
        file_.write(header)
        fmt = '  {:<10}' + ' {:>20}' * 21 + '\n\n'
        quantiles = [1] + np.arange(5, 100, 5).tolist() + [99]
        args = ['']
        for i in quantiles:
            args += [str(i) + '%']
        file_.write(fmt.format(*args))
        quantiles = [i * 0.01 for i in quantiles]
        x = data_frame.filter(regex=r'^X\_', axis=1)
        values = mte_information(coeffs[:2], coeffs[3][3:], coeffs[3][:3], quantiles, x)
        values = ['MTE'] + values
        fmt = '  {:<10}' + ' {:>20.4f}' * 21 + '\n\n'
        file_.write(fmt.format(*values))

        # Next we write out the parametrization of the model.
        header = '\n\n Parametrization \n\n'
        file_.write(header)
        str_ = '  {0:>10} {1:>20}\n\n'.format('Identifier', 'Value')
        file_.write(str_)

        value = np.append(np.append(coeffs[0], coeffs[1]), np.append(coeffs[2], coeffs[3]))
        len_ = len(value) - 1
        for i in range(len_):
            file_.write('  {0:>10} {1:>20.4f}\n'.format(str(i), value[i]))


def mte_information(para, cov, var, quantiles, x):
    """The function calculates the marginal treatment effect for pre specified quantiles of the
    collected unobservable variables.
    """
    MTE = []
    # Calculate the variance of V:
    var_v = var[0] + var[1] + var[2] + - 2 + cov[0] - 2 * cov[2] + 2* cov[1]
    cov_v1 =  (cov[0] + cov[2] - var[1]) / var_v
    cov_v0 =  (cov[1] + var[0] - cov[0]) / var_v
    para_diff = para[1] - para[0]

    for i in quantiles:
        MTE += [np.mean(np.dot(para_diff, x.T)) - (cov_v1 - cov_v0) * norm.ppf(i)]

    return MTE