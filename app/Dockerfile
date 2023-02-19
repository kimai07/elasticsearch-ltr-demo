FROM python:3.9

RUN apt-get update && \
    apt-get install --no-install-recommends -y git default-jre curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | pip install -r /dev/stdin

WORKDIR /app
RUN git clone -b es_7_17_4 https://github.com/o19s/elasticsearch-learning-to-rank.git

COPY run.sh /app/run.sh

CMD ["bash", "run.sh"]