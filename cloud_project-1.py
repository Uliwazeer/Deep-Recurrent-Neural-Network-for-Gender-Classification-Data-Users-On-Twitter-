# -*- coding: utf-8 -*-
"""Cloud_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12qNw6VW7qOC-arw7N4V2ASL9utDPoEsB

# **Twitter User Gender Classification**

#Getting started

#In the first let's import some important libraries |

**we need this libraries now, but this is not all the libraries we need for our project**
"""

!pip install tensorflow

import pandas as pd 
import numpy as np 

#for visualization 
import matplotlib.pyplot as plt
import seaborn as sns 

#for preprocessing
import tensorflow as tf
import sklearn
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

#analyze the results 
from sklearn.metrics import confusion_matrix, classification_report

"""**Let's load the data from the csv file**

there is an error happens sometimes if the encoding a little off and we can fix it by encoding="latin-1"
```
data = pd.read_csv("/content/gender-classifier-DFE-791531.csv",encoding="latin-1" )
```
"""

data = pd.read_csv("/content/gender-classifier-DFE-791531.csv", encoding="latin-1")

#let's show the dataset and display all columns
data

"""#info about the columns in the dataset

1. **unitid**: a unique id for the user
2. **golden**: whether the user was included in the gold standard for the model; TRUE or FALSE
3. **trustedjudgments**: number of trusted judgments (int); always 3 for non-golden, and what may be a unique id for gold standard observations
4. **lastjudgment_at**: date and time of last contributor judgment; blank for gold standard observations
5. **gender**: one of male, female, or brand (for non-human profiles)
6. **gender:confidence**: a float representing confidence in the provided gender
7. **profile_yn**: “no” here seems to mean that the profile was meant to be part of the dataset but was not available when contributors went to judge it
8. **profile_yn: confidence**: confidence in the existence/non-existence of the profile
9. **created**: date and time when the profile was created
10. **description**: the user’s profile description
11. **fav_number**: number of tweets the user has favourited
12. **gender_gold**: if the profile is golden, what is the gender?
13. **link_color**: the link colour on the profile, as a hex value
14. **name**: the user’s name
15. **profileyngold**: whether the profile y/n value is golden
16. **profileimage**: a link to the profile image
17. **retweet_count**: number of times the user has retweeted (or possibly, been retweeted)
18. **sidebar_color**: color of the profile sidebar, as a hex value
19. **text**: text of a random one of the user’s tweets
20. **tweet_coord**: if the user has location turned on, the coordinates as a string with the format “[latitude, longitude]”
21. **tweet_count**: number of tweets that the user has posted
22. **tweet_created**: when the random tweet (in the text column) was created
23. **tweet_id**: the tweet id of the random tweet
24. **tweet_location**: location of the tweet; seems to not be particularly normalized
25. **user_timezone**: the timezone of the user
26. **the third columnn**(unitstate: state of the observation; one of finalized (for contributor-judged) or golden (for gold standard observations)




"""

#To know the type of data in columns (numerical , categorical)  
data.info()

"""## **Preprocessing**

Check if there is a null values
"""

data.isna().sum()

data.isna().mean()

"""OK, as we see there is some columns have high percentage of null values so let's modifying data """

data.shape

#check the unnecessary columns with high number of unique values 
data.nunique()

#as wee see there is a number of unnecessary columns
unnecessary_cols = ['_unit_id','name','profileimage','tweet_id']

"""Before we drop columns with over than 30% missing values, let is take a look in gender column"""

data['gender'].unique()

"""As we see there is a unknown values in gender columns which is not useful so will replace the unknown with Nan by using np.NaN and after that drop columns """

#the shape before drop the columns with missing values
data['gender'].shape

"""******************************************************************************************************

here we use true,false series of missing values in gender column to be the index of the original dataframe
"""

#this will returns only the rows which have the missing values in gender column 
data[data['gender'].isna()].index

"""_______________________________________________________________________

To know the columns which have over than 30% missing values
"""

data.isna().mean() > 0.3

"""As we see, we have true,false series... the true indicate the columns which have over than 30% missing values, the true indicate the columns which have lower than 30% missing values"""

#get the column names with over than 30% missing values
over_30_per_missing = data.columns[data.isna().mean() > 0.3]
over_30_per_missing

