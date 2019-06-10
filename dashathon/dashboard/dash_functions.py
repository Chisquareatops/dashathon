"""This module provides helper functions to perform the data selection and
analytics on the combined pool of marathon data, based on user selections."""

import numpy as np
import math

SECONDS = 60.0

def get_subset(df, age, gender):
    """
    This function returns a subset of a data frame based on gender and/or age.
    Parameters:
    df (dataframe): a dataframe containing marathon split times for individuals
    age (string): an age group, originally selcted via user input
    gender (string): a gender category, originally se3lected via user input
    Returns:
    subset (dataframe): a dataframe containing times for selected individuals
    """
    if age == 'all':
        if gender == 'all':
            subset = df.copy()
        else:
            subset = df.loc[(df['gender'] == str(gender))].copy()
    elif gender == 'all':
        subset = df.loc[(df['age_range'] == str(age))].copy()
    else:
        subset = df.loc[(df['gender'] == str(gender))
                        & (df['age_range'] == age)].copy()
    return subset

def get_top(df, quantile):
    """
    This function returns the top X% of runners based on finish time.
    Parameters:
    df (dataframe): a dataframe containing marathon split times for individuals
    quantile (float): a decimal specifying the desired cutoff for performance
    Returns:
    subset_winners (dataframe): dataframe containing times for top individuals
    """
    quantile_value = df["overall"].quantile(quantile)
    subset_winners = df.loc[(df["overall"] <= quantile_value)].copy()
    return subset_winners

def get_user_paces(user_splits):
    """
    This function returns paces for a user based on their input split times.
    Parameters:
    user_splits (array): an array of strings giving user split times
    Returns:
    user_numeric (array): an array of floats giving user paces in minutes/km
    """
    split_numeric = [5, 10, 15, 20, 21.082, 25, 30, 35, 40, 42.165]
    user_numeric = []
    for i in range(len(user_splits)):
        try:
            numbers = user_splits[i].split(":")
            if len(numbers) == 2:
                mins = float(numbers[0])
                secs = float(numbers[1]) / SECONDS
                user_numeric.append((mins + secs) / split_numeric[i])
            elif len(numbers) == 3:
                hours = float(numbers[0]) * SECONDS
                mins = float(numbers[1])
                secs = float(numbers[2]) / SECONDS
                user_numeric.append((hours + mins + secs) / split_numeric[i])
            else:
                user_numeric.append(np.nan)
        # in case of ANY failure simply insert a nan for this split
        except Exception:
            user_numeric.append(np.nan)
    return user_numeric

def get_user_times(user_splits):
    """
    This function returns times for a user based on their input split times.
    It differs from get_user_paces in that it returns total times in seconds,
    not pace in minutes/km.
    Parameters:
    user_splits (array): an array of strings giving user split times
    Returns:
    user_numeric_time (array): an array of floats giving user times in seconds
    """
    user_numeric_time = []
    for i in range(len(user_splits)):
        try:
            numbers = user_splits[i].split(":")
            if len(numbers) == 2:
                mins = float(numbers[0])
                secs = float(numbers[1]) / SECONDS
                user_numeric_time.append(mins + secs)
            elif len(numbers) == 3:
                hours = float(numbers[0]) * SECONDS
                mins = float(numbers[1])
                secs = float(numbers[2]) / SECONDS
                user_numeric_time.append(hours + mins + secs)
            else:
                user_numeric_time.append(np.nan)
        # in case of ANY failure simply insert a nan for this split
        except Exception:
            user_numeric_time.append(np.nan)
    return user_numeric_time

def get_mean_pace(df, split_list):
    """
    This function returns mean paces at various splits for a group of runners.
    Parameters:
    df (dataframe): contains split times for individual runners
    Returns:
    mean_paces (array): an array of floats, the mean pace at each split
    for the group of runners contained in the dataframe
    """
    split_numeric = [5, 10, 15, 20, 21.082, 25, 30, 35, 40, 42.165]
    mean_paces = []
    for i in range(len(split_list)):
        mean_time = df[split_list[i]].mean(axis=0) / SECONDS
        mean_pace = mean_time / split_numeric[i]
        mean_paces.append(mean_pace)
    return mean_paces

def get_split_ratio(df):
    """
    This function returns a copy of a data frame with a new column
    for split ratios.
    Parameters:
    df (dataframe): contains split times for individual runners
    Returns:
    df_new (dataframe): a copy of the passed data frame which contains one
    new column; the split ratio comparing the second half of each individual's
    marathon to the first half.
    """
    df_new = df.copy()
    df_new["split_ratio"] = (df_new["official_time"] - df_new["half"]) / (
        df_new["half"]
    )
    return df_new

def get_fatigue_zone(user_numeric, split_list):
    """
    This function returns the name of the split at which a user ran slowest.
    Parameters:
    user_splits (array): an array of strings giving user split times
    user_numeric (array): an array of floats giving user paces in min/km
    Returns:
    fatigue_zone (string): the name of the split where user's pace slowest
    """
    for i in range (len(split_list)):
        if math.isnan(user_numeric[i]):
            user_numeric[i] = 0
    slowest_pace = max(user_numeric)
    slowest_pace_index = user_numeric.index(slowest_pace)
    fatigue_zone = split_list[slowest_pace_index]
    return fatigue_zone
