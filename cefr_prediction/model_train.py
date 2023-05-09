import numpy as np
import pandas as pd

import ktrain
from ktrain import text

# Load the data
df = pd.read_csv('data/train_data.csv')
df = df[['text', 'label']]

df["label"] = df["label"] - 1  # change the label to 0, 1, 2

# Split the data
(x_train, y_train), (x_test, y_test), preproc = text.texts_from_df(train_df=df,
                                                                   text_column='text',
                                                                   label_columns=['label'],
                                                                   val_pct=0.2,
                                                                   maxlen=350,
                                                                   max_features=35000,
                                                                   preprocess_mode='bert')

# Create the model
model = text.text_classifier(name='bert',
                             train_data=(x_train, y_train),
                             preproc=preproc)

# Train the model
learner = ktrain.get_learner(model=model,
                             train_data=(x_train, y_train),
                             val_data=(x_test, y_test),
                             batch_size=6)

learner.fit_onecycle(lr=2e-5, epochs=1, verbose=1)

# Save the model
predictor = ktrain.get_predictor(learner.model, preproc)

predictor.save('cefr_ktrain_bert')