# un_pop_analysis.py
# Muhammad Daud Sheikh, Ateeb Goraya
# June 16th, 2021

# A program to allow users to input a user defined UN sub-region and country within this sub-region. It outputs statistical data relating to fertility and population growth

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')




'''
The check_user_sub-region function checks if the user inputted a sub-region that is contained within the merged UN dataset

'''

def check_user_subregion(data):

        while True:
            user_s = input('\nPlease enter valid UN Sub-Region that you wish to know details about: ') # User Input
            try:
                if user_s in data.index.get_level_values(1):
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\nThe UN Sub-Region is not in the UN Database, please try again.') 
        return user_s

'''
The check_user_country function checks if the user inputted country is contained within the UN subregion specified by the user earlier

'''

def check_user_country(data):

        while True:
            user_c = input('\nPlease enter valid Country within the UN subregion specified above that you wish to know details about: ') # User Input
            try:
                if user_c in data.index.get_level_values(2):
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\nThe Country entered is not in the UN Sub-Region Specified, please try again.') 
        return user_c


def main():

    # STAGE 1: Import data

    print('\n\n') # Adding line for formatting
    print("ENSF 592 World Data")
    print('\n\n') # Adding line for formatting

    world_data_uncodes = pd.read_excel("C:/Users/sheik/Documents/ENSF 592/Projects/project-p21-group-27/UN Population Datasets/UN Codes.xlsx", # Importing the UN codes that categorize country data to UN regions and sub-tegions
                            dtype = {'Country': str, 'UN Region': str, 'UN Sub-Region': str})
    world_data1 = pd.read_excel("C:/Users/sheik/Documents/ENSF 592/Projects/project-p21-group-27/UN Population Datasets/UN Population Dataset 1.xlsx", 
                            dtype = {'Code': int, 'Region/Country/Area': str, 'Year': str, 'Series': str, 'Value': float}).drop('Code', axis = 1) # Importing UN dataset 1 that contains fertility and other HDI information
    world_data2 = pd.read_excel("C:/Users/sheik/Documents/ENSF 592/Projects/project-p21-group-27/UN Population Datasets/UN Population Dataset 2.xlsx", 
                            dtype={'Code': int, 'Region/Country/Area': str, 'Year': str, 'Series': str, 'Value': float}).drop('Code', axis = 1) # Importing UN dataset 2 that contains population and geographical information



    # STAGE 2 Dataframe Creation

    world_data3 = pd.concat([world_data1, world_data2]).sort_values(by=['Region/Country/Area','Year','Series']) # Concating the 2 datasets in order to all all the statistical parameters in the "series" column
    world_data = pd.merge(world_data_uncodes,world_data3, how='inner', left_on='Country', right_on='Region/Country/Area').drop('Region/Country/Area', axis=1) # Merging the concatenated dataset by only keeping only rows that match the UN Codes "Country" and Datasets 1 and 2 "Region/Country/Area"
    world_data = world_data.set_index(['UN Region', 'UN Sub-Region', 'Country', 'Year','Series']) # Setting the hierarchical index according the column titles shown in the command on the left

    world_data_pivot = pd.pivot_table(world_data, values='Value', index = ['UN Region', 'UN Sub-Region', 'Country', 'Year'], columns='Series') # Making a new pivot table out of the merged data with the indexs being the hierarchical data and columns being 
     
    # Add two new columns

    # Calculating total urban population from capital city and capital city population as a percentage of the whole urban population
    world_data_pivot['Total Urban Population (thousands)'] = world_data_pivot['Capital city population (thousands)']/(world_data_pivot['Capital city population (as a percentage of total urban population)']/100) 


    world_data_pivot['Gender with higher life expectancy'] = world_data_pivot['Life expectancy at birth for females (years)'] # Initializing column 'Life expectancy at birth for females (years)'

    # Checking to see which gender has a longer life expectancy at birth for a given country for each year in the UN dataset
    world_data_pivot['Gender with higher life expectancy'].astype(str) # Setting data type in column as string
    idx = world_data_pivot.index[world_data_pivot['Life expectancy at birth for females (years)'].notnull()] # Using masking to find all indices in the 'Life expectancy at birth for females (years)' column that has real values by using notnull()

    for i in idx: # Iterating over all the indexes that were found to contain values in the 'Life expectancy at birth for females (years)' column

        if world_data_pivot['Life expectancy at birth for females (years)'][i] > world_data_pivot['Life expectancy at birth for males (years)'][i]:
            world_data_pivot['Gender with higher life expectancy'][i] = 'Female'

        elif world_data_pivot['Life expectancy at birth for females (years)'][i] < world_data_pivot['Life expectancy at birth for males (years)'][i]:
            world_data_pivot['Gender with higher life expectancy'][i] = 'Male'

    


    # STAGE 3: User Entry

    user_subregion = check_user_subregion(world_data) # Using the check_user_subregion function to do the error handling for the user input of the UN sub-region
    sub_region_stats = world_data.loc[world_data.index.get_level_values('UN Sub-Region') == user_subregion] # Assigning new variable to data only concerning user defines sub-region
    user_country = check_user_country(sub_region_stats) # Using the check_user_subregion function to do the error handling for the user input of the country in the UN sub-region specified
    country_stats = world_data.loc[world_data.index.get_level_values('Country') == user_country] # Assigning new variable to data only concerning user defines country


    # STAGE 4: Analysis & Calculation

    print('\n')
    print('=' * 200) # printing line to organize data between user input and fertility rate and population increase output

    # Shows feritility rate (children/women) of the user specified UN Sub-Region
    print('\n')
    print('The following list shows fertiility rates and population increase rate of the countries specified in UN Sub-Region ' + user_subregion + ' in descending order: ')
    print('\n')

    # This command assigns @parameter: fertility_rank to a ranked dataframe of all countries within the user specified UN sub-region by order of fertility of all years.
    # It does this with a masking operation which return a boolean array of indices where the user specified UN Region is true and sorts in descending order base on the 'Total fertility rate (children per women)' column in the data
    fertility_rank = world_data_pivot.loc[world_data_pivot.index.get_level_values('UN Sub-Region') == user_subregion].sort_values(by='Total fertility rate (children per women)', ascending=False)

    #This find the maximum fertility and population increase rate values of each country regardless of year. This is done by grouping at year level (level=2) and applying the .apply(max).sort() methods to the data
    fertility_max = fertility_rank[['Total fertility rate (children per women)','Population annual rate of increase (percent)']].groupby(level=2).apply(max).sort_values(by='Total fertility rate (children per women)' ,ascending=False)
    print(fertility_max)

    print('\n\n')

    # Shows the fertility and population increase rate data of the user specified country using a pivot table
    print('\nThe following statistics shows fertility and population increase rate for ' + user_country + ': \n')
    country_fertility_pop = country_stats.unstack()['Value'].loc[:,['Total fertility rate (children per women)','Population annual rate of increase (percent)']]#, 'Population annual rate of increase (percent)']) # printing country stats
    print(country_fertility_pop.dropna())
    print('\n\n')

    # Calculating the overall mean fertility data for the user specified UN subregion
    world_subregion_mean_all = world_data_pivot.groupby(level='UN Sub-Region').mean()
    world_subregion_mean_fertility = world_subregion_mean_all.loc[user_subregion, 'Total fertility rate (children per women)']
    print('The mean fertility rate for the UN Sub-Region specified is ' + str(round(world_subregion_mean_fertility, 2)))
    print('\n')

    # Calculating the overall mean fertility data for the user specified country
    country_mean_all = world_data_pivot.groupby(level='Country').mean()
    country_mean_fertility = country_mean_all.loc[user_country, 'Total fertility rate (children per women)']
    print('The mean fertility rate for the Country specified over 2005, 2010, 2015 and 2018 is ' + str(round(country_mean_fertility, 2)))
    
    print('\n')
    print('=' * 200)
    print('\n')

    # This command outputs a pivot table with a list of common statistical parameters using the describe method for each of the UN statistical parameter value in the merged UN dataset
    world_data_describe = world_data_pivot.describe()
    print('The following is the basic statistical data for the various series in the UN dataset: \n')
    print(world_data_describe.transpose()) # The table is transposed for easier comprehension of data statistics
    
    # Stage 5 Export & Matplotlib

    # Exporting pivot table with all merged UN data to the file "group27_output_export"
    world_data_pivot.to_excel('group27_output_export.xlsx')

    # Converting countries within the user specified sub-region from indices to list and setting as the x-axis values of bar graph
    # Converting fertility rates for the countries within the user specified sub-region from a dataframe to float list
    plt.bar(fertility_max['Total fertility rate (children per women)'].keys().tolist(), fertility_max['Total fertility rate (children per women)'].reset_index()['Total fertility rate (children per women)'].values)
    plt.xlabel('Countries within user specified Sub-Region') # Adding plot X-axis label
    plt.ylabel('Total Fertility Rate (Children/Women)') # Adding plot Y-axis label
    plt.title('Total Fertility Rate for Countries within UN Sub-Regions') # Adding plot title
    plt.show()
    


if __name__ == '__main__':
    main()

