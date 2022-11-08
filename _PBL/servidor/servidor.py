# Nuvem
import paho.mqtt.client as mqtt
import json
from threading import Thread
from time import sleep
import random
from apiNuvem import Api

"""
    Topicos
        nevoa/id/hidrometros/id
"""


def on_connect(client, userdata, flags, rc):
    """ Função para verificar o status da conexão

            Caso Rc == 0 Conexão bem sucessida
            Rc != 0 Algum tipo de erro, vai depender da numeração de retorno

         """
    if rc == 0:
        print('Conectado, código de retorno = ', rc)
    else:
        print('Não foi possível se conectar, código = ', rc)


def on_message(client, userdata, msg):
    # Colocar dados de mensagem em um dicionario e colocar em fila para tratar
    dados = str(msg.payload.decode("utf-8")).split(" - ")

    dic = {"metodo" : dados[0], "status" : dados[1] , "remetente" : dados[2], "rota" : dados[3], "json" : dados[4]}
    print(dic)
    lista_de_requisições.append(dic)
 

api = Api()

broker = 'broker.hivemq.com'
port = 3000

client_id = f"nuvem"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker)
client.loop_start()

# Topicos ouvindo 
client.subscribe("nuvem")

client.on_connect = on_connect
client.on_message = on_message

dadosHidro = sleep(0.8)

while True:
    # Ficar esperando as mensagens chegar, e verificar   
    # Mostrar mensagem que chegou na lista
    for conexao in lista_de_requisições:
        dados_requisicao = conexao
        verboHTTP = dados_requisicao["metodo"]
        status = dados_requisicao["status"]
        remetente = dados_requisicao["remetente"]
        rota = dados_requisicao["rota"]
        dadosJson = json.loads(dados_requisicao["json"])
        
        if verboHTTP == "GET":
           if rota == "rankHidrometros/": 
                retorno = api.rank10()
                client.publish(remetente, f"GET - 200 - nuvem - dadosHidrometro/ - {retorno}", 1, False)
        elif verboHTTP == "POST":  
           pass
        elif verboHTTP == "PUT":
            pass
            
        
        
        lista_de_requisições.pop(0)

client.loop_stop()