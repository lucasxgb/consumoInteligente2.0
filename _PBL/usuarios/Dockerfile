FROM python:3
RUN pip install paho-mqtt
WORKDIR / usr / src / app
COPY  . .
CMD [ "cliente.py", "adm.py"]
ENTRYPOINT ["python3"]