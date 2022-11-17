# Hidrometro
import paho.mqtt.client as mqtt
import json
from threading import Thread
from time import sleep
import random
from apiNevoa import Api


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
 

def DefinirNumeroNevoa():
    num = input('Informe o número da nevoa -> ')
    while num == "": # Colocar um validador para garantir que seja apenas um numero
        num = input('Informe uma número valido -> ')
    num = int(num)
    return num

api = Api()

broker = '172.16.103.3'
port = 3000

numeroNevoa = DefinirNumeroNevoa()
nuvem_se_conectar = "nuvem"

client_id = f"nevoa_{numeroNevoa}"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker, port)
client.loop_start()

# Topicos ouvindo 
print(f"nevoa/{numeroNevoa}")
client.subscribe(f"nevoa/{numeroNevoa}")
client.subscribe(f"nevoa")


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
            # Pegar informações do Hidrometro
            if rota == "pegarHidrometroEspecifico/": 
                retorno = api.GET_pegarInformacoesHidro(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - dadosHidrometro/ - {retorno}", 1, False)
            # Pegar informações do Hidrometro
            elif rota == "verHistoricoHidrometro/": 
                retorno = api.GET_pegarInformacoesHidro(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - historicoHidrometro/ - {retorno}", 1, False)
            # Gerar conta
            elif rota == "gerarConta/":
                retorno = api.GET_GerarBoleto(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - contaGerada/ - {retorno}", 1, False)
            # ADm informações do Hidrometro especifico
            elif rota == "hidrometroEspecifico/":
                retorno = api.GET_pegarInformacoesHidro(dadosJson['matricula'])
                client.publish("adm", f"GET - 200 - nevoa/{numeroNevoa} - hidroEspecifico/ - {retorno}", 1, False)
            # Nuvem, pegar rank de N hidrometros com mais gasto
            elif rota == "rankHidrometros/":
                retorno = api.GET_rankHidro(dadosJson['quantidade'])
                client.publish("nuvem", f"POST - 200 - nevoa/{numeroNevoa} - rankHidrometros/ - {retorno}", 1, False)
            elif rota == "media/":
                retorno = api.GET_media()
                client.publish("nuvem", f"POST - 200 - nevoa/{numeroNevoa} - media/ - {retorno}", 1, False)
                
        elif verboHTTP == "POST":  
            # Login Hidrometro 
            if rota == "loginHidrometro/":
                retorno = api.POST_LoginHidrometro(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - loginHidrometro/ - {retorno}", 1, False)
            # Login Cliente =====================
            elif rota == "loginCliente/": 
                retorno = api.POST_LoginCliente(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - dadosHidrometro/ - {retorno}", 1, False)
            # Pagar conta
            elif rota == "pagarConta/": 
                retorno = api.PUT_Pagarconta(dadosJson['matricula'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - contaPaga/ - {retorno}", 1, False)
                client.publish(f"hidrometro/{dadosJson['matricula']}", f"GET - 200 - nevoa/{numeroNevoa} - desbloquearHidrometro/ - {retorno}", 1, False)
            # Colocar dados do hidrometro
            elif rota == "dadosHidrometro/": 
                retorno = api.PUT_novoConsumo(dadosJson['matricula'], dadosJson['consumo'], dadosJson['vazamento'])
                client.publish(remetente, f"GET - 200 - nevoa/{numeroNevoa} - dadosHidrometro/ - {retorno}", 1, False)
            
        elif verboHTTP == "PUT":
           # Adm bloquear hidrometro
            if rota == "bloquearHidrometro/": 
                retorno = api.PUT_bloquear_hidrometro(dadosJson['matricula'])
                client.publish("adm", f"GET - 200 - nevoa/{numeroNevoa} - bloquearHidro/ - {retorno}", 1, False)
                client.publish(f"hidrometro/{dadosJson['matricula']}", f"GET - 200 - nevoa/{numeroNevoa} - bloquearHidrometro/ - {retorno}", 1, False)
            
        lista_de_requisições.pop(0)

client.loop_stop()