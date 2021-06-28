FROM python:3.9.5-buster

WORKDIR /app

# install runtime dependencies
RUN pip install --no-cache-dir uwsgi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY labyrinth ./labyrinth
COPY instance ./instance
COPY labyrinth_main.py .

COPY uwsgi-docker.ini .

# setup 
RUN python instance/create_secret.py >> instance/config.py

# uwsgi port
EXPOSE 9112 

# http port
EXPOSE 9113

ENV INTERNAL_URL="http://localhost:9113"

CMD ["uwsgi", "uwsgi-docker.ini"]
