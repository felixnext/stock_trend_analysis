FROM python:3.6-slim

# install relevant packages
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt ./reqs.txt
RUN pip install -r reqs.txt

# execute data
RUN mkdir /app/app
RUN mkdir /app/recommender
RUN mkdir /app/data

# copy data and generate models
COPY ./data /app/data/
COPY ./recommender /app/recommender/

# TODO: run addditional setup?

# copy the final app data
COPY ./frontend /app/app/

# ports
EXPOSE 3001

# run command
WORKDIR /app/app
CMD ["python", "run.py"]
