FROM ubuntu:22.04
RUN apt-get update
RUN apt install sudo
WORKDIR mosquitto /
RUN apt-get install -y mosquitto
RUN sudo mkdir config/
RUN sudo mkdir data/
RUN sudo mkdir log/
RUN sudo touch config/mosquitto.conf  
RUN sudo chmod 777 log/
RUN sudo chmod 777 data/
RUN sudo chmod 777 config/
RUN sudo echo -e "allow_anonymous true" >> config/mosquitto.conf
RUN sudo echo -e "listener 3000" >> config/mosquitto.conf
RUN sudo echo -e  "persistence true" >> config/mosquitto.conf
RUN sudo echo -e  "persistence_location data/" >> config/mosquitto.conf
RUN sudo echo -e  "log_dest file log/mosquitto.log" >> config/mosquitto.conf 
EXPOSE 3000

 



