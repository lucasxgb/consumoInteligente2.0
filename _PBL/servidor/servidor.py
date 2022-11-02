import paho.mqtt.client as mqtt
from threading import Thread
from time import sleep

broker = 'broker.hivemq.com'
port = 3000
client_id = 'servidor'

lista_de_requisições = []

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
    
    print(f"metodo: {dados[0]} - status: {dados[1]} - topico: {dados[2]} - remetente: {dados[3]} - msg: {dados[4]}")
    
    dic = {"metodo" : dados[0], "status" : dados[1] ,"topico" : dados[2], "remetente" : dados[3], "rota" : dados[4], "msg" : dados[5]}
    lista_de_requisições.append(dic)


client = mqtt.Client("teste")
client.connect(broker)
client.loop_start()

# Topicos ouvindo
client.subscribe("nevoa/#")
client.subscribe("adm")
client.subscribe("cliente")

client.on_connect = on_connect
client.on_message = on_message

client.publish("nevoa/01", f"GET - 700 - nevoa/01 - nevoa - nevoa conectada ao servidor", 1, False)

cont = 100

while True:
    # Ficar esperando as mensagens chegar, e verificar - Chamar API dependendo     

    cont += 100
    for conexao in lista_de_requisições:
        dados_requisicao = conexao  
        
        verboHTTP = dados_requisicao["metodo"]
        status = dados_requisicao["status"]
        remetente = dados_requisicao["remetente"]
        msg = dados_requisicao["msg"]
        topicoRemetente = dados_requisicao["topico"]
        rota = dados_requisicao["rota"]
        
        print(f"metodo: {verboHTTP}, status: {status} , topico: {topicoRemetente}, remetente: {remetente}, msg: {msg}")
        
        ## API aqui
        # client.publish(topic, msgEnviar)
        
        #client.publish("nevoa/01", f"GET - {cont} - nevoa/01 - nevoa - fazer_tal_coisa - nevoa conectada ao servidor", 1, False)

        if remetente == "hidrometro":
            # receber dados do hidrometro, e salvar no banco
            pass
        elif remetente == "servidor":
            # receber dados do hidrometro, e mandar resposta
            pass
        elif remetente == "adm":
            # receber dados do adm, e mandar resposta
            pass
            
        lista_de_requisições.pop(0)
    

client.loop_stop()