#text will indicate pandas series of text
#vocab_lenght will indicate how many of the most frequent words do we want to use 
def get_sequences(texts, vocab_lenght):
    #tokenizer it will assign each word to a unique integer from one to vocab_lenght. So, the most frequent word will be given a value of one, the next most frequent will be given a value of two 
    #tokenizer it is really cool it has a lot of filtering methods built into it, it is can filter out any special characters, any pure, any punctuation... then it is going to lower case the whole thing and then split it on white space   
    tokenizer = Tokenizer(num_words=vocab_lenght)
    tokenizer.fit_on_texts(texts)#this will just collect all the information about the frequency of each word 

    sequences = tokenizer.texts_to_sequences(texts)#from text to sequences 

    max_seq_length = np.max([len(sequence) for sequence in sequences])#to know the sequence with maximum length

    print(max_seq_length)

    sequences = pad_sequences(sequences, maxlen= max_seq_length, padding='post')#to pad all the the sequences so they all take the same length by add zeros to the end(padding to put all zeros in the end)

    return sequences

get_sequences(data['text'], vocab_lenght=10000)

"""As we see, this is the first tweet [599, 6, 8511, 168, 186, 420, 3630, 4066, 11, 1, 5, 3, 4], each word in the tweet has been encoded to a unique integer from 1 to 10000

if we look, we have a varying lengths here it is not in the great way fo feed it into model, so we are going to pad all the the sequences so they all take the same length by add zeros to the end
"""

get_sequences(data['text'], vocab_lenght=10000)

def hex_to_decimal(x):
    try:
      return np.int(x ,16)#convert from hexadecimal to decimal 
    except:
      return 0 #if we have error(the color codes which is set to zero) we're  just going to return zero

#get a list of colors 
#we're going to pass into color column and return three new columns(reds, blues, greens)

def get_rgb(colors):
    
    red = colors.apply(lambda x : hex_to_decimal(x[0:2]))#the first two characters represent to red 
    green = colors.apply(lambda x : hex_to_decimal(x[2:4]))#the second two characters represent to green 
    blue = colors.apply(lambda x : hex_to_decimal(x[4:6]))#the third two characters represent to blue
    #but this is not enough this us just going to be a string
    #So I'm going to convert from hexadecimal to decimal 
    #but there is one issue, some of the color codes just gets set to zero
    
    return red, green, blue

def preprocess_inputs(df):
    #we will not accidentally modifying, we want to keep as it is  
    df = df.copy()

    #Drop unnecessary columns (as shown in Data_1 output)
    df = df.drop(unnecessary_cols, axis=1)

    #Encode unknown values in the target column as np.Nan (as shown in the Target_1 output)
    df['gender'] = df['gender'].replace('unknown', np.NaN)

    #Drop rows with missing target values (as shown in Data_2 output)
    gender_nas = df[df['gender'].isna()].index
    df = df.drop(gender_nas, axis=0).reset_index(drop=True)#this will prevents the old indecies becoming a new column in df

    #Drop columns with over than 30% missing values (as shown in Data_3 output)
    missing_cols = over_30_per_missing
    df = df.drop(missing_cols, axis=1)

    #There are only 50 remaining missing values in the _last_judgment_at columns, so let's drop those rows (as shown in Data_4 output)
    judgment_nas = df[df['_last_judgment_at'].isna()].index
    df = df.drop(judgment_nas, axis=0).reset_index(drop=True)

    #Let's encode the missing values in the description column as empty string (as shown in Data_5 output)
    df['description'] = df['description'].fillna('')

    #Create date/time cols, replacing the original time cols with a bunch of new cols based on the data in each one, to be able to fed into the model (as shown Data_6 output)
    for column in ['_last_judgment_at','created','tweet_created']:
      #this code will return a column but in date/time format
      df[column] = pd.to_datetime(df[column])
    
    df['_last_judgment_year'] = df['_last_judgment_at'].apply(lambda x : x.year)
    df['_last_judgment_month'] = df['_last_judgment_at'].apply(lambda x : x.month)
    df['_last_judgment_day'] = df['_last_judgment_at'].apply(lambda x : x.day)
    df['_last_judgment_hour'] = df['_last_judgment_at'].apply(lambda x : x.hour)

    df['created_year'] = df['created'].apply(lambda x : x.year)
    df['created_month'] = df['created'].apply(lambda x : x.month)
    df['created_day'] = df['created'].apply(lambda x : x.day)
    df['created_hour'] = df['created'].apply(lambda x : x.hour)

    df['tweet_created_year'] = df['tweet_created'].apply(lambda x : x.year)
    df['tweet_created_month'] = df['tweet_created'].apply(lambda x : x.month)
    df['tweet_created_day'] = df['tweet_created'].apply(lambda x : x.day)
    df['tweet_created_hour'] = df['tweet_created'].apply(lambda x : x.hour)
    
    df = df.drop(['_last_judgment_at','created','tweet_created'], axis=1)

    #get the sequence data for description and text cols.(as shown in the Data_7 output)
    desc_seq = get_sequences(df['description'], vocab_lenght=20000)
    tweets = get_sequences(df['text'], vocab_lenght=20000)

    df = df.drop(['description', 'text'], axis=1)

    #Drop the cols with only one unique values.(as shown in the Data_7 output)
    df = df.drop(['_golden', '_unit_state', 'profile_yn' ,'_trusted_judgments','_last_judgment_month','_last_judgment_year','tweet_created_day','tweet_created_month','tweet_created_year'], axis=1) 

    #Encode color columns as RGB values (as shown in the Data_8 output)
    df['link_red'], df['link_green'], df['link_blue'] = get_rgb(df['link_color']) 
    df['sidebar_red'], df['sidebar_green'], df['sidebar_blue'] = get_rgb(df['sidebar_color']) 

    df = df.drop(['link_color', 'sidebar_color'], axis=1)

    #Encode label column that as 0 1 and 2
    label_mapping = {'female':0, 'male':1, 'brand':2}
    df['gender'] = df['gender'].replace(label_mapping)

    #split df into X and y(target)
    X = df.drop('gender', axis=1).copy()
    y = df['gender'].copy()

    #Scale the X with standard scaler
    scaler = StandardScaler()
    X = pd.DataFrame(scaler.fit_transform(X), columns = X.columns)#this will allow each column to take a very similar range of values and will improve the model's performance 
      
   #return df #for code in line 83 
    return X, desc_seq, tweets, y

