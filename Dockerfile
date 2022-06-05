FROM python:3.7-slim

RUN apt update && \
    apt install -y build-essential libomp-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY setriq_service .
ENV DEFAULT_METRIC_SPEC=default_metric_spec.json

EXPOSE 6000
EXPOSE 9000

CMD ["seldon-core-microservice", "SetriqService", "--service-type=MODEL", "--persistence=0"]
