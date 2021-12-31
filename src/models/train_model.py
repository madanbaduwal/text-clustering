# In this module we use features/build_features.py module to train ,
# hyperparameters search and store artifacts(reports) of our model.
# Artifact are store in MLflow and best model only save(in model folder) or in S3 buccket

import pandas as pd
import numpy as np
import os
import mlflow
from mlflow_extend import mlflow

from pprint import pprint
from src.utils.mlflow import fetch_logged_datas
from src.utils.config import Config
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans,AgglomerativeClustering

class TrainModel:
    def __init__(self):
        pass

    def load_data(self):
        data = pd.read_csv(Config.LOCAL_DATA_DIR+"/features-unlabelled_data.csv")
        data = data[["ATTENDANCE","ASSIGNMENT_SCORE","SUBMITTED_DEADLINE","QUIZ_SCORE"]]
        return data

    def train_test_split(self):
        data = self.load_data()
        X = np.ascontiguousarray(data) # if we have a supervise we need to split in X,y
        return X

    def pipeline(self):
        pipe = Pipeline([('Kmeans', KMeans(n_clusters=3, random_state=0))])
        return pipe

    def train_model(self):
        mlflow.sklearn.autolog()

        # mlflow.set_tracking_uri("http://35.173.191.133:5000") # In this way we  can also save artificats into server also
        # mlflow.set_experiment('RECO_QR_SentenceAttentionModel')

        X = self.train_test_split()
        pipe = self.pipeline()

        with mlflow.start_run() as run:
            pipe.fit(X)
            print("Logged data and model in run: {}".format(run.info.run_id))

            # mlflow.log_artifact('sentAttention.png', 'model_architecture/') # In this way 
            # mlflow.log_figure(figure, "Train and Validation losses.png")
            # mlflow.end_run()

        # show logged data
        for key, data in fetch_logged_datas(run.info.run_id).items():
            print("\n---------- logged {} ----------".format(key))
            pprint(data)

        # Note : We can also save  this artifictas (mlruns) at server to show others
        
    def save_model():
        # Load  best model from mlruns/0../.. and save it to the models folder and upload it to the S3 buccket
        pass


if __name__ == "__main__":
    trainModel = TrainModel()
    trainModel.train_model()


# Use 
# After running this we can see the artificts at mlruns folder

## mlflow ui  # To show all mlruns artifacts