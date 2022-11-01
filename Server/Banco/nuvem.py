'''Arquivo para colocar a nuvem'''
'''Conexão mqtt'''
import random, json
from time import sleep
import paho.mqtt.client as mqtt
import threading

listaMensagem = []
class Nuvem:
    def retorno(self, cliente, dadosUsuario, mensagem):
        """ Função para tratar as mensagens que chega ao tópico que está escrito

            Caso a mensagem venha no tópico geral de hidrômetros ela será convertida em dict e enviada para o banco.

            Caso seja uma mensagem especifica, ocorre o tratamento de dados

         """
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        if mensagem.topic == 'nuvem/Hidrometros': #se a mensagem chegar no tópico de hidrometros, ele guarda a informação no banco
            listaMensagem.append(json.loads(mensagemDecode))
        else:  #se não ele tem que verificar se a mensagem que chega é pra bloquear ou não
            print("Mensagem recebida", mensagemDecode)
            print('Tópico da Mensagem', mensagem.topic)

    # Log - Registro do cliente
    def retornoLog(self, cliente, dadosUsuario, nivel, buf):
        print('Log: ', buf)


    def verificaConexao(self, cliente, dadosUsuario, flags, rc):
        """ Função para verificar o status da conexão

            Caso Rc == 0 Conexão bem sucessida
            Rc != 0 Algum tipo de erro, vai depender da numeração de retorno

         """
        if rc == 0:
            print('Conectado, código de retorno= ', rc)
        else:
            print('Não foi possível se conectar, código= ', rc)

    def inicia(self):
        """ Função para iniciar a conexão entre tópicos mqtt """
        broker = 'broker.hivemq.com'
        client = mqtt.Client('nuvem', random.randint(1, 1000))
        client.on_connect = self.verificaConexao  # metodo do mqtt responsavel por verificar se estabeleceu a conexão
        # ou não
        client.connect(broker)
        print('Conectado no servidor')
        return client

