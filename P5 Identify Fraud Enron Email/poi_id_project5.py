
# coding: utf-8

# In[2]:

#!/usr/bin/python
import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data,test_classifier
from sklearn.feature_selection import f_regression,SelectKBest
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.grid_search import GridSearchCV
from sklearn.decomposition import RandomizedPCA
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.cross_validation import train_test_split
import numpy as np



### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary',  'total_payments',  'bonus',  'total_stock_value',                  'expenses', 'exercised_stock_options', 'other',  'restricted_stock', 'to_messages',                  'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi'] # You will need to use more features


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop("TOTAL",0)
data_dict.pop("LAY KENNETH L",0)
data_dict.pop("FREVERT MARK A",0)
data_dict.pop("BHATHAGAR SANJAY",0)
data_dict.pop("WHITE JR TOHMASE",0)
data_dict.pop("PAL LOUL",0)
data_dict.pop("LAVORATO JOHN",0)
data_dict.pop("DIETRICH JANET R",0)
data_dict.pop("KAMINSKI WINCENTY J",0)
data_dict.pop("KEAN STEVEN J",0)
data_dict.pop("SHAPIRO RICHARD S",0)
data_dict.pop("WHALLEY LAWRENCE G",0)







### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict


# define a function
def computeFraction( poi_messages, all_messages ):
    """ given a number messages to/from POI (numerator) 
        and number of all messages to/from a person (denominator),
        return the fraction of messages to/from that person
        that are from/to a POI
   """
    if poi_messages=="NaN":
        fraction=0
    else:
        if all_messages=="NaN":
            fraction=0
        else:
            fraction=float(1.0*poi_messages/all_messages)

    ### you fill in this  it returns either
    ###     the fraction of all messages to this person that come from POIs
    ###     or
    ###     the fraction of all messages from this person that are sent to POIs
    ### the same code can be used to compute either quantity

    ### beware of "NaN" when there is no known email address (and so
    ### no filled email features), and integer division!
    ### in case of poi_messages or all_messages having "NaN" value, return 0.
    return fraction


for name in my_dataset:

    
    from_poi_to_this_person = my_dataset[name]["from_poi_to_this_person"]
    to_messages = my_dataset[name]["to_messages"]
    fraction_from_poi = computeFraction( from_poi_to_this_person, to_messages )
    
    my_dataset[name]["fraction_from_poi"] = fraction_from_poi
   
    from_this_person_to_poi = my_dataset[name]["from_this_person_to_poi"]
    from_messages = my_dataset[name]["from_messages"]
    fraction_to_poi = computeFraction( from_this_person_to_poi, from_messages )
   
    my_dataset[name]["fraction_to_poi"] = fraction_to_poi
### Extract features and labels from dataset for local testing


data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Decision Tree for the Classifier
dtc=DecisionTreeClassifier(random_state=42)

# SelectKBest to choose the features
kbest=SelectKBest()

# RandomiizedPCA to reduce the dimention
pca = RandomizedPCA(random_state=3)







### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html






#Split features and labels into train and test data.
features_train, features_test, labels_train, labels_test =     train_test_split(features, labels, test_size=0.3, random_state=42)

combined_features = FeatureUnion([("kbest", kbest),("pca", pca),])
transformed_features=combined_features.fit(features_train,labels_train).transform(features_train)
    
    
#MinMax Scaling after SelectKBest and PCA
scale=MinMaxScaler()    
    
#Pipeline 
pipeline=Pipeline([("features_train",combined_features),("minmax",scale),("dtc",dtc)])
parameters={"features_train__pca__n_components":range(1,14),
                    "features_train__kbest__k":range(1,14),
                    "dtc__criterion":["gini","entropy"]}


#GridSearch (10 fold Cross Validation)
grid_search=GridSearchCV(pipeline,parameters,cv=10,verbose=0)
grid_search.fit(features_train,labels_train)

print "The Best parameters for the grid:"
print grid_search.best_params_

clf = grid_search.best_estimator_




### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

print "Classification report:" 
print " "
test_classifier(clf, my_dataset, features_list)

dump_classifier_and_data(clf, my_dataset, features_list)


# In[ ]:



