"""If there are no data then
we need ta make dataset first in data/make_dataset.py module
But we have a snowflake data
we connect with snowflake warehouse direct
and extract features from fuseclassroom database."""
import datetime
from pathlib import Path
import numpy as np
import botocore.discovery
import os 

from loguru import logger
from snowflake import connector

from src.utils.config import Config


class FeatureCreation:
    """
        Class for creating features and save it to local and S3 buccket.
        ...
        Attributes
        -----------
        bucket_name : str
            The name of the bucket in Amazon S3.
        src : str
            Source Location
        dst : str
            Destination Location
        Methods
        -----------
        download(src, dst='.', bucket_name=None)
            Downlaods the file from Amazon S3 and save in destination location.
        upload(src, dst='.', bucket_name=None)
            Upload from from source to destination in Amazon S3.
        """
    def __init__(self):
        logger.info("Connecting to the Snowflake  Server.")
        print(Config.base_path)
        self.conn = connector.connect(
            user=Config.user,
            password=Config.password,
            account=Config.account,
            database=Config.database,
            schema=Config.schema,
        )
        self.cur = self.conn.cursor()
        logger.info("Connected to the Snowflake  Server")

    # Feature extraction for all data frame
    def process_query_for_one_students_features(self,sql, student_course=(None, None)):
        """Process raw query and return pandas
        data frame of the student in a given course.
        Args:
            sql(query) : sql query.
        Returns:
            cur.fetch_pandas_all() : Dataframe
        """
        self.cur.execute(sql, student_course)
        # Fetch result from the cursor and deliver it as Pandas DataFrame.
        return self.cur.fetch_pandas_all()

    def create_features_for_one_student(self,student_course):
        """Process raw query and return features in Pandas Data
        Frame of the student in a given course.
        Args:
            No argument.
        Returns:
            data,log_d : Both are DataFrame.
        """
        # Get all Student and course combinations query.
        user_course_combination_query = """
        SELECT USERID AS STUDENTID, COURSEID, GUID FROM
        SCHOLARSHIP_ROLE_BINDER
        WHERE DELETED = 'FALSE' AND STATUS!='NULL' AND
        STATUS!='INACTIVE' AND STUDENTID =%s
            AND COURSEID = %s
        """

        # Execute above query and return DataFrmae form.
        logger.info("All students student_id and course_id combination extracting.")
        user_course_combination = self.process_query_for_one_students_features(
            user_course_combination_query,
            student_course,
        )
        logger.info("All students student_id and course_id combination extrected.")

        # Query query
        quiz_query = """
        SELECT UQAL.USERID AS STUDENTID,
        Q.COURSEID,
        AVG(DIV0(IFNULL(UQAL.OBTAINEDSCORE, 0), Q.FULLMARKS))
        AS QUIZ_SCORE
        FROM USERQUIZATTEMPTLOGS AS UQAL
        RIGHT JOIN QUIZ AS Q
            ON UQAL.QUIZID = Q._ID
        WHERE UQAL.DELETED='FALSE' AND UQAL.OBTAINEDSCORE <= Q.FULLMARKS
        AND UQAL.USERID =%s
            AND Q.COURSEID = %s
        GROUP BY UQAL.USERID, Q.COURSEID;"""

        # Execute quiz query and return DataFrame.
        logger.info(
            """All Students student_id and course_id and
        there quiz score combination extracting.""",
        )
        quiz = self.process_query_for_one_students_features(quiz_query, student_course)
        logger.info(
            """All Students student_id and course_id and there
        quiz score combination extracted.""",
        )

        # Assignment Query
        assignment_query = """
        SELECT SSA.STUDENTID, SSA.COURSEID,
                AVG(DIV0(IFNULL(SSA.GRADENUMBER, 0) , IA.TOTALGRADE))
                AS ASSIGNMENT_SCORE
                ,DIV0(COUNT_IF(SSA.SUBMITTEDWITHINDEADLINE='TRUE'),
                COUNT(SSA.SUBMITTEDWITHINDEADLINE))
                AS SUBMITTED_DEADLINE
            FROM STUDENT_SUBMITTED_ASSIGNMENTS as SSA
                LEFT JOIN INSTRUCTOR_ASSIGNMENTS AS IA
                    ON IA._ID = SSA.INSTRUCTORASSIGNMENTID
            WHERE SSA.ASSIGNMENTGRADED = 'TRUE' AND SSA.DELETED='FALSE'
            AND SSA.STUDENTID = %s
                    AND SSA.COURSEID = %s
        GROUP BY SSA.STUDENTID, SSA.COURSEID;
        """
        # Assignment query
        logger.info(
            """All students student_id and course_id and
        there assignment score and
        submitted deadline score combination extracting.""",
        )
        assignment = self.process_query_for_one_students_features(
            assignment_query,
            student_course,
        )
        logger.info(
            """All students student_id and course_id and
        there assignment score and submitted deadline score combination extracted.""",
        )

        # Attendance Query
        attendance_query = """
        SELECT p.COURSEID, p.STUDENTID, (q.PRESENT /  p.TOTAL) AS ATTENDANCE
        FROM (
            SELECT _ID, COURSEID, STUDENTID, count(*) AS TOTAL
            FROM FUSECLASSROOMAPPMONGOPROD.STUDENT_ATTENDANCE,
            lateral flatten(input => ATTENDANCEREPORTS) a
            GROUP BY 1,2,3) p
            INNER JOIN
            (
            SELECT _ID, COURSEID, STUDENTID, count(*) AS PRESENT
            FROM FUSECLASSROOMAPPMONGOPROD.STUDENT_ATTENDANCE,
            lateral flatten(input => ATTENDANCEREPORTS) a
            WHERE value:present = 'true' AND STUDENTID = %s AND
                    COURSEID = %s
            GROUP BY 1,2,3
            ) q ON p._ID = q._ID;
        """
        # Attendance query.
        logger.info(
            """All students student_id and course_id and
        there attendance score combination extracting.""",
        )
        attendance = self.process_query_for_one_students_features(
            attendance_query,
            student_course,
        )
        logger.info(
            """All students student_id and course_id and
        there attendance score combination extracted.""",
        )

        # Merging all features DataFrame
        logger.info("Combining all features.")
        data = user_course_combination
        data_column = [attendance, assignment, quiz]
        for i in data_column:
            data = data.merge(i, on=["COURSEID", "STUDENTID"], how="left")
        logger.info("Combined all features.")

        # Convert each column into proper data type
        columns = ["ATTENDANCE", "SUBMITTED_DEADLINE", "QUIZ_SCORE"]
        for i in columns:
            data[i] = data[i].astype(float)

        # Make seperate data frame which contain NAN values
        # nan_data_frame = data.copy()

        # Fill NAN value
        data = data.fillna(1)

        # Feature transformation
        logger.info("Feature transforming(log transformation).")
        log_d = data.copy()
        log_d["ATTENDANCE"] = np.log10(1 + log_d["ATTENDANCE"])
        log_d["SUBMITTED_DEADLINE"] = np.log10(1 + log_d["SUBMITTED_DEADLINE"])
        log_d["QUIZ_SCORE"] = np.log(1 + log_d["QUIZ_SCORE"])
        logger.info("Feature transform(log transformation) completed.")

        features = data
        log_features = log_d

        """Note : we predict model in log_features other are only
        for appearances features."""
        return features, log_features


    # Feature extraction for all data frame
    def process_query_for_all_students_features(self,sql):
        """Precess raw query and return  Pandas
        DataFrame of students in given courses.
        Args:
            sql(query) : Sql query.
        Returns:
            cur.fetch_pandas_all() : DataFrame
        """
        self.cur.execute(sql)
        # Fetch the result set from the cursor and deliver it as
        # the Pandas DataFrame.
        return self.cur.fetch_pandas_all()


    # Question are we extract features for all students?
    def create_features_for_all_students(self):
        """Precess raw query and return features in Pandas Data
        Frame of students in given courses.
        Args:
            No argument.
        Returns:
            data,log_d : Both are DataFrame
        """
        # Get all Student and Course combinations.
        user_course_combination_query = """
        SELECT USERID AS STUDENTID, COURSEID, GUID FROM SCHOLARSHIP_ROLE_BINDER
        WHERE DELETED = 'FALSE' AND STATUS!='NULL' AND STATUS!='INACTIVE'
        """

        # Execute above query and return DataFrame.
        logger.info("All student student_id and course_id combinations extracting")
        user_course_combination = self.process_query_for_all_students_features(
            user_course_combination_query,
        )
        logger.info("All student student_id and course_id combinations extrected")
        # Quiz score
        quiz_query = """
        SELECT UQAL.USERID AS STUDENTID,
        Q.COURSEID,
        AVG(DIV0(IFNULL(UQAL.OBTAINEDSCORE, 0), Q.FULLMARKS)) AS QUIZ_SCORE
        FROM USERQUIZATTEMPTLOGS AS UQAL
        RIGHT JOIN QUIZ AS Q
            ON UQAL.QUIZID = Q._ID
        WHERE UQAL.DELETED='FALSE' AND UQAL.OBTAINEDSCORE <= Q.FULLMARKS
        GROUP BY UQAL.USERID, Q.COURSEID;"""

        # Execute quiz query and return DataFrame.
        logger.info(
            """All students student_id and course_id and there
        quiz score combination extracting.""",
        )
        quiz = self.process_query_for_all_students_features(quiz_query)
        logger.info(
            """All students student_id and course_id and
        there quiz score combination extracted.""",
        )

        # Assignment Query
        assignment_query = """
            SELECT SSA.STUDENTID, SSA.COURSEID,
                AVG(DIV0(IFNULL(SSA.GRADENUMBER, 0) , IA.TOTALGRADE)) AS
                ASSIGNMENT_SCORE
                ,DIV0(COUNT_IF(SSA.SUBMITTEDWITHINDEADLINE='TRUE'),
                COUNT(SSA.SUBMITTEDWITHINDEADLINE)) AS SUBMITTED_DEADLINE
            FROM STUDENT_SUBMITTED_ASSIGNMENTS as SSA
                LEFT JOIN INSTRUCTOR_ASSIGNMENTS AS IA
                    ON IA._ID = SSA.INSTRUCTORASSIGNMENTID
            WHERE SSA.ASSIGNMENTGRADED = 'TRUE' AND SSA.DELETED='FALSE'
            GROUP BY SSA.STUDENTID, SSA.COURSEID;
            """
        # Execute assignment query and return DataFrame.
        logger.info(
            """All students student_id and course_id and there assignment score and
            submitted deadline score combination extracting.""",
        )
        assignment = self.process_query_for_all_students_features(assignment_query)
        logger.info(
            """All students student_id and course_id and there assignment score and
            submitted deadline score combination extracted.""",
        )

        # Attendance Query
        attendance_query = """
        SELECT p.COURSEID, p.STUDENTID, (q.PRESENT /  p.TOTAL) AS ATTENDANCE
        FROM (
            SELECT _ID, COURSEID, STUDENTID, count(*) AS TOTAL
            FROM FUSECLASSROOMAPPMONGOPROD.STUDENT_ATTENDANCE,
            lateral flatten(input => ATTENDANCEREPORTS) a
            GROUP BY 1,2,3) p
            INNER JOIN
            (
            SELECT _ID, COURSEID, STUDENTID, count(*) AS PRESENT
            FROM FUSECLASSROOMAPPMONGOPROD.STUDENT_ATTENDANCE,
            lateral flatten(input => ATTENDANCEREPORTS) a
            WHERE value:present = 'true'
            GROUP BY 1,2,3
            ) q ON p._ID = q._ID;
        """
        # Execute attendance query and return DataFrame.
        logger.info(
            """All students student_id and course_id and
            there attendance score combination extracting.""",
        )
        attendance = self.process_query_for_all_students_features(attendance_query)
        logger.info(
            """All students student_id and course_id and
            there attendance score combination extracted.""",
        )

        # Merging all features DataFrame
        logger.info("Combining all features.")
        data = user_course_combination
        data_column = [attendance, assignment, quiz]
        for i in data_column:
            data = data.merge(i, on=["COURSEID", "STUDENTID"], how="left")
        logger.info("Combined all features.")

        # Convert each column into proper data type
        columns = ["ATTENDANCE", "SUBMITTED_DEADLINE", "QUIZ_SCORE"]
        for i in columns:
            data[i] = data[i].astype(float)

        # Make seperate data frame which contain NAN values
        # nan_data_frame = data.copy()

        # Fill NAN value
        data = data.fillna(1)

        # Feature transformation
        logger.info("Feature transforming(log transformation).")
        log_d = data.copy()
        log_d["ATTENDANCE"] = np.log10(1 + log_d["ATTENDANCE"])
        log_d["SUBMITTED_DEADLINE"] = np.log10(1 + log_d["SUBMITTED_DEADLINE"])
        log_d["QUIZ_SCORE"] = np.log(1 + log_d["QUIZ_SCORE"])
        logger.info("Feature transform(log transformation) completed.")

        # Column rename and column add for backend database collection match column
        columns_to_be_renamed = {"STUDENTID": "predictedUser", "COURSEID": "courseId"}
        data.rename(columns=columns_to_be_renamed, inplace=True)
        data["predictBy"] = "MACH"
        data["predictedDate"] = datetime.datetime.now()
        data["predictedDate"] = data["predictedDate"].astype(str)

        features = data
        log_features = log_d

        """Note : we predict model in log_features other are only
        for appearances features."""

        # save data(features) at local
        data_dir = Config.LOCAL_DATA_DIR
        final_file = os.path.join(data_dir, "features-unlabelled_data.csv")
        features.to_csv(final_file, index=False)
        
        # Upload data to server
        # today = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")).replace(' ', '-')
        # s3_data_path = Path(Config.S3_DATA_DIR, f'student-status/data/{today}/features-unlabelled_data.csv')
        # try:
        #         Config.S3_BUCKET.upload(local_filename=Config.LOCAL_DATA_DIR,
        #       file_name=s3_data_path)
        # except botocore.exceptions.ClientError as e:
        #         logger.error(e)
        
        
        return features, log_features

# For model testing purpose
if __name__ == "__main__":
    featureCreation = FeatureCreation()
    features, log_features = featureCreation.create_features_for_all_students()



    # features, log_features = create_features_for_one_student(
    #     ("5f35213b5ce3280042be57ff", "5f35086067c8190042c216bf"),
    # )
    # features, log_features = create_features_for_all_students()
