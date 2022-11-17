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

def obterNevoa(matricula):
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

broker = '127.0.0.1'
port = 3000

client_id = f"nuvem"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker, port)
client.loop_start()

# Topicos ouvindo 
client.subscribe("nuvem")

client.on_connect = on_connect
client.on_message = on_message

dadosHidro = sleep(0.8)


def pegarDadosMedia():
    while True:
        sleep(10)
        client.publish("nevoa", 'GET - 200 - nuvem - media/ - {"" : ""}', 1, False)


thread = Thread(target=pegarDadosMedia, args=[])
thread.start()

qtdRank = 0
media = 0

while True:
    # Ficar esperando as mensagens chegar, e verificar   
    # Mostrar mensagem que chegou na lista

    dicionarioRank = {}
    dicionarioMedia = {}

    

    for conexao in lista_de_requisições:
        dados_requisicao = conexao
        verboHTTP = dados_requisicao["metodo"]
        status = dados_requisicao["status"]
        remetente = dados_requisicao["remetente"]
        rota = dados_requisicao["rota"]
        dadosJson = json.loads(dados_requisicao["json"])
        
        if verboHTTP == "GET":
            # Rank de hidrometro
            if rota == "rankHidrometros/": 
                # Mandar msg para todos as nevoas
                qtdRank = int(dadosJson['quantidade'])
                client.publish("nevoa",f'GET - 200 - nuvem - rankHidrometros/ - {json.dumps(dadosJson)}', 1, False)
            # Pegar dados de hidrometro especifico
            elif rota == "hidrometroEspecifico/":
                nevoa = obterNevoa(int(dadosJson['matricula']))
                client.publish(nevoa, f"GET - 200 - nuvem - hidrometroEspecifico/ - {json.dumps(dadosJson)}", 1, False)
        elif verboHTTP == "PUT":
            # Pegar dados de hidrometro especifico
            if rota == "bloquearHidrometro/": 
                nevoa = obterNevoa(int(dadosJson['matricula']))
                client.publish(nevoa, f"GET - 200 - nuvem - bloquearHidrometro/ - {json.dumps(dadosJson)}", 1, False)
        elif verboHTTP == "POST":
            if rota == "rankHidrometros/":
                sleep(1)
                cont = 0
                for conexao2 in lista_de_requisições:
                    dados_requisicao2 = conexao2
                    verboHTTP2 = dados_requisicao2["metodo"]
                    rota2 = dados_requisicao2["rota"]
                    if verboHTTP2 == "POST":
                        if rota2 == "rankHidrometros/":
                            dadosJson2 = json.loads(dados_requisicao2["json"])
                            dicionarioRank.update(dadosJson2)
                            if cont != 0:   # Pois se cont for 0, é o item atual e ele não vai ser deletado aqui e sim mais abaixo
                                lista_de_requisições.pop(cont)
                    cont += 1
                # Fazer rank dos 30 e mandar pro adm
                cont = 0
                dicRetorno = {}
                for i in sorted(dicionarioRank, key = dicionarioRank.get, reverse=True):
                    dicRetorno[i] = dicionarioRank[i]
                    cont+=1
                    if cont >= qtdRank:
                        break    
                # Mandar msg para todos as nevoas
                client.publish("adm", f'GET - 200 - nuvem - rankHidrometros/ - {json.dumps(dicRetorno)}', 1, False)
                dicionarioRank = {}
                qtdRank = 0

            # calcular a media geral e bloquear os hidrometros acima
            elif rota == "media/":
                media = 0
                sleep(1)
                cont = 0
                qtd = 0
                for conexao2 in lista_de_requisições:
                    dados_requisicao2 = conexao2
                    verboHTTP2 = dados_requisicao2["metodo"]
                    rota2 = dados_requisicao2["rota"]
                    if verboHTTP2 == "POST":
                        if rota2 == "media/":
                            dadosJson2 = json.loads(dados_requisicao2["json"])
                            dicionarioMedia.update(dadosJson2)
                            qtd += 1
                            media += float(dadosJson2["media"])
                            if cont != 0:   # Pois se cont for 0, é o item atual e ele não vai ser deletado aqui e sim mais abaixo
                                lista_de_requisições.pop(cont)
                    cont += 1
                # Definir a media
                #
                # Mandar msg para todos os hidrometros (mandar media de bloqueio)
                media = media / qtd
                retornar = "{-}"
                retornar = retornar.replace("-", f'"media" : "{media}"')

                client.publish("hidrometros", f'POST - 200 - nuvem - media/ - {retornar}', 1, False)
        
        lista_de_requisições.pop(0)

client.loop_stop()