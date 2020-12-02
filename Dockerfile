FROM python:3.9-alpine
COPY . /srv/app
RUN pip install -r requirements.txt
CMD python3 app.py