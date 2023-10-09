import pandas as pd
import pickle
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')
import numpy as np
import re

import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


class Preprocessor:
    def __init__(self):
        pass

    def preprocessing_text(self, df):
        """
        Preprocess the text data by removing non-alphabetic characters, urls and mentions
        """
        # encode all text that has encoding starting with \
        df['text'] = df['text'].str.encode('ascii', 'ignore').str.decode('ascii')

        # remove all non-ascii characters
        df['text'] = df['text'].str.replace(r'[^\x00-\x7F]+', '')

        # remove all non-alphanumeric characters
        df['text'] = df['text'].str.replace(r'[^a-zA-Z0-9\s]', '')

        # remove all single characters
        # df['text'] = df['text'].str.replace(r'\b[a-zA-Z]\b', '')

        # trim all leading and trailing whitespaces
        df['text'] = df['text'].str.strip()

        # remove all whitespaces
        df['text'] = df['text'].str.replace(r'\s+', ' ')

        # to lowercase
        df['text'] = df['text'].str.lower()

        return df

    def standardize_text(self, df):
        """
        Standardize the text data by removing non-alphabetic characters, urls and mentions
        """
        df['text'] = df['text'].str.replace(r"http\S+", "")
        df['text'] = df['text'].str.replace(r"http", "")
        df['text'] = df['text'].str.replace(r"@\S+", "")
        df['text'] = df['text'].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
        df['text'] = df['text'].str.replace(r"@", "at")
        df['text'] = df['text'].str.lower()
        return df

    def lemmatize(self, df):
        """
        Process the text data using nltk library and
        lemmatize the words to their root form
        :return:
        """
        lemmatizer = WordNetLemmatizer()
        df['text'] = df['text'].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.split()]))
        return df

    def remove_stopwords(self, df):
        """
        Remove stopwords from the text data
        :return:
        """
        stop_words = set(stopwords.words('english'))
        df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
        return df

    def remove_less_frequent_words(self, df, frequency_threshold=750, train=True):
        """
        Remove words that appear less than 5 times
        :return:
        """
        if train:
            # fit a countvectorizer to the text data
            count_vectorizer = CountVectorizer()
            corpus = df['text'].values
            frequencies = count_vectorizer.fit(corpus)
            words_to_remove = [key for key, value in frequencies.vocabulary_.items() if value < frequency_threshold]
            df['text'] = df['text'].apply(
                lambda x: ' '.join([word for word in x.split() if word not in words_to_remove]))

            print("Saving the count vectorizer")
            print("Number of words removed: ", len(words_to_remove))
            print("Sample of removed words: ", words_to_remove[:10])

            # save the words removed to a pickle file
            with open('../data/words_removed.pickle', 'wb') as handle:
                pickle.dump(words_to_remove, handle, protocol=pickle.HIGHEST_PROTOCOL)

            return df

        else:
            # test data
            with open('../data/words_removed.pickle', 'rb') as handle:
                # load the words removed from the training data
                words_to_remove = pickle.load(handle)

            df['text'] = df['text'].apply(
                lambda x: ' '.join([word for word in x.split() if word not in words_to_remove]))
            return df
        
    def remove_special_characters(self, df):
        df["text"] = df["text"].apply(lambda t: re.sub(r"[^a-zA-Z0-9\s]+", "", t))
        return df

    def keyword_one_hot_encoding(self, df):
        """
        Modify the keyword column
        """
        # apply one-hot encoding to the keyword column
        enc = OneHotEncoder(handle_unknown='ignore')
        df['keyword'] = df['keyword'].fillna('no_keyword')
        df['keyword'] = df['keyword'].apply(lambda t: t.replace('%20', '_'))

        X = list(df['keyword'])
        X = np.array(X).reshape(-1, 1)

        enc.fit(X)
        encoded_array = enc.transform(X).toarray()

        encoded_df = pd.DataFrame(encoded_array, columns=enc.categories_[0])
        return encoded_df


class CustomizedProcessor(BaseEstimator, TransformerMixin, Preprocessor):
    def __init__(self):
        super().__init__()
        
    def fit(self, *_):
        return self

    def transform(self, data):
        df = data.fillna('no_value')
        df = self.remove_special_characters(df)
        df = self.remove_stopwords(df)
        df = self.preprocessing_text(df)
        df = self.standardize_text(df)
        df = self.lemmatize(df)
                
        # change np.nan to 'no_value' for text column
        df['text'] = df['text'].fillna('no_value')
        df['text'] = df['text'].apply(lambda t: t.replace('%20', '_'))

        # encoded_df = self.keyword_one_hot_encoding(df)
        # df = df.join(encoded_df)
        print("Preprocessing completed.")
        return df


def preprocessing_pipeline():
    """
    Preprocessing pipeline
    """
    return Pipeline(steps=[('preprocessor', CustomizedProcessor())])

def cefr_model(input_str):
    """
    Create label for input str
    """

    ## TODO @Egehan/@Lavanya
    ## label = 


    return label


