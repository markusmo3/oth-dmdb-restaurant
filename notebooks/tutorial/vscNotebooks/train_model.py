#%% [markdown]
# Import libraries and prepare data

#%%
import xgboost as xgb
import pandas as pd 
from sklearn.model_selection import train_test_split
data=pd.read_csv('../data/ecommerce_data.csv')
X = data.drop('user_action', axis=1)
y = data.user_action
dumie_features = ['T0to6', 'T6to12', 'T12to18', 'T18to24']
dummies = pd.get_dummies(X.time_of_day, prefix=dumie_features)
X[dumie_features] = dummies
X = X.drop(labels=['time_of_day'], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)
%pylab inline
pylab.rcParams['figure.figsize'] = (40, 40)
#%% [markdown]
# Now create a model and train it 
# Important xgboost hyper parameters to improve the model are: 
#     - learning_rate: step size shrinkage used to prevent overfitting. Range is [0,1]
#     - max_depth: determines how deeply each tree is allowed to grow during any boosting round.
#     - subsample: percentage of samples used per tree. Low value can lead to underfitting.
#     - colsample_bytree: percentage of features used per tree. High value can lead to overfitting.
#     - n_estimators: number of trees you want to build.
#     - objective: determines the loss function to be used like reg:linear for regression problems, reg:logistic for classification           problems with only decision, binary:logistic for classification problems with probability.
#     - gamma: controls whether a given node will split based on the expected reduction in loss after the split. A higher value               leads to fewer splits. Supported only for tree-based learners.
#     - alpha: L1 regularization on leaf weights. A large value leads to more regularization.
#     - lambda: L2 regularization on leaf weights and is smoother than L1 regularization.
# There are two Classes in xgboost for creating a model XGBRegressor and XGBClassifier
# 

#%%
model = xgb.XGBClassifier(learning_rate=0.1, max_depth=4, n_estimations=10000, reg_lambda=1, objective='leg:logistic')
model.fit(X_train, y_train)
#%% [markdown]
# 
#%% [markdown]
# After training our model we can plot all trees of our model with plot_tree(num_trees=[tree_number])

#%%
import matplotlib.pyplot as plt
import matplotlib
import graphviz

xgb.plot_tree(model,  num_trees=5)
plt.show()
#%% [markdown]
# Now we can predict whether or not our model is good by testing it with our test data

#%%
y_pred = model.predict(X_test)
y_pred
#%% [markdown]
# And calculate the accuracy of our prediction 
# This will only work for Classification problems to test the performance
# For regression problems there are other ways to go like using the MSE(mean squared error)

#%%
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test[0:len(y_pred)], y_pred)
print('Accuracy: ',(accuracy * 100),'%')

