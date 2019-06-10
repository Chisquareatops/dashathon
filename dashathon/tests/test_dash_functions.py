import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
import unittest
import dashathon.dash_functions

class TestDashFunctions(unittest.TestCase):

    # check that the subset function does not remove any rows when
    # age and gender are both 'all'
    def test_subset_nosubset(self):
        df = pd.read_csv('bostonnycchicago.csv')
        age = 'all'
        gender = 'all'
        result = dash_functions.get_subset(df, age, gender)
        self.AssertEqual(df.count, result.count)
    
    # check that there is only one unique value for gender
    # when a specific value for gender is selected
    def test_subset_gender(self):
        df = pd.read_csv('bostonnycchicago.csv')
        age = 'all'
        gender = 'M'
        result = dash_functions.get_subset(df, age, gender)
        genders = result['gender'].unique()
        self.AssertEqual(1, len(genders))
      
    # check that subsetting based on the 75th quantile leaves
    # the expected data
    # this function is not tested on line data because rank duplication
    # and rounding make the exact number of remaining rows hard to predict.
    # please note the function is seeking values below the specified quantile
    # because in terms of rank and pace, lower is better
    def test_get_top(self):
        fake_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temp_df = pd.DataFrame()
        temp_df['overall'] = fake_data
        result = dash_functions.get_top(temp_df, 0.75)
        max_ = result['overall'].max()
        self.AssertEqual(7, max_)

    # call get_user_paces with data that is half valid and half invalid
    # check that resulting list contains five numpy nan values
    def test_user_paces_nans(self):
        user_splits = ['29:32', '55:00', '155:00', '2:0:0', '1:1:1',
                       'two hours', np.nan, '7', ':32', '29:32s']
        result = dash_functions.get_user_paces(user_splits)
        temp_df = pd.DataFrame()
        temp_df['col'] = result
        nans = temp_df['col'].isna().sum()
        self.AssertEqual(5, nans)

    # call get_user_paces with data that is 100%
    # check that result is entirely numeric   
    def test_user_paces_no_nans(self):
        user_splits = ['29:32', '55:00', '155:00', '2:0:0', '1:1:1',
                       '100:00', '00:00', '1:1', '12:12:12', '29:32']
        result = dash_functions.get_user_paces(user_splits)
        temp_df = pd.DataFrame()
        temp_df['col'] = result
        self.AssertEqual(is_numeric_dtype(temp_df['col']), True)
  
    # call get_user_times with data that is half valid and half invalid
    # check that resulting list contains five numpy nan values
    def test_user_times_nans(self):
        user_splits = ['29:32', '55:00', '155:00', '2:0:0', '1:1:1',
                       'two hours', np.nan, '7', ':32', '29:32s']
        result = dash_functions.get_user_times(user_splits)
        temp_df = pd.DataFrame()
        temp_df['col'] = result
        nans = temp_df['col'].isna().sum()
        self.AssertEqual(5, nans)

    # call get_user_times with data that is 100%
    # check that result is entirely numeric
    def test_user_times_no_nans(self):
        user_splits = ['29:32', '55:00', '155:00', '2:0:0', '1:1:1',
                       '100:00', '00:00', '1:1', '12:12:12', '29:32']
        result = dash_functions.get_user_times(user_splits)
        temp_df = pd.DataFrame()
        temp_df['col'] = result
        self.AssertEqual(is_numeric_dtype(temp_df['col']), True)

    # test get_mean_pace function on real data and check for correct
    # number of results
    def test_get_mean_pace_real_data(self):
        df = pd.read_csv('bostonnycchicago.csv')
        split_list = ['5k', '10k', '15k', '20k', 'half', '25k',
                      '30k', '35k', '40k', 'official_time']
        result = dash_functions.get_mean_pace(df, split_list)
        self.AssertEqual(len(result), 10)

    # test get_mean_pace function on real data and check for correct
    # type of results
    def test_get_mean_pace_real_data(self):
        df = pd.read_csv('bostonnycchicago.csv')
        split_list = ['5k', '10k', '15k', '20k', 'half', '25k',
                      '30k', '35k', '40k', 'official_time']
        result = dash_functions.get_mean_pace(df, split_list)
        temp_df = pd.DataFrame()
        temp_df['col'] = result
        self.AssertEqual(is_numeric_dtype(temp_df['col']), True)

    # test get_mean_pace function on synthetic data and check
    # for exact expected results
    def test_get_mean_pace_synth_data(self):
        split_list = ['5k', '10k', '15k', '20k', 'half', '25k',
                      '30k', '35k', '40k', 'official_time']
        df = pd.DataFrame()
        df['5k'] = [300, 300, 300]
        df['10k'] = [300, 300, 300]
        df['15k'] = [1800, 1800, 1800]
        df['20k'] = [200, 600, 1000]
        df['half'] = [0, 0, 0]
        df['25k'] = [1500, 1500, 1500]
        df['30k'] = [0, 0, 0]
        df['35k'] = [0, 0, 0]
        df['40k'] = [-5, 0, 5]
        df['official_time'] = [0, 0, 0]
        result = dash_functions.get_mean_pace(df, split_list)
        test_means = [1.0, 0.5, 2.0, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        self.AssertEqual((result == test_means), True)

    # test get_split_ratio function on synthetic data and check
    # for exact expected results
    def test_get_split_ratio(self):
        df = pd.DataFrame()
        df['half'] = [200]
        df['official_time'] = [300]
        result = dash_functions.get_split_ratio(df)
        self.AssertEqual(result.iloc[0]['split_ratio'], 0.5)
    
    # test get_fatigue_zone function on synthetic data and check
    # for exact expected result
    def test_get_fatigue_zone(self):
        user_numeric = [5, 6, 7, 8, 9, 1, 2, 3, 4, 5]
        split_list = ['5k', '10k', '15k', '20k', 'half', '25k',
                      '30k', '35k', '40k', 'official_time']
        result = dash_functions.get_fatigue_zone(user_numeric, split_list)
        self.AssertEqual(result, 'half')
