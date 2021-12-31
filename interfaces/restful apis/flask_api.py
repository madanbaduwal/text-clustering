# # In this module we take input from api endpoint and
# use src/models/predic_model.py for prediction.
# import numpy as np
# from flask import Flask, request, jsonify, render_template,Response
# from src.models.predict_model import predicted_from_studentid_courseid
# import json
# app = Flask(__name__)
# @app.route('/')
# def get_initial_response():
#     """Welcome message for the API."""
#     message = {
#         'api_version': 'v1.0',
#         'status': '200',
#         'message': 'Welcome to the Flask API'
#     }
#     resp = jsonify(message)
#     return resp
# @app.route('/predict',methods=['POST'])
# def predict():
#     if request.json:
#         j = request.json
#         student_id = j["student_id"]
#         courseid = j["course_id"]
#         features , prediction = predicted_from_studentid_courseid(
#   student_id,courseid)
#     else:
#         raise TypeError("Invalid Request Format")
#     pred = {
#     'student_id': student_id,
#     'course_id': courseid,
#     'Label': prediction
#     }
#     resp = jsonify(pred)
#     return resp
# @app.errorhandler(404)
# def page_not_found(e):
#     """Send message to the user with notFound 404 status."""
#     message = "This route is currently not supported."
#     " Please refer API documentation."
#     return Response(message, status=404)
# if __name__ == "__main__":
#     app.run(debug=True,port=5000)
# # curl -X POST --data '{"value": "txt"}' http://localhost:5000/predict
