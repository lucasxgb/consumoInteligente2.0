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


def login(matricula):
    criarJson = '{"matricula":"-"}'.replace('-', str(matricula))
    client.publish(nevoa_se_conectar, f"POST - 200 - hidrometro/{matricula} - loginHidrometro/ - {criarJson}", 1, False)


def alterarVazao(vazao):
    escolha = random.randint(1,3)
    # Se 3, mater a vazão
    if escolha == 1: # Aumentar vazão
        if vazao < 5:
            vazao += 1
            return vazao
        else:
            return vazao
    elif escolha == 2: # Diminuir vazão
        if vazao > 0:
            vazao -= 1
            return vazao
        else:
            return vazao
    else:
        return vazao


def obterMatricula():
    mat = input('Informe a matricula do seu hidrômetro -> ')
    while mat == "": # Colocar um validador para garantir que seja apenas um numero
        mat = input('Informe uma matricula valida -> ')
    mat = int(mat)
    return mat


def nevoaConectar(matricula):
    if matricula > 0 and matricula <= 100:
        return "nevoa/1"
    elif matricula > 100 and matricula <= 200:
        return "nevoa/2"
    elif matricula > 200 and matricula <= 300:
        return "nevoa/3"
    elif matricula > 300 and matricula <= 400:
        return "nevoa/4"
    elif matricula > 400 and matricula <= 500:
        return "nevoa/5"

vazao = 0
consumo = 0
bloqueado = 0
media = 0

broker = '172.16.103.3'
port = 3000

matricula = obterMatricula()
nevoa_se_conectar = nevoaConectar(matricula)

client_id = f"hidrometro_{matricula}"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker, port)
client.loop_start()

# Topicos ouvindo
client.subscribe(f"hidrometro/{matricula}")
client.subscribe("hidrometros")


client.on_connect = on_connect
client.on_message = on_message

login(matricula)

sleep(3.5)

dadosLogin = lista_de_requisições[0]
lista_de_requisições.pop(0)

consumo = int(json.loads(dadosLogin['json'])['consumoAtual'])

if json.loads(dadosLogin['json'])['bloqueado'] == "0":
    bloqueado = False
else:
    bloqueado = True

if json.loads(dadosLogin['json'])['login'] == "sucesso":
    while True:
        # Ficar esperando as mensagens chegar, e verificar - Chamar API dependendo do que veio
        # Mostrar mensagem que chegou na lista
        for conexao in lista_de_requisições:
            dados_requisicao = conexao
            verboHTTP = dados_requisicao["metodo"]
            status = dados_requisicao["status"]
            remetente = dados_requisicao["remetente"]
            rota = dados_requisicao["rota"]
            #print(dados_requisicao["json"])
            dadosJson = json.loads(dados_requisicao["json"])
            
            #print(f"metodo : {verboHTTP}, status : {status} , remetente : {remetente}, rota : {rota}, json : {dadosJson}")

            # Vericar os dados recebidos e alterar.

            if rota == "bloquearHidrometro/":  # Dados do Hidrometro -> Referente a rota 01
                bloqueado = True
            elif rota == "desbloquearHidrometro/":  # Dados do Hidrometro -> Referente a rota 01
                bloqueado = False
            elif rota == "media/":
                print(dadosJson)
                media = float(dadosJson['media'])
            lista_de_requisições.pop(0)
        
        sleep(2.5) 
        
        #print(f"Media: {media}")
        if consumo <= media:
            if bloqueado == False:
                vazao = alterarVazao(vazao)
                consumo += vazao
            else:
                vazao = 0

        criarJson = '{"consumo" : "-", "matricula" : "_", "vazamento" : "|"}'.replace("-",str(consumo)).replace("_",str(matricula)).replace("|",str(vazao))
        client.publish(nevoa_se_conectar, f"POST - 200 - hidrometro/{matricula} - dadosHidrometro/ - {criarJson}", 1, False)

client.loop_stop()