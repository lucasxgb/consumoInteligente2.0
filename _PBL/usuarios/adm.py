# Cliente

import paho.mqtt.client as mqtt
import json
from threading import Thread
from time import sleep

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


def menuAux():
    print('=' * 10, '{Bem vindo}', '=' * 10)
    print('''Selecione a opção desejada
           [1] - VER OS N HIDROMETROS COM MAIOR GASTO
           [2] - PEGAR DADOS DE HIDROMETRO ESPECIFICO
           [3] - BLOQUEAR HIDROMETRO
           ''')
    opt = int(input('Opção -> '))
    return opt


def menu(client, nuvem_se_conectar):
    # O cliente manda os dados para a nuvem
    escolha = menuAux()
    criarJson = '{"" : ""}'
    if escolha == 1:
        qtd = int(input("Digite a quantidade de hidrometros: "))
        criarJson = '{"quantidade" : "-"}'.replace("-", str(qtd))
        client.publish(nuvem_se_conectar, f"GET - 200 - adm - rankHidrometros/ - {criarJson}", 1, False)
    elif escolha == 2: # Mandar para a nuvem, a nnuvem mandar para a nevoa e a nevoa mandar para o ADM
        matricula = int(input("Digite a matricula do Hidrometro: "))
        criarJson = '{"matricula" : "-"}'.replace("-", str(matricula))
        client.publish(nuvem_se_conectar, f"GET - 200 - adm - hidrometroEspecifico/ - {criarJson}", 1, False)
    elif escolha == 3:
        matricula = int(input("Digite a matricula do Hidrometro: "))
        criarJson = '{"matricula" : "-"}'.replace("-", str(matricula))
        client.publish(nuvem_se_conectar, f"PUT - 200 - adm - bloquearHidrometro/ - {criarJson}", 1, False)


broker = 'broker.hivemq.com'
port = 3000

nuvem_se_conectar = "nuvem"

client_id = f"adm"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker)
client.loop_start()

# Topicos ouvindo
client.subscribe("adm")

client.on_connect = on_connect
client.on_message = on_message

sleep(.8)

while True:
    # Ficar esperando as mensagens chegar, e verificar - Chamar API dependendo do que veio
    # Mostrar mensagem que chegou na lista
    for conexao in lista_de_requisições:
        dados_requisicao = conexao
        verboHTTP = dados_requisicao["metodo"]
        status = dados_requisicao["status"]
        remetente = dados_requisicao["remetente"]
        rota = dados_requisicao["rota"]
        dadosJson = dados_requisicao["json"]
        
        #print(f"metodo : {verboHTTP}, status : {status} , remetente : {remetente}, rota : {rota}, json : {dadosJson}")
        # Vericar os dados recebidos e mostrar em tela mensagens.

        if rota == "rank/":  # Dados do Hidrometro -> Referente a rota 01
            informacoesHidro = json.loads(dadosJson)
            print(informacoesHidro)
            
        elif rota == "hidroEspecifico/": # Historico do Hidrometro -> Referente a rota 02
            informacoesHidro = json.loads(dadosJson)
            print(f"\n\nConsumo: {informacoesHidro['1']['consumoAtual']} M³")
            print(f"Devendo: {informacoesHidro['1']['contaPagar']} R$")
            if informacoesHidro['1']['vazamento'] == "0":
                print("Vazamento: Não tem")
            else:
                print("Vazamento: Existente")
            if informacoesHidro['1']['bloqueado'] == "0":
                print("Bloqueado: Não\n\n")
            else:
                print("Bloqueado: Sim\n\n")

        elif rota == "bloquearHidro/": # Gerar Conta -> Referente a rota 03
            informacoesHidro = json.loads(dadosJson)
            print(informacoesHidro)
        
        elif rota == "rankHidrometros/":
            dadosJson =  json.loads(dadosJson)
            print("\n\n")
            for chave in dadosJson.keys():
                print( f"Matricula: {chave}      Quantidade Gasta: {dadosJson[chave]}")
            print("\n\n")
            

        lista_de_requisições.pop(0)
    menu(client, nuvem_se_conectar)
    sleep(2.5)

client.loop_stop()