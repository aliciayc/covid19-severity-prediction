import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from functions import merge_data
from functions import load_medicare_data
from functions import load_respiratory_disease_data
from functions import load_tobacco_use_data
from os.path import join as oj
from sklearn.model_selection import train_test_split
#from load_data import load_county_level

outcome_cases = '#Cases_3/22/2020'
outcome_deaths = '#Deaths_3/22/2020'

def load_county_level(ahrf_data = 'data/hrsa/data_AHRF_2018-2019/processed/df_renamed.pkl',
        usafacts_data_cases = 'data/usafacts/confirmed_cases_mar23.csv',
        usafacts_data_deaths = 'data/usafacts/deaths_mar23.csv',
        diabetes = 'data/diabetes/DiabetesAtlasCountyData.csv',
        voting = 'data/voting/county_voting_processed.pkl',
        icu = 'data/medicare/icu_county.csv',
        heart_disease_data = "data/cardiovascular_disease/heart_disease_mortality_data.csv",
        stroke_data = "data/cardiovascular_disease/stroke_mortality_data.csv"):
    print('loading county level data...')
    df = merge_data.merge_data(ahrf_data=ahrf_data, 
                               usafacts_data_cases=usafacts_data_cases,
                               usafacts_data_deaths=usafacts_data_deaths,
                               medicare_group="All Beneficiaries",
                               voting=voting,
                               icu=icu,
                               resp_group="Chronic respiratory diseases",
                               heart_disease_data=heart_disease_data,
                               stroke_data=stroke_data,
                               diabetes=diabetes) # also cleans usafacts data
    
    # basic preprocessing
    df = df.sort_values(outcome_deaths, ascending=False)
    df = df.infer_objects()
    
    # add features
    df['FracMale2017'] = df['PopTotalMale2017'] / (df['PopTotalMale2017'] + df['PopTotalFemale2017'])
    df['#FTEHospitalTotal2017'] = df['#FTETotalHospitalPersonnelShortTermGeneralHospitals2017'] + df['#FTETotalHospitalPersonnelSTNon-Gen+LongTermHosps2017']

    return df


def merge_hospital_and_county_data(hospital_info_keys, county_info_keys):
    
    hospitals = pd.read_csv("data/hospital_level_info/02_hospital_info.csv")
    county_to_fips = dict(zip(zip(hospitals['COUNTY'], hospitals['STATE']), hospitals['COUNTYFIPS']))
    hospital_level = pd.read_csv("data/hospital_level_info/03_hospital_level_info_merged.csv")
    def map_county_to_fips(name, st):
        if type(name) is str:
            #name = re.sub('[^a-zA-Z]+', '', county_name).lower()
            if (name, st) in county_to_fips and county_to_fips[(name, st)] != "NOT AVAILABLE":
                return int(county_to_fips[(name, st)])
        return np.nan
    hospital_level['countyFIPS'] = hospital_level.apply(lambda x: map_county_to_fips(x['County Name_y'], x['State_x']), axis=1).astype('float')
    county_level = load_county_level()
    if county_info_keys != 'all':
        county_level = county_level[county_info_keys]
    if hospital_info_keys != 'all':
        hospital_level = hospital_level[hospital_info_keys]
    hospital_county_merged = hospital_level.merge(county_level, how='left', on='countyFIPS')
    return hospital_county_merged



def split_data(df):
    np.random.seed(42)
    countyFIPS = df.countyFIPS.values
    fips_train, fips_test = train_test_split(countyFIPS, test_size=0.25, random_state=42)
    df_train = df[df.countyFIPS.isin(fips_train)]
    df_test = df[df.countyFIPS.isin(fips_test)]
    return df_train, df_test

if __name__ == '__main__':
    df = load_county_level()
    print('loaded succesfully')