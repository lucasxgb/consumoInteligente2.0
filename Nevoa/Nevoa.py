''' Se inscreve no tópico e manda para o servidor principal '''
import paho.mqtt.client as mqtt
import time
import json


listaMensagem = [] #mensagens que recebo entram na lista
class Conexao():
    def retrn(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        print("Mensagem recebida", mensagemDecode)
        print('Tópico da Mensagem', mensagem.topic)
    def retorno(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))

        listaMensagem.append(json.loads(mensagemDecode))

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
        c = True
        broker = 'broker.hivemq.com'
        client = mqtt.Client('nevoa')
        client.on_connect = self.verificaConexao #metodo do mqtt responsavel por verificar se estabeleceu a conexão ou não
        client.connect(broker)
        print('Conectado no servidor')
        client.loop_start()
        print('Se inscrevendo no tópico')
        while c ==True:
            client.subscribe('nevoa/Hidrometros')
            client.on_message = self.retorno  # inserindo a função de retorno
            #client.on_log = self.retornoLog  # retorno do log das mensagens
            c=False

    #para se conectar em um tópico de um hidrômetro expecifico
    def conectaHidroexpecifico(self, matriculaConecta):
        for matricula in listaMensagem:
            if matriculaConecta == str(matricula['Matricula']):
                broker = 'broker.hivemq.com'
                client = mqtt.Client('nev')
                client.on_connect = self.verificaConexao  # metodo do mqtt responsavel por verificar se estabeleceu a conexão ou não
                client.connect(broker)
                print('Conectado no servidor')
                client.loop_start()
                print('Se inscrevendo no tópico')
                while True:
                    client.subscribe(f'nevoa/Hidrometros/{matriculaConecta}')
                    client.on_message = self.retrn  # inserindo a função de retorno
                    # client.on_log = self.retornoLog  # retorno do log das mensagens

nova = Conexao()



def menu():
    print('''\nPor favor, selecione uma das opcções: 
       [1] - Alterar Vazão
       [2] - Ver Dados
       [0] - Encerrar Hidrômetro''')
    opt = int(input('\n'))
    return opt

def menuAux():
    nova.inicia()
    opt = menu()
    if opt == 1:
        mat = input('insira matricula:') #matricula vem do adm no caso

        nova.conectaHidroexpecifico(mat)

menuAux()