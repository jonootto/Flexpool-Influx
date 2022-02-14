# set base image (host OS)
FROM python:slim

# set the working directory in the container
RUN useradd --create-home flexstat
WORKDIR /home/flexstat
# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
# RUN apt-get update && \
#     apt-get install -y gcc && \
#     pip install --upgrade -r requirements.txt && \
#     apt-get purge -y gcc && apt-get -y autoremove && \
#     rm -rf /var/lib/apt/lists/*
 RUN apt-get update && \
     pip install --upgrade -r requirements.txt && \
     apt-get purge -y gcc && apt-get -y autoremove && \
     rm -rf /var/lib/apt/lists/*
USER flexstat
# copy the content of the local src directory to the working directory

COPY src/ .

# command to run on container start
EXPOSE 8000
CMD [ "python","-u","./getstats.py" ] 