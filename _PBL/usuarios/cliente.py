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


def login(matricula, nevoa_se_conectar):
    criarJson = '{"matricula":"-"}'.replace('-', str(matricula))
    client.publish(nevoa_se_conectar, f"POST - 200 - cliente/{matricula} - loginCliente/ - {criarJson}", 1, False)


def menuAux():
    print('=' * 10, '{Bem vindo}', '=' * 10)
    print('''Selecione a opção desejada
           [1] - VER HIDRÔMETRO
           [2] - VER HISTÓRICO HIDRÔMETRO
           [3] - GERAR CONTA
           [4] - PAGAR CONTA
           ''')
    opt = int(input('Opção -> '))
    return opt


def menu(client, matricula, nevoa_se_conectar):
    # O cliente manda os dados para a nevoa
    escolha = menuAux()
    criarJson = '{"matricula" : "-"}'.replace("-", str(matricula))
    if escolha == 1:
        client.publish(nevoa_se_conectar, f"GET - 200 - cliente/{matricula} - pegarHidrometroEspecifico/ - {criarJson}", 1, False)
    elif escolha == 2:
        client.publish(nevoa_se_conectar, f"GET - 200 - cliente/{matricula} - verHistoricoHidrometro/ - {criarJson}", 1, False)
    elif escolha == 3:
        client.publish(nevoa_se_conectar, f"GET - 200 - cliente/{matricula} - gerarConta/ - {criarJson}", 1, False)
    elif escolha == 4:
        client.publish(nevoa_se_conectar, f"POST - 200 - cliente/{matricula} - pagarConta/ - {criarJson}", 1, False)



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

broker = 'broker.hivemq.com'
port = 3000

matricula = obterMatricula()
nevoa_se_conectar = nevoaConectar(matricula)
client_id = f"cliente_{matricula}"
lista_de_requisições = []

client = mqtt.Client(client_id)
client.connect(broker)
client.loop_start()

# Topicos ouvindo
print(f"cliente/{matricula}")
client.subscribe(f"cliente/{matricula}")

client.on_connect = on_connect
client.on_message = on_message

login(matricula, nevoa_se_conectar)

sleep(2.5)

dadosLogin = lista_de_requisições[0]
lista_de_requisições.pop(0)

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
            dadosJson = dados_requisicao["json"]
            
            
            #print(f"metodo : {verboHTTP}, status : {status} , remetente : {remetente}, rota : {rota}, json : {dadosJson}")
            # Vericar os dados recebidos e mostrar em tela mensagens.

            if rota == "dadosHidrometro/":  # Dados do Hidrometro -> Referente a rota 01
                dadosJson = json.loads(dadosJson)["1"]
                informacoesHidro = dadosJson
                print(f"\n\nConsumo :  {informacoesHidro['consumoAtual']}")
                print(f"Vazamento :  {informacoesHidro['vazamento']}\n\n")
            elif rota == "historicoHidrometro/": # Historico do Hidrometro -> Referente a rota 02
                dadosJson = json.loads(dadosJson)["1"]
                informacoesHidro = dadosJson
                print("\n\nUltimas 5 informações do Hidrometro")
                print(f" Consumo Atual :  {informacoesHidro['consumoAtual']} M³")
                print(f" Consumo Anterior 01 :  {informacoesHidro['consumoAnterior01']} M³")
                print(f" Consumo Anterior 02 :  {informacoesHidro['consumoAnterior02']} M³")
                print(f" Consumo Anterior 03 :  {informacoesHidro['consumoAnterior03']} M³")
                print(f" Consumo Anterior 04 :  {informacoesHidro['consumoAnterior04']} M³ \n\n")
            elif rota == "contaGerada/": # Gerar Conta -> Referente a rota 03
                informacoesHidro = json.loads(dadosJson)
                print(informacoesHidro)
                print(f"\n\n Valor a Pagar:  {informacoesHidro['conta']}\n\n")
            elif rota == "contaPaga/": # Pagar Conta -> Referente a rota 04
                informacoesHidro = json.loads(dadosJson)
                print(f"\n\n Informação :  {informacoesHidro['conta']}\n\n")

            lista_de_requisições.pop(0)
        menu(client, matricula, nevoa_se_conectar)
        sleep(2.5)

client.loop_stop()