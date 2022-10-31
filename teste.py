import paho.mqtt.client as mqtt
from threading import Thread

broker = 'broker.hivemq.com'
port = 3000
topic = "nevoa_01/hidrometro_01"
client_id = 'nevoa_01'

def conectar(client, userdata, flags, rc):
    print("Conectado com sucesso no broker")
    #client.subscribe(topic)
    #client.publish(topic, "Publicação no topico raiz")


def mensagem(client, userdata, msg):
    print(msg.payload.decode("utf-8"))

client = mqtt.Client(client_id)
client.connect(broker)
client.loop_start()

while True:
    client.on_connect = conectar
    client.on_message = mensagem
    msgEnviar = input("Digite a msg -> ")
    client.publish(topic, msgEnviar)
    client.subscribe(topic)