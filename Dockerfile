FROM python:3.9

RUN mkdir /iss_tracker
WORKDIR /iss_tracker
COPY requirements.txt /iss_tracker/requirements.txt
RUN pip install -r /iss_tracker/requirements.txt
COPY iss_tracker.py /iss_tracker/iss_tracker.py

ENTRYPOINT ["python"]
CMD ["iss_tracker.py"]