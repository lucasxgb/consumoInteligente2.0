'''Arquivo para colocar a nuvem'''
'''Conexão mqtt'''
import random, json
from time import sleep
import paho.mqtt.client as mqtt
import threading

listaMensagem = []
listaMedia = []
class Nuvem:
    def retorno(self, cliente, dadosUsuario, mensagem):
        """ Função para tratar as mensagens que chega ao tópico que está escrito

            Caso a mensagem venha no tópico geral de hidrômetros ela será convertida em dict e enviada para o banco.

            Caso seja uma mensagem especifica, ocorre o tratamento de dados

         """
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        if mensagem.topic == 'nuvem/Hidrometro': #topico para um hidrômetro especifico
            listaMensagem.append(json.loads(mensagemDecode))
        elif mensagem.topic == 'nuvem/Medias':
            self.calculaMedia() 
            self.enviaMedia()


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

    def inscrevendoTopico(self):
        """ Função responsável por inscrever a névoa no tópico do hidrômetro utilizando mqtt """
        client = self.inicia()
        client.loop_start()  # para ver o retorno das chamadas
        c = True
        while c == True:
            client.subscribe('nuvem/Medias', 1)
            client.on_message = self.retorno# inserindo a função de retorno

    def calculaMedia(self):
        valor = 0
        mediaGeral = 0
        for item in listaMedia:
            valor += item
        mediaGeral = (valor/len(listaMedia))
        for item in listaMedia:
            listaMedia.remove(item)
        return mediaGeral

    def enviaMedia(self):
        """ Função responsável por inscrever a névoa no tópico do hidrômetro utilizando mqtt """
        client = self.inicia()
        media = self.calculaMedia()
        client.loop_start()  # para ver o retorno das chamadas
        c = True
        while c == True:
            client.subscribe('nuvem/mediaCorte', 1)
            client.publish('nuvem/mediaCorte', media)
            client.on_message = self.retorno  # inserindo a função de retorno
nova = Nuvem()
nova.inscrevendoTopico()
