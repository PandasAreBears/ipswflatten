FROM python:latest

RUN apt-get update
RUN apt-get install fuse libfuse3-dev bzip2 libbz2-dev cmake g++ git libattr1-dev zlib1g-dev -y

RUN git clone https://github.com/sgan81/apfs-fuse.git && \
    cd apfs-fuse && \
    git submodule update --init --recursive && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD src src

CMD ["/bin/bash"]