#check if we drop the unnecessry cloumns 
#check_fdrop = preprocess_inputs(data)
#check_fdrop

Data, Target =preprocess_inputs(data)
Data

"""As we see there is a 20050 rows and 25 columns"""

#let's drop the unnecessary columns with high number of unique values 
Data_1, Target_1 =preprocess_inputs(data)
Data_1

"""As wee see after drop the unnecessary columns with high number of unique values we now have 21 columns

_____________________________________________

let's take a look to the unique values in the target column
"""

#we have unknown values which is not useful. So, we going to encode unknown values in the target column unsing np.Nan
Target_1.unique()

Target_1.unique()

"""As we see the unknown values replaced with nan, now we're going to go a head and drop the missing target values """

Data_2, Target_2 =preprocess_inputs(data)
Data_2

Target_2.shape

"""After Drop the rows with missing target values, we have 18836 rows and 21 columns

Now let's drop columns with over than 30% missing values
"""

Data_3, Target_3 =preprocess_inputs(data)
Data_3

"""After drop columns with over than 30% missing values, we have 16 cols and 18836 rows, Now let's check the remaining missing values"""

#check the columns with missing values after 
Data_3.isna().sum()

"""We only have two colums with remaining missing values 
1. _last_judgment_at
2. description

we must understand what kind of data in these two columns. 
_last_judgment_at: it is a date time column and there is only 50 missing values what we could do is create a bunch of new columns the year, month, day, hour times values from the original date time and then we could fill the means for each of those for these 50 missing values but it is only 50 missing values and we can going to drop those 50 rows because it not like a big loss it'll be all right

"""

#data after drop the 50 rows with missing values in the _last_judgment_at column
Data_4, Target_4 = preprocess_inputs(data)

#check the columns with missing values after drop the 50 rows with missing values in the _last_judgment_at column
Data_4.isna().sum()

"""now we only have the missing values in the description column.
the description column this is a text column and this is actually very important, this probably has a lot of a information about a person's gender(this is talk about how people describe themselves)

Let's encode the missing values in the description column as empty strings
"""

#the Data after encode the missing values in the discription column as empty strings
Data_5, Target_5 = preprocess_inputs(data)
Data_5

"""Now we have 18786 rows and 16 cloumns. So, we still have a lot of data

Now we going to deal with data types , for numerical columns if we take a look they are already ready to be fed into the model after some scaling, but for categorical cols these need to be transformed in some way to can be fed into the model

if we take a look in the ['_last_judgment_at', 'created', 'tweet_created'], it is a date/time, So what we're going to do is create a bunch of new columns based on the data in each one
"""

#check the Data after encode the missing values in the discription column as empty strings
Data_5.isna().sum()

"""Now we have no more missing values, we're totally done with missing values"""

Data_6, Target_6 = preprocess_inputs(data)
Data_6

"""So, now we have 12 new cols with the information taken from the date/time cols

Now we're going to deal with description,text 

we're actually going to feed these bits of information in separately. we're going to feed each one in a sequence of toknized words which each word is mapped to unique integer.

____________
"""

Data_7, desc, tweets, Target_7 = preprocess_inputs(data)
Data_7

