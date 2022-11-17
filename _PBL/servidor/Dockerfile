FROM python:3
RUN pip install paho-mqtt
WORKDIR / usr / src / app
COPY  . .
EXPOSE 3000
CMD [ "servidor.py" ]
ENTRYPOINT ["python3"]