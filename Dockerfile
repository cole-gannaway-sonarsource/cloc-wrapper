FROM alpine:3.12

# For alpine
RUN apk update 
RUN apk add curl
RUN apk add unzip
RUN apk add cloc
RUN apk add git

RUN apk add python3
RUN apk add py3-pip

# Install python packages
RUN pip3 install requests

WORKDIR /opt/sonar-loc-count/

# Copy scripts
COPY cloc.py cloc.py
COPY azure-devops-discover-repos.py azure-devops-discover-repos.py
COPY github-discover-repos.py github-discover-repos.py


# Do nothing
ENTRYPOINT ["tail", "-f", "/dev/null"]