#%% [markdown]
# Load e-commerce dataset and print head to verify that it's loaded correctly
#%%
import pandas as pd
data = pd.read_csv('../../data/ecommerce_data.csv')
data.head()
#%% [markdown]
# Select elements by index 
#%%
data.iloc[3]

#%%
data.iloc[[0,3,5]]
#%% [markdown]
# By giving a range in .iloc the first element is included and the last element is excluded

#%%
data.iloc[1:5]
#%% [markdown]
# You can also select single cells by giving a row and column values
# Here it's the value of column 5 and row 3

#%%
data.iloc[3, 5]
#%% [markdown]
# With .loc we can select rows: 
#     - by label/index
#     - with a boolean / conditional lookup+#

#%%
#this wouldn't have worked with iloc
data.loc[3, 'is_mobile']
#%% [markdown]
# Conditional .loc looks like

#%%
data.loc[data['n_products_viewed'] > 3, ['n_products_viewed', 'user_action']].head(10)
#%% [markdown]
# Get the column names of a dataset

#%%
data.columns
#%% [markdown]
# Accessing single or specific columns of a dataset is done like that:

#%%
data[['is_mobile', 'user_action']].head()
#%% [markdown]
# Print description of dataset which contains the count of rows in each column as well as the mean, standard deviation and important quartiles. Calculation for quartiles and theire meaning: <br>
# mean (=Mittelwert != Median): Sum of all value / count of values <br>
# The standard deviation marks the average distance of the values from the mean <br>
# For calculation of quantiles the values in a column are ordered <br>
# even count of rows: <br>
#* 0.25 quantile: data \[round(rowCount*0.25)\] 
#* 0.5 quantile (= median != Mittelwert): 0.5 * (data\[rowCount / 2\] + data\[rowCount / 2 + 1\])
#* 0.75 quantile: data\[round(rowCount*0.75)\] <br>
# odd count of rows: 
#    * 0.25 quantile: data\[round(rowCount*0.25)\] 
#    * 0.5 quantile:  data\[round(rowCount*0.5)\] 
#    * 0.75 quantile: data\[round(rowCount*0.75)\] 

#%%
data.describe()
#%% [markdown]
# data.info() shows us general information about our dataset and its columns like the number of entries, the count of non null rows and the data type of each column

#%%
data.info()
#%% [markdown]
# We can get unique values of a column with .unique()

#%%
data.time_of_day.unique()
#%% [markdown]
# Because our dataset has some categorized numbers which are categorized as integers which is not that good to read we map the integers to strings<br>
# To do this we create two dictionaries which contain the values to map<br>
# After applying our dictionaries we print the head() of our dataset to confirm that it worked out 

#%%
dictTime = {0: '0to6', 1: '6to12', 2: '12to18', 3: '18to24'}
dictAction = {0: 'bounce', 1: 'add_to_cart ', 2: 'begin_checkout', 3: 'finish_checkout'}
data.time_of_day = data.time_of_day.map(dictTime)
data.user_action = data.user_action.map(dictAction)
data.head()
#%% [markdown]
# Now we want to get the count of user_actions at each daytime period
# For this we use the groupby function of pandas

#%%
data2 = data[['time_of_day', 'user_action']].copy()
data2['count'] = 1
data2[['time_of_day','count']].groupby(['time_of_day']).count()
#%% [markdown]
# Now we want to analyze which action users are supposed to do on which daytime <br>
#%%
data2.groupby(['time_of_day', 'user_action']).count()
#%% [markdown]
# Now we analyze the actions of our mobile users

#%%
data2 = data[['is_mobile', 'user_action']].copy()
data2['count'] = 1
data2[['is_mobile', 'count']].groupby(['is_mobile']).count()

#%%
data2.groupby(['is_mobile', 'user_action']).count()
#%% [markdown]
# We can also apply lambda functions (or normal functions) to our dataset

#%%
def double_values(x):
    return x*2
data.apply(double_values).head()
#%% [markdown]
# We can apply lambda functions to single columns as well 
# Here we calculate the visit duration in hours

#%%
data3 = data.copy()
data3['visit_duration'] = data3['visit_duration'].apply(lambda x: x/60)
data3.head()
#%% [markdown]
# Pandas also supports sorting of dataframes by single or multiple columns
# For optimization reasons we can also select the sorting function with kind : {‘quicksort’, ‘mergesort’, ‘heapsort’}

#%%
data3.sort_values(by=['visit_duration'], ascending=False).head()


#%%


#%%


#%%


#%%
