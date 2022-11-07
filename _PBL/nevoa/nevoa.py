# Hidrometro

import paho.mqtt.client as mqtt
import json
from threading import Thread
from time import sleep
import random

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
    
    lista_de_requisições.append(dic)
 

def DefinirNumeroNevoa():
    num = input('Informe o número da nevoa -> ')
    while num == "": # Colocar um validador para garantir que seja apenas um numero
        num = input('Informe uma número valido -> ')
    num = int(num)
    return num


broker = 'broker.hivemq.com'
port = 3000

numeroNevoa = DefinirNumeroNevoa()
nuvem_se_conectar = "nuvem"

client_id = f"nevoa_{numeroNevoa}"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker)
client.loop_start()

# Topicos ouvindo 
client.subscribe("hidrometro/#")

client.on_connect = on_connect
client.on_message = on_message

dadosHidro = sleep(0.5)

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
        
        #print(f"metodo : {verboHTTP}, status : {status} , remetente : {remetente}, rota : {rota}, json : {dadosJson}")

        # Vericar os dados recebidos e alterar.

        if verboHTTP == "GET":
            # 
            pass
        elif verboHTTP == "POST":  
            # Colocar dados do hidrometro
            # Login Hidrometro
                # Fazendo
            # Login Cliente
            pass
        elif verboHTTP == "PUT":
            pass
        elif verboHTTP == "DELETE":
            pass  
        
        lista_de_requisições.pop(0)

client.loop_stop()