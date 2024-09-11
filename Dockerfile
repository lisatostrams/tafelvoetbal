FROM python:3.9-ubi8

USER root
COPY . /opt/app-root/src/
RUN pip install -r requirements.txt

EXPOSE 8050

CMD ["python","app.py"]