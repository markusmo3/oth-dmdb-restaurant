#%% [markdown]
# Get Data and import modules

#%%
import pandas as pd

data = pd.read_csv('../../data/ecommerce_data.csv')
data.head()
#%% [markdown]
# Because some machine learning algorithms can't handle categorized columns it's a good idea to encode them  <br>
# Often one-hot-encoding is a good choice for this <br>
# one-hot-encoding means that each category of a column gets its own column and if the category is selected in the corresponding column the dummy column is marked with an one and all other dummy columns are zero <br>
# pandas has a get_dummies function to archive this <br>
# There are other methods to encode categorized data. 

#%%
# Define new column names
dummie_features = ['T0to6', 'T6to12', 'T12to18', 'T18to24']
# dummiefy time_of_day
dummies = pd.get_dummies(data.time_of_day, prefix=dummie_features)
#insert the one-hot-encoded features in our dataframe
data[dummie_features] = dummies
#drop the old column
data = data.drop(labels=['time_of_day'], axis=1)
data.head()
#%% [markdown]
# For some machine learning algorithms (unlike xgboost i.e.) it's also important to handle NaN values in the dataset. <br>
# There are some methods to handle them:  <br>
#     - Simply remove rows with NaN values (not recommended)
#     - Fill NaN Values with the median of all non NaN values 
#     - Fill NaN Values with the help of some special algorithm 

#%%
data.loc[0:10, 'visit_duration'] = None
data.head(12)
#%% [markdown]
# Check for NaN values

#%%
pd.isna(data).head()
#%% [markdown]
# Now let's simply drop the NaN value rows

#%%
data.dropna(axis=0).head()
#%% [markdown]
# Scikit-learn has some useful features to fill NaN values but keep in mind that scikit-learn  returns a numpy array. So you have to convert it back to a pandas dataframe if you want to do additional things with it.
# Pandas as well has a fillna() function. we will use this one to fill the missing values with the mean of our visit_duration column
# For furher information refer to he corresponding documentation 
# http://scikit-learn.org/stable/modules/impute.html
# https://pandas.pydata.org/pandas-docs/version/0.22/generated/pandas.DataFrame.fillna.html

#%%
import numpy as np

data.visit_duration = data.visit_duration.fillna(np.mean(data.visit_duration))
#or: data.visit_duration = data.visit_duration.fillna(np.mean(data.visit_duration.mean)) 
data.head()
#%% [markdown]
# For training our model it's most of the time necessary to split it into features and labels
# The columns which are used to predict are called features and in code they are marked as X
# The column which should be predicted by our algorithm is called label and in code it's y 

#%%
features = ['is_mobile', 'n_products_viewed', 'visit_duration','is_returning_visitor', 'T0to6','T6to12', 'T12to18', 'T18to24' ]
X = data[features]
#The above 2 rows can also be written as
X = data.drop('user_action', axis=1)
y = data.user_action
#%% [markdown]
# Now we want to split our X and y into training and test data to test our machine learning model after it's trained
# sklearn has a function for doing this
# for test purpose it's important to add the random_state parameter to ensure that our dataset is equally split each time we call this function

#%%
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)



#%%


#%%
