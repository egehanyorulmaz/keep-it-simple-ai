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
        df = self.remove_special_characters(data)
        df = self.remove_stopwords(df)
        df = self.preprocessing_text(df)
        df = self.standardize_text(df)
        df = self.lemmatize(df)
        df = df.fillna('no_value')
        
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


if __name__ == '__main__':
    df = pd.read_csv('../data/train.csv')
    print('Preprocessing the data...')
    preprocessor = preprocessing_pipeline(args)
    df = preprocessor.fit_transform(df)
    df.to_csv('../data/train_preprocessed.csv', index=False)
