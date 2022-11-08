import paho.mqtt.client as mqtt #importação cliente mqtt
import time
########### instanciando um cliente ###############
#cliente = mqtt.Client('Id_cliente')

############ Se conectando a um broker ############
#cliente.connect('Broker')

############ publicando em um tópico ##############
#cliente.publish('topico/publicar', 'o que vai publicar')

############ Função de retorno para processar as mensagens ##############
def retorno(cliente, dadosUsuario, mensagem):
    mensagemDecode = str(mensagem.payload.decode('utf-8'))
    print('aqui')
    print("Mensagem recebida", mensagemDecode)
    print('Tópico da Mensagem', mensagem.topic)

########### Log - Registro do cliente #################
def retornoLog(cliente, dadosUsuario, nivel, buf):
    print('Log: ', buf)

######## Verifica conexão ################
def verifcaConexao(cliente, dadosUsuario, flags, rc):
    if rc ==0:
        print('Conectado, código de retorno= ', rc)
    else:
        print('Não foi possível se conectar, código= ', rc)

broker = '127.0.0.1'
port = 3000
client = mqtt.Client('MatriculaHidro')
print('Conectando no broker')
client.connect(broker, port)
client.loop_start()
print('Se inscrevendo no tópico')
client.subscribe('enviarDados/Hidrometros', qos = 0)
print('Publicando no tópico')
client.publish('enviarDados/Hidrometros', 'Dados')
client.on_message = retorno #inserindo a função de retorno
client.on_log = retornoLog #retorno do log das mensagens
time.sleep(4)
client.loop_stop()