"""we drop the text and description cols from the original df, and store it with a new form in the desc, tweets vars"""

print(desc.shape)
desc

"""the longest sequence in desc is 62 """

print(tweets.shape)
tweets

"""the longest tweet in tweets is 104

So we're going to feed desc, tweets in separately a long X, so there is going to be three inputs to model and then we're going to predict y

______

before encode the color columns, let's check the number of unique values for each column
"""

#get the number of unique values for each column 
{column: len(Data_7[column].unique()) for column in Data_7.columns}

"""So, As we see, we have a number of coloumns with only one value, so we're going to drop all of those, these columns aren't giving us any useful information.  """

#After Drop the cols with only one unique value
{column: len(Data_7[column].unique()) for column in Data_7.columns}

Data_7

"""After Drop the cols with only one unique value
, We're down to 14 cols.

______

Now let's encode the color columns

we could encode these columns as one hot encodings... but if we look and think what this is data in colors cols, these rgb color encodings are created As follows, the first two characters are the instensity of red, the second two characters is the intensity of green, the characters is the intensity of blue.

So, what we could do is actually take the first two characters, the second two characters and the third two characters, and create new features out of them one for red, one for green and one for blue
"""

Data_8, desc, tweets, Target_8 = preprocess_inputs(data)
Data_8

{column: len(Data_8[column].unique()) for column in Data_8.columns}

Data_8

"""_______

Now let's Scale X using a standard scaler, this is from sklearn and this will give each column in x a mean of zero and variance of one
"""

Data_9, desc, tweets, Target_9 = preprocess_inputs(data)
Data_9

Target_9

Target_9.unique()

Target_9.value_counts()

"""Now our dataset fully processed fully scaled no missing values

________

# Building the model

## Train_Test split
"""

#we're going to split this into eight new sets of the data 
X_train, X_test, desc_train, desc_test, tweets_train, tweets_test, y_train, y_test = train_test_split(Data_9, desc, tweets, Target_9, train_size=0.7, random_state=1)#this will ensure that the data is always shuffled in the same manner

"""### Modeling """

desc

X_inputs = tf.keras.Input(shape=(Data_9.shape[1],))#this first input is just being fed through the two dense layers(X_dense1,X_dense2) which we going to define them
desc_inputs = tf.keras.Input(shape=(desc.shape[1],))
tweet_inputs = tf.keras.Input(shape=(tweets.shape[1],))

#we're going process each one separately 

#this is just going to be a standard neural network section 
X_dense1 = tf.keras.layers.Dense(256, activation='relu')(X_inputs)
X_dense2 = tf.keras.layers.Dense(256, activation='relu')(X_dense1)

#desc 
desc_embedding = tf.keras.layers.Embedding( # this is going to take sequence and it is going to send each word to a new location in a high dimensional vector space 
    input_dim=20000,#this is a sort of mapping from a sparse encoding to a dense encoding, each  word is going to be mapped to a new location,so we map that as a vector of length 20000
    output_dim=256,#we're going to mapping the vector to a new dimensional space of our choosing and teh 256 will work 
    #generally the more intricate the connection between the words the higher dimension space you need 
    #each word can be represented as a vector of length 256 which is a lot better than represented by a vector of length 20000
    input_length=desc.shape[1]#that is just going to be the length of a given sequence 
)(desc_inputs)

desc_embedding.shape

"""None: is just batch size

62: is a number of words in a sequence 

256: each word is 256 elements long because each one is now represented as 256 dimensional vector

___________

So we're not only going to send the embedded words to the final prediction, we're also going to run the embedded words  through GRU(Gated Recurrent Units) which is form long-short-term memory network layer, which is form of RNN(Recurrent Neural Networks). RNN is uses the previous information in the sequence to produce the current output.

the purpose of GRU is to capture time dependencies between the words, in RNN takes as input a given word but also the previous one and so each time it sees a new word, it considers (the past as well as the present)
"""

desc_gru = tf.keras.layers.GRU(256, return_sequences=False)(desc_embedding)#if the return_sequences=True it would return a new sequence in each time step for each new word it sees, but if we have it on false it will just return the final output

"""___________

'''because the desc_embedding is two dimensional, we're going to have some a hard time feeding it into the later parts of the model, so we're going to flatten it which will take all of the rows and put them side by side, 
so we going to have one long vector'''
"""

desc_faltten = tf.keras.layers.Flatten()(desc_embedding)

"""desc embedding is now being passed into the gru but also into the flattened layer, so we're going to concat the desc_gru with desc_faltten, because each one of them returns a single vector, so we're going to take these two vectors and put them side by side """

