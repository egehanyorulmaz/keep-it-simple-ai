import ktrain
from ktrain import text, predictor
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix, classification_report

# Split the data
(x_train, y_train), (x_test, y_test), preproc = text.texts_from_df(train_df=df,
                                                                   text_column='text',
                                                                   label_columns=['label'],
                                                                   val_pct=0.2,
                                                                   maxlen=350,
                                                                   max_features=35000,
                                                                   preprocess_mode='bert')


# Evaluation
y_pred = predictor.predict(x_test)
y_true = np.argmax(y_test, axis=1)
y_pred = np.argmax(y_pred, axis=1)

# Classification report
print("Classification Report:")
print(classification_report(y_true, y_pred))

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)

# Confusion Matrix Visualization
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="YlGnBu", xticklabels=preproc.get_classes(),
            yticklabels=preproc.get_classes())
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')