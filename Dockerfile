FROM python:3.8-slim-buster
WORKDIR /app
COPY pyproject.toml pyproject.toml
RUN poetry install
COPY . .
CMD [ "streamlit","run", "streamlit_app.py"]



# Use

## sudo docker build --tag python-docker .
## docker images