desc_concat = tf.keras.layers.concatenate([desc_gru, desc_faltten])#this is going to contain all the information from the description

#tweets the same thing we do to description, we're going to here
tweet_embedding = tf.keras.layers.Embedding(
    input_dim=20000,
    output_dim=256,
    input_length=tweets.shape[1]
)(tweet_inputs)
tweet_gru = tf.keras.layers.GRU(256, return_sequences=False)(tweet_embedding)
tweet_faltten = tf.keras.layers.Flatten()(tweet_embedding)
tweet_concat = tf.keras.layers.concatenate([tweet_gru, tweet_faltten])

concat = tf.keras.layers.concatenate([X_dense2, desc_concat, tweet_concat])

#finally our output will be a dense layer with three values and softmax activation function
outputs = tf.keras.layers.Dense(3, activation="softmax")(concat)#the 3  stands for the three probaility values(male,female,brand), and the softmax activation function ensures that their values between 0 and 1

"""Now we're going to create a model """

model = tf.keras.Model(inputs=[X_inputs, desc_inputs,tweet_inputs], outputs=outputs)

print(model.summary())

"""here we can see a list of parameters that are being tuned in this model,
the (Param #) column stands for the weights that actually are learning where to send the words in 256 dimensional space.

dense_15(Param #)=129795, 129795 the final weights are in the connection between our final dense layer(dense_15) and the concatenation(concatenate_7)
"""

tf.keras.utils.plot_model(model)

"""As we see here, we have three different inputs, the left one for the descriptions, the right one for tweets, the middle one for the regular x values.

middle : The regular x values is getting passed through two dense layers , then sent it to the concatenation layer.

right and left : both being embedded, the embeddings are being sent to a GRU and to a flattened, and the two outputs from GRU and flatten are getting concatenated back together.

the fifth row : the final three outputs get concatenated to one big vector

the final row : the concatenated vector sent to a dense layer to give our final three values.

## Training
"""

model.compile(
    optimizer = 'adam',
    loss = 'sparse_categorical_crossentropy',
    metrics = ['accuracy']
)

batch_size = 32
epochs = 3 #generally when using gru's, you only have to train for a very small number of epochs, usually it is fit best by the first or second epoch
#when i call the fit function i going to include a callback that will save the best epoch weights 
history = model.fit(
    [X_train, desc_train, tweets_train],
    y_train,
    validation_split = 0.2,
    batch_size = batch_size,
    epochs = epochs,
    callbacks=[
        tf.keras.callbacks.ModelCheckpoint('./model.h5',#this will let us save a hdf5 file with our model weights
                                           save_best_only=True,#save only the best epochs so we can load it up later 
                                           save_weights_only=True),#since we're just going to loading the weights
        tf.keras.callbacks.ReduceLROnPlateau()#which will help us converge a little more eaisly(reduce learning rate on plateau)       
    ]
)

model.load_weights('./model.h5')

"""# Results"""

results = model.evaluate([X_test, desc_test, tweets_test], y_test, verbose=0)#turn off the boast mode
print("Model Accracy: {:.2f}%".format(results[1] *100))#multiply by 100 to get the percentage

y_true = np.array(y_test)

y_predict = model.predict([X_test, desc_test, tweets_test])

y_predict

"""As we see here, it returns three different probability values for each example as that is what we set it to return these three values with a soft max activation, but we want the index of the highest probability which will our actual classification."""

y_predict = map(lambda x: np.argmax(x), y_predict)#x will be one of the three probability values and it is going to return the index of the maximum value, this is what we want
y_predict = np.array(list(y_predict))

y_true

y_predict

#going to create a confusion matrix 
cm = confusion_matrix(y_true, y_predict)
clr = classification_report(y_true, y_predict, target_names=['Female','Male','Brand'])

plt.figure(figsize=(10, 10))
sns.heatmap(cm, annot=True, fmt='g', cbar=False, cmap='Blues')#annot=True so we can see the actual count values,,, fmt='g' to avoid the counts show in scientific notation 
plt.xticks(np.arange(3) + 0.5, ['Female','Male','Brand'])
plt.yticks(np.arange(3) + 0.5, ['Female','Male','Brand'])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

"""  we can here the number of predicted values for each category and compared with number of actual values for each category """

print("Classification Report:\n\n", clr)

"""As we see, the most easily calssified category was a brand 

female: precision=0.6 which means that, 60% of our values were correct in the predictions... recall=0.55 which means out of all actual female values 55% were correct.

male: precision=0.53 which means that, 53% of our values were correct in the predictions... recall=0.66 which means out of all actual female values 66% were correct. Which looks like a male category probably our worst category.which means it is the hardest for the model to classify
"""