"""IN this model we create a simple web app.
We take input from user(UI) and
do prediction using src/models/predict_model.py"""
import datetime
import os
import sys

# we up directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from pymongo import MongoClient

from config import settings
from src.models.predict_model import predicted_for_one_student
from src.models.predict_model import predicted_in_dummy_features
from src.models.predict_model import (
    prediction_for_all_students_and_dump_into_mongoserver,
)


def app():
    """Function that create web app"""

    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # st.set_page_config(layout="wide")
    # Add text and data

    # Add a title
    # st.title('My first app')
    # Along with magic commands, st.write() is Streamlit’s “Swiss Army knife”.
    # You can pass almost anything to st.write():
    # text, data, Matplotlib figures, Altair charts, and more. Don’t worry,
    #  Streamlit will figure it out and render things the right way.
    # st.write()  # write
    # your own markdown.
    st.markdown(
        """<h1 style='text-align: center; color: black;'>
            Student status engine v2</h1>""",
        unsafe_allow_html=True,
    )

    # Write a data frame
    # st.dataframe()
    # st.table()

    # Use magic (streamlit call nagarikana ni dherai garna milxa)
    # """
    # # My first app
    # Here's our first attempt at using data to create a table:
    # """

    # df = pd.DataFrame({
    # 'first column': [1, 2, 3, 4],
    # 'second column': [10, 20, 30, 40]
    # })

    # df

    # Draw charts and maps
    # st.line/bar/..(dataframe)

    # Add interactivity with widgets
    # Checkbox
    # if st.checkbox('Show dataframe'):
    #  (click garyapaxi sabai dekhauxa tyati matra)
    #     chart_data = pd.DataFrame(
    #     np.random.randn(20, 3),
    #     columns=['a', 'b', 'c'])
    #     chart_data

    # option = st.selectbox(      # kunai auta select garyasi k garni vanni
    # 'Which number do you like best?',
    #  [1,2,3])
    # 'You selected: ', option
    #  you can put your logic here
    #  if option == 1:
    #      then...

    options = [
        "predicted_in_dummy_features",
        "predicted_for_one_student",
        "prediction_for_all_students_and_dump_into_mongoserver",
        "Label Interpretation",
    ]

    option = st.sidebar.selectbox("What do you want?", options)

    # Prediction in dummy features
    if option == "predicted_in_dummy_features":
        st.markdown(
            """<h4 style='text-align: center; color: black;padding-top: 1rem;'>
            Prediction in dummy data for normalized features</h4>""",
            unsafe_allow_html=True,
        )
        first_c, second_c, third_c, fourth_c = st.beta_columns(4)
        with first_c:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                attendance_score</h5>""",
                unsafe_allow_html=True,
            )
            atten = st.number_input(".")
        with second_c:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                assignment_score</h5>""",
                unsafe_allow_html=True,
            )
            assign = st.number_input("..")
        with third_c:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                submitted_deadline</h5>""",
                unsafe_allow_html=True,
            )
            submitt = st.number_input("...")
        with fourth_c:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                quiz_score</h5>""",
                unsafe_allow_html=True,
            )
            quiz = st.number_input("....")
        with third_c:
            if st.button("Predict"):
                pred_cluster, pred_class = predicted_in_dummy_features(
                    [assign, submitt, quiz, atten],
                )

                st.write(pred_class[0])
                st.image(f"../references/{pred_class[0]}.jpg")

    # predicted_for_one_student
    if option == "predicted_for_one_student":
        st.markdown(
            """<h4 style='text-align: center; color: black;'>
            Prediction in actual data.</h4>""",
            unsafe_allow_html=True,
        )
        first_column, second_column = st.beta_columns(2)
        with first_column:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                Student_id</h5>""",
                unsafe_allow_html=True,
            )
            student_id = st.text_input(".....")
        with second_column:
            st.markdown(
                "<h5 style='text-align: center; color: black;'>Course_id</h5>",
                unsafe_allow_html=True,
            )
            course_id = st.text_input("......")
        with second_column:
            if st.button("Predict"):
                first1_time = datetime.datetime.now()
                (
                    features,
                    log_features,
                    pred_cluster,
                    pred_class,
                ) = predicted_for_one_student(student_id, course_id)
                second2_time = datetime.datetime.now()
                st.write(f"Prediction is:{second2_time-first1_time}")

                features = features.to_numpy()
                st.write("ATTENDANCE_SCORE:", features[0][3])
                st.write("ASSIGNMENT_SCORE :", features[0][4])
                st.write("ASSIGNMENT_SUBMITTED_DEADLINE:", features[0][5])
                st.write("QUIZ_SCORE:", features[0][6])
                st.write(pred_class[0])
                st.image(f"../references/{pred_class[0]}.jpg")

    # prediction_for_all_students_and_dump_into_mongoserver
    if option == "prediction_for_all_students_and_dump_into_mongoserver":
        st.markdown(
            """<h4 style='text-align: center; color: black;padding-top: 1rem;'>
            Prediction</h4>""",
            unsafe_allow_html=True,
        )
        if st.button("prediction_for_all_students_and_dump_into_mongoserver"):
            (
                features,
                log_features,
                f_time,
                p_time,
                d_time,
                total_data_points,
            ) = prediction_for_all_students_and_dump_into_mongoserver()
            first_column, second_column, third_column = st.beta_columns(3)
            with first_column:
                with st.beta_expander("Feature Creation"):
                    st.write(
                        """
                        At first we connect with snowflake.Then we do
                        query and create features.
                        """,
                    )
                st.write(f"Feature extraction time is:{f_time}")
                st.write(
                    f"Total number of pints extracts:{total_data_points}",
                )
            with second_column:
                with st.beta_expander("Prediction"):
                    st.write(
                        """
                        In this phase , we load pretrain KMeans
                        clustering model.We do prediction on features.
                        which  have created previously.
                        """,
                    )
                st.write(
                    f"Total data points extractt is:{total_data_points}",
                )
                st.write(f"Prediction time is:{p_time}")

            with third_column:
                with st.beta_expander(
                    """Dump prediction data into prediction result folder into
                    .csv file formate and mongodb server """,
                ):
                    st.write(
                        """
                        We dump predicted  data into the mongo server.
                        """,
                    )
                    st.write(f"Dump time is:{d_time}")

            # fig, ax = plt.subplots(figsize=(16, 9))
            # st.bar_chart(st.bar_chart(features['Label']))

    if option == "Label Interpretation":
        first_column, second_column = st.beta_columns(2)
        with first_column:
            st.markdown(
                """<h5 style='text-align: center; color: black;'>
                Student_id</h5>""",
                unsafe_allow_html=True,
            )
            # student_id = st.text_input(".")

            options1 = st.multiselect(
                "Select student id",
                [
                    "60791f80d1093d0093880a8a",
                    "60791f89d1093d0093880ae1",
                    "5f1ebb6166c06f0042f3d9a9",
                    "5fa7bc8de8a8960042d8248d",
                    "5f4fae61783b130042cebd98",
                    "5ff2909c619a03005147ebe0",
                    "5f59e2bf84fd9a0042c74c17",
                    "605ad4458d4e39009842e694",
                    "5f3520f05ce3280042be567b",
                    "5f1e629f27632a0042d1f8ff",
                ],
                ["60791f80d1093d0093880a8a"],
            )
            student_id = options1[0]

        with second_column:
            st.markdown(
                "<h5 style='text-align: center; color: black;'>Course_id</h5>",
                unsafe_allow_html=True,
            )
            # course_id = st.text_input("..")
            options2 = st.multiselect(
                "Select course id",
                [
                    "6066b7ff62de4e009e0cfd01",
                    "60796b4d659bfd0093be7706",
                    "5f1ec4a227632a0042d20c60",
                    "5fa7bd1cd37cfc0042a9d358",
                    "5f4f5ca2783b130042ceb8ce",
                    "5fe17caf5cb1050051e39820",
                    "5f59cc2584fd9a0042c74882",
                    "605ad60616b4380098462e04",
                    "5f35089637202800424aa0e5",
                    "5f1aa4e8ebacb00042a33470",
                ],
                ["6066b7ff62de4e009e0cfd01"],
            )
            course_id = options2[0]

        # with second_column:
        if st.button("Prediction"):
            try:
                client = MongoClient(settings.mongo_server)
                print("Connected successfully!!!")
            except:
                print("Could not connect to MongoDB")
            # database
            db = client[settings.mongo_database]

            # collection
            prediction_collection = db[settings.prediction_mongo_collection]
            prediction_query = {"predictedUser": student_id, "courseId": course_id}
            prediction_result = prediction_collection.find_one(
                prediction_query,
            )  # Get list value
            
            student_id = prediction_result["predictedUser"]
            course_id = prediction_result["courseId"]

            prediction_result_numpy_array = np.array(
                [
                    prediction_result["ATTENDANCE"],
                    prediction_result["ASSIGNMENT_SCORE"],
                    prediction_result["SUBMITTED_DEADLINE"],
                    prediction_result["QUIZ_SCORE"],
                ],
            )
            label = prediction_result["originalLabel"]
            att = round(np.array(prediction_result_numpy_array)[0] * 100, 0)
            st.write(
                "Attendance Score:",
                str(att),
                "%",
            )
            ass = round(np.array(prediction_result_numpy_array)[1] * 100, 0)
            st.write(
                "Assignment Score :",
                str(ass),
                "%",
            )
            sub = round(np.array(prediction_result_numpy_array)[2] * 100, 0)
            st.write(
                "Assignment Submitted Deadline Score:",
                str(sub),
                "%",
            )
            qu = round(np.array(prediction_result_numpy_array)[3] * 100, 0)
            st.write(
                "Quiz Score:",
                str(qu),
                "%",
            )
            st.write("Prediction :", label)
            pred_nump_log = np.array(
                [
                    np.log10(1 + prediction_result["ATTENDANCE"]),
                    prediction_result["ASSIGNMENT_SCORE"],
                    np.log10(1 + prediction_result["SUBMITTED_DEADLINE"]),
                    np.log(1 + prediction_result["QUIZ_SCORE"]),
                ],
            )

            centers_collection = db[settings.centroid_mongo_collection]
            centers_query = {"index": 0}
            centers_result = centers_collection.find_one(centers_query)
            centers_result_numpy_array = np.array(
                [
                    centers_result["Yellow"],
                    centers_result["Green"],
                    centers_result["Red"],
                ],
            )
            print("centers_result_numpy_array", centers_result_numpy_array)

            if label == "Red":
                final_base_bar = [
                    10 ** centers_result["Yellow"]["ATTENDANCE"] - 1,
                    centers_result["Yellow"]["ASSIGNMENT_SCORE"],
                    10 ** centers_result["Yellow"]["SUBMITTED_DEADLINE"] - 1,
                    np.exp(centers_result["Yellow"]["QUIZ_SCORE"]) - 1,
                ]
                obtain_color = "#FF0000"
                base_color = "#FFFF00"
            elif label == "Yellow":
                final_base_bar = [
                    10 ** centers_result["Yellow"]["ATTENDANCE"] - 1,
                    centers_result["Yellow"]["ASSIGNMENT_SCORE"],
                    10 ** centers_result["Yellow"]["SUBMITTED_DEADLINE"] - 1,
                    np.exp(centers_result["Yellow"]["QUIZ_SCORE"]) - 1,
                ]
                base_color = "#00FF00"
                obtain_color = "#FFFF00"
            else:
                final_base_bar = [
                    10 ** centers_result["Yellow"]["ATTENDANCE"] - 1,
                    centers_result["Yellow"]["ASSIGNMENT_SCORE"],
                    10 ** centers_result["Yellow"]["SUBMITTED_DEADLINE"] - 1,
                    np.exp(centers_result["Yellow"]["QUIZ_SCORE"]) - 1,
                ]
                obtain_color = "#00FF00"
                base_color = "#00FF00"
            pred_r_expo = [
                10 ** pred_nump_log[0] - 1,
                pred_nump_log[1],
                10 ** pred_nump_log[2] - 1,
                np.exp(pred_nump_log[3]) - 1,
            ]

            percentage_score = np.round(
                (-1)
                * (
                    (np.array(final_base_bar) - np.array(pred_r_expo))
                    / np.array(final_base_bar)
                )
                * 100,
                0,
            )

            fe = ["ATTENDANCE", "ASSIGNMENT", "SUBMITTED_DEADLINE", "QUIZ"]
            fig, ax = plt.subplots()
            ind = [x for x, _ in enumerate(fe)]
            plt.bar(
                ind,
                final_base_bar,
                width=0.25,
                label="Base reference",
                color=base_color,
            )
            graph = plt.bar(
                [0.27, 1.27, 2.27, 3.27],
                pred_r_expo,
                0.25,
                label="Obtained score",
                color=obtain_color,
            )

            i = 0
            for p in graph:
                width = p.get_width()
                height = p.get_height()
                x, y = p.get_xy()
                plt.text(
                    x + width / 2,
                    y + height * 1.01,
                    str(np.round(percentage_score[i], 2)),
                    ha="center",
                    weight="bold",
                )
                i += 1

            plt.xticks(ind, fe)
            # plt.ylabel("Obtained score")
            # plt.xlabel("Features")
            plt.legend(loc="upper right")
            plt.title("AI Explanation")
            st.pyplot(fig)


if __name__ == "__main__":
    app()
