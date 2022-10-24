''' Se inscreve no tópico e manda para o servidor principal '''
import paho.mqtt.client as mqtt
import time


listaMensagem = [] #mensagens que recebo entram na lista
class Conexao():
    def retorno(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        listaMensagem.append(mensagemDecode)

    ########### Log - Registro do cliente #################
    def retornoLog(self, cliente, dadosUsuario, nivel, buf):
        print('Log: ', buf)

    ######## Verifica conexão ################
    def verificaConexao(self, cliente, dadosUsuario, flags, rc):
        if rc == 0:
            print('Conectado, código de retorno= ', rc)
        else:
            print('Não foi possível se conectar, código= ', rc)

    ###### metodo para publicar no tópico #######
    #def publica(self, urlTopico, dadosEnviar):
    #   return urlTopico, dadosEnviar
    def inicia(self):
        broker = 'broker.hivemq.com'
        client = mqtt.Client('nev')
        client.on_connect = self.verificaConexao #metodo do mqtt responsavel por verificar se estabeleceu a conexão ou não
        client.connect(broker)
        print('Conectado no servidor')
        client.loop_start()
        print('Se inscrevendo no tópico')
        while True:
            client.subscribe('nevoa/Hidrometros')
            client.on_message = self.retorno  # inserindo a função de retorno
            #client.on_log = self.retornoLog  # retorno do log das mensagens

nova = Conexao()
nova.inicia()
