##########################################################
# first build and test algolibs for the solver libraries #
##########################################################
FROM gcc:9.4 as algolibs-base

WORKDIR /usr/src/algolibs

RUN apt-get update && apt-get install -y \
  cmake

COPY algolibs/solvers ./solvers
COPY algolibs/CMakeLists.txt .

FROM algolibs-base as algolibs-test

COPY algolibs/test ./test
COPY algolibs/graphbuilder ./graphbuilder
COPY algolibs/CMakeLists.txt.gtest .

RUN mkdir build
RUN cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=RELEASE -DBUILD_TESTS=ON -DBUILD_BENCHMARKS=OFF
RUN cmake --build build

WORKDIR /usr/src/algolibs/build/test/
RUN ctest -V
WORKDIR /usr/src/algolibs

FROM algolibs-base as algolibs-release

RUN mkdir build
RUN cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=RELEASE -DBUILD_TESTS=OFF -DBUILD_BENCHMARKS=OFF
RUN cmake --build build

##################################################################
# then package the backend python application,                   #  
# using the shared libraries (.so files) from the previous stage #
##################################################################
FROM python:3.9.5-buster as base

WORKDIR /app

# copy source and share libraries
COPY backend/labyrinth ./labyrinth
COPY backend/instance ./instance
RUN rm -rf instance/lib && mkdir instance/lib
COPY --from=algolibs-release /usr/src/algolibs/build/solvers/*.so instance/lib/

FROM base as dev

COPY backend/dev-requirements.txt .
RUN pip install --no-cache-dir -r dev-requirements.txt

# lint
FROM dev as lint
RUN flake8 . --count --max-line-length=120 --max-complexity=10 --show-source --statistics --exclude __pycache__,venv

# test
FROM dev as test 
COPY backend/pytest.ini backend/conftest.py ./
COPY backend/tests ./tests
RUN pytest .

FROM base as release

# install runtime dependencies
RUN pip install --no-cache-dir uwsgi

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy production-relevant source
COPY backend/labyrinth_main.py backend/uwsgi-docker.ini ./

# setup 
RUN python instance/create_secret.py >> instance/config.py

# uwsgi port
EXPOSE 9112 

# http port
EXPOSE 9113

ENV INTERNAL_URL="http://localhost:9113"

CMD ["uwsgi", "uwsgi-docker.ini"]