def cefr_classifier(df):
    """
    Load pretrained cefr model and generate data labels
    """

    src = df[["source"]].rename(columns={'source': 'text'})
    dst = df[["target"]].rename(columns={'target': 'text'})

    ## TODO: Preprocess text col
    preprocessor = preprocessing_pipeline()
    src1 = preprocessor.fit_transform(src)
    dst1 = preprocessor.fit_transform(dst)

    ## TODO: Would parallel apply work here....please check
    df['source_level_cefr'] = src1.parallel_apply(lambda x: cefr_model(x))
    df['target_level_cefr'] = dst1.parallel_apply(lambda x: cefr_model(x))

    return df


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import nltk
    nltk.download('wordnet')

    # Read data ---------------------------------------------------------------------
    ## Setup data location (If GCP, pass the loc using gs://)
    loc = "./data/"

    print("Loading data...")
    df1 = pd.read_csv(loc + "BreakingNewsLevels.csv")
    df2 = pd.read_csv(loc + "huggingface_cochrane_dataset.csv")
    df3 = pd.read_csv(loc + "NewsInLevels_dataset_TextSimplification.csv")
    df4 = pd.read_csv(loc + "wiki_large.csv")
    df5 = pd.read_csv(loc + "wiki_small.csv")
    print("Done.\n")

    # Concat dataframe --------------------------------------------------------------

    print("Concat data...")

    ## Data source: BreakingNewsenglish.com
    df1a = df1[['text in level 3', 'text in level 2']].rename(columns={'text in level 3': 'source', 'text in level 2': 'target'})
    df1a = df1a.assign(source_level_og = 3, target_level_og = 2)
    df1b = df1[['text in level 3', 'text in level 1']].rename(columns={'text in level 3': 'source', 'text in level 1': 'target'})
    df1b = df1b.assign(source_level_og = 3, target_level_og = 1)
    df1c = df1[['text in level 2', 'text in level 1']].rename(columns={'text in level 2': 'source', 'text in level 1': 'target'})
    df1c = df1c.assign(source_level_og = 2, target_level_og = 1)

    df1 = pd.concat([df1a, df1b, df1c], axis=0, ignore_index=True)
    df1['data_source'] = 'BreakingNewsEnglish'

    ## Data source: Huggingface
    df2 = df2[["source","target"]]
    df2['source_level_og'] = None
    df2['target_level_og'] = None
    df2['data_source'] = 'HuggingFace'

    ## Data source: News in levels
    pivoted_df = df3.pivot(index='level_url', columns='level', values='text').reset_index()
    pivoted_df.columns = ['id', 'text in level 1', 'text in level 2', 'text in level 3']

    df3a = pivoted_df[['text in level 3', 'text in level 2']].rename(columns={'text in level 3': 'source', 'text in level 2': 'target'})
    df3a = df3a.assign(source_level_og = 3, target_level_og = 2)
    df3b = pivoted_df[['text in level 3', 'text in level 1']].rename(columns={'text in level 3': 'source', 'text in level 1': 'target'})
    df3b = df3b.assign(source_level_og = 3, target_level_og = 1)
    df3c = pivoted_df[['text in level 2', 'text in level 1']].rename(columns={'text in level 2': 'source', 'text in level 1': 'target'})
    df3c = df3c.assign(source_level_og = 2, target_level_og = 1)

    df3 = pd.concat([df3a, df3b, df3c], axis=0, ignore_index=True)
    df3['data_source'] = 'NewsInLevels'

    ## Data Source: Wiki
    df4 = df4[["source","target"]] ## large
    df4['source_level_og'] = None
    df4['target_level_og'] = None
    df4['data_source'] = 'WikiLarge'

    df5 = df5[["source","target"]] ## small
    df5['source_level_og'] = None
    df5['target_level_og'] = None
    df5['data_source'] = 'WikiSmall'

    ## Add more data sources later .....





    ## Concat all
    raw_df = pd.concat([df1, df2, df3, df4, df5], axis=0, ignore_index=True)
    raw_df.reset_index(drop=True, inplace=True)

    raw_df['data_type'] = 'text_simplification'
    raw_df['source_level_cefr'] = None
    raw_df['target_level_cefr'] = None

    id_column = [f"TS{str(i).zfill(9)}" for i in range(1, len(raw_df) + 1)]
    raw_df['id'] = id_column

    print("Done.\n")

    ## Save intermediate dataframe before CEFR classification
    if(1):

        print("Saving raw data...")
        raw_df.to_csv(loc + "raw_data.csv", index=False)

        ## TODO: Save pickle files
        # with open(loc+'raw_data.pkl', 'wb') as f:
        #     pickle.dump(raw_df, f)
        print("Done.\n")

        

    if(0):
        print("Load raw data...")
        with open(loc+'raw_data.pkl', 'rb') as f:
            raw_df = pickle.load(f)

        print("Done.\n")

    
    # CEFR Classification --------------------------------------------------------
    ## Col: source  |  source_level_og  | source_level_cefr  |  target  |  target_level_og  |  target_level_cefr 
    
    print("Adding CEFR labels...")
    
    labelled_df = cefr_classifier(raw_df)

    print("Done.\n")

    if(1):

        print("Saving labelled data...")
        ## TODO: Save pickle files
        # with open(loc+'labelled_data.pkl', 'wb') as f:
        #     pickle.dump(labelled_df, f)
        print("Done.\n")


    # Prepare for training -------------------------------------------------------
    ## 
    ## Select og level if available, else cefr label. Final 4 cols for training

    param['labels'] = "og" ## "cefr"

    if param['labels'] == "og":
        
        labelled_df['source_level'] = labelled_df['source_level_og'].fillna(labelled_df['source_level_cefr'])
        labelled_df['target_level'] = labelled_df['target_level_og'].fillna(labelled_df['target_level_cefr'])
        
        train_df = labelled_df[['source','source_level','target','target_level']]

    else:

        labelled_df['source_level'] = labelled_df['source_level_cefr'].fillna(labelled_df['source_level_og'])
        labelled_df['target_level'] = labelled_df['target_level_cefr'].fillna(labelled_df['target_level_og'])
        
        train_df = labelled_df[['source','source_level','target','target_level']]

    
    if(1):

        print("Saving train data...")

        train_df.to_csv(loc + "train_data.csv", index=False)

        ## TODO: Save pickle files
        # with open(loc+'train_data.pkl', 'wb') as f:
        #     pickle.dump(train_df, f)
        
        print("Done.\n")








    

    

