"""In this module we load model
we had trained in models/train_model.py  and
build  use feature features/build_features.py  and do prediction."""
import datetime
import os
import sys
import pickle

import numpy as np
import pandas as pd
from loguru import logger
from pymongo import MongoClient
from configs.config import Config
from configs.config import settings
import botocore.discovery
from pathlib import Path
from src.features.build_features import create_features_for_all_students
from src.features.build_features import create_features_for_one_student

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

class Predict:
    def __init__(self):
       pass

    def fetch_model(self, model_name="model.pkl"):
        """Fetch model from S3
        """
        local_model_path = Path(Config.LOCAL_MODEL_DIR, model_name)

        if not local_model_path.exists():
            logger.info("Fetching model from S3")
            s3_data_path = Path(Config.S3_MODEL_DIR, model_name)
            try:
                Config.S3_BUCKET.download(s3_data_path, Config.LOCAL_MODEL_DIR)
            except botocore.exceptions.ClientError as e:
                logger.error(e)
                return None

        return pickle.load(open(local_model_path, "rb"))


    def predicted_in_dummy_features(self,data):
        """Label prediction for the given features.
        Args:
            data(list) : List of features.
        Returns:
            pred(panda data frame) : Pandas DataFrame.
        """
        features = data
        # Order of features [ATTENDANCE,ASSIGNMENT_SCORE,
        # ASSIGNMENT_SUBMITTED_DEADLINE,QUIZ_SCORE]
        # Feature transformation
        logger.info("Start feature transformation.")
        log_features = [
            np.log10(1 + features[0]),
            features[1],
            np.log10(1 + features[2]),
            np.log(1 + features[3]),
        ]
        log_features = np.asarray(log_features).reshape(1, -1)
        logger.info("Feature transformation completed.")

        # Load model
        logger.info("Start model loading and prediction.")
        model = self.fetch_model()
        pred_cluster = model.predict(log_features)
        logger.info("Complete model loading and prediction")
        logger.info(
            f"Prediction completed, features are{features}",
        )

        # Assign cluster name(class name)
        pred_class = [
            "Yellow" if i == 0 else "Green" if i == 1 else "Red" for i in pred_cluster
        ]
        logger.info(f"Prediction lebel is:{pred_class[0]}")
        return pred_cluster, pred_class


    def predicted_for_one_student(self,student_id, courseid):
        """Label prediction of the given student_id and course_id.
        Args:
            student_id(str) : student_id.
            courseid(str) : course_id.
        Returns:
            pred(list) : list of prediction.
        """
        logger.info("Start creating features")
        features, log_features = create_features_for_one_student((student_id, courseid))
        logger.info("Complete features creation")

        # Load model and do prediction
        logger.info("Start model loading and prediction")
        model = self.fetch_model()
        pred_cluster = model.predict(log_features.iloc[:, 3:7].copy())
        logger.info("Complete model loading and prediction")
        logger.info(
            f"Prediction completed, features are{features}",
        )

        # Assign cluster name(class name)
        pred_class = [
            "Yellow" if i == 0 else "Green" if i == 1 else "Red" for i in pred_cluster
        ]
        logger.info(f"Prediction lebel is:{pred_class[0]}")
        return features, log_features, pred_cluster, pred_class


    def prediction_for_all_students_and_dump_into_mongoserver(self):
        """Label prediction for all data points.
        Args:

        Returns:
            data(Dataframe) : Data frame in which contain student_id,
            course_id,gu_id ,features and dump into the mongo server.
        """
        # Feature extraction for all students and there courses
        logger.info("Start features creation")
        f_first_time = datetime.datetime.now()
        features, log_features = create_features_for_all_students()
        f_second_time = datetime.datetime.now()
        f_time = f_second_time - f_first_time
        index = features.index
        total_number_of_data_points_features_extraction = len(index)
        logger.info(
            f"Total time required is :{f_time}",
        )

        # Load model
        logger.info("Start model loading")
        model = self.fetch_model()
        logger.info("Completed model loading")

        # Do prediction on log_features
        logger.info("Start prediction")
        p_first_time = datetime.datetime.now()
        pred_cluster = model.predict(log_features.iloc[:, 3:7].copy())
        logger.info("Completed predictions")
        p_second_time = datetime.datetime.now()
        p_time = p_second_time - p_first_time
        # Assign Cluster Label to the DataFrame
        features["originalLabel"] = pred_cluster

        # Map cluster(0,1,2) to the actual label(Green,yellow,red)
        lborign = ["Yellow", "Green", "Red"]
        features["originalLabel"] = features["originalLabel"].replace([0, 1, 2], lborign)

        # Backend demand said we need  revisedLabel column with same originalLabel data
        features["revisedLabel"] = features["originalLabel"]
        

        # You Can save prediction data to cvs for prediction analysis
        logger.info("Start saving prediction data to .csv file to some folder")
        current_dir = os.getcwd()
        print("current directory is:", current_dir)
        # os.chdir('/tmp')
        if not os.path.exists("predicted_results"):
            os.makedirs("predicted_results")
            if os.path.exists("predicted_results/predictions.csv"):
                os.remove("predicted_results/predictions.csv")
            else:
                with open("predicted_results/predictions.csv", "wb"):
                    features.to_csv(
                        r"predicted_results/predictions.csv",
                        index=False,
                        header=True,
                    )
        logger.info("Completed saving prediction data to .csv file to some folder")
        
        # You can also upload this model to the S3 buckket also


        # Dump all the prediction data frame into mongo data server.
        # Data base configuration
        # Making a Connection with MongoClient
        logger.info("Start connecting to mongodb server")
        try:
            client = MongoClient(settings.mongo_server)
            logger.info("Connected successfully!!!")
        except:
            logger.info("Could not connect to MongoDB")

        # database
        db = client[settings.mongo_database]

        # collection
        prediction_mongo_collection = db[settings.prediction_mongo_collection]
        centroid_mongo_collection = db[settings.centroid_mongo_collection]

        # To insert data into mongodb server we
        # first need to convert into dictionary
        features.reset_index(inplace=True)
        data_dict = features.to_dict("records")

        # To insert data into mongodb server we
        # first need to convert into dictionary
        centers = model.cluster_centers_
        centers = centers.tolist()

        # Convert centers to there dictionary with respect to cluster and features
        Yellow = {}
        Green = {}
        Red = {}
        features = ["ATTENDANCE", "ASSIGNMENT_SCORE", "SUBMITTED_DEADLINE", "QUIZ_SCORE"]
        for i, f in enumerate(features):
            Yellow[f] = centers[0][i]
            Green[f] = centers[1][i]
            Red[f] = centers[2][i]

        temp = [(Yellow, Green, Red)]
        centers_df = pd.DataFrame(data=temp, columns=["Yellow", "Green", "Red"])
        centers_df.reset_index(inplace=True)
        centers_dict = centers_df.to_dict("records")

        # Insert into collection
        d_first_time = datetime.datetime.now()
        prediction_mongo_collection.insert_many(data_dict)
        centroid_mongo_collection.insert_many(centers_dict)
        d_second_time = datetime.datetime.now()
        d_time = d_second_time - d_first_time
        logger.info("Complete data dump into the mongodb server")

        return (
            features,
            log_features,
            f_time,
            p_time,
            d_time,
            total_number_of_data_points_features_extraction,
        )

# For module testing purpose
if __name__ == "__main__":
    predict = Predict()
    (
        features,
        log_features,
        f_time,
        p_time,
        d_time,
        total_number_of_data_points_features_extraction,
    ) = predict.prediction_for_all_students_and_dump_into_mongoserver()
