''' Se inscreve no tópico e manda para o servidor principal '''
import random, time, json
import paho.mqtt.client as mqtt
import threading

listaMensagem = []  # mensagens que recebo entram na lista
class Conexao():
    # exibe as mensagens que chegam
    def retrn(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        print("Mensagem recebida", mensagemDecode)
        print('Tópico da Mensagem', mensagem.topic)

    # insere as mensagens que chegam na lista
    def retorno(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        listaMensagem.append(json.loads(mensagemDecode))

    # Log - Registro do cliente
    def retornoLog(self, cliente, dadosUsuario, nivel, buf):
        print('Log: ', buf)

    # Verifica conexão
    def verificaConexao(self, cliente, dadosUsuario, flags, rc):
        if rc == 0:
            print('Conectado, código de retorno= ', rc)
        else:
            print('Não foi possível se conectar, código= ', rc)

    # metodo para publicar no tópico
    # def publica(self, urlTopico, dadosEnviar):
    #   return urlTopico, dadosEnviar

    def inicia(self):
        broker = 'broker.hivemq.com'
        client = mqtt.Client('nevoa', random.randint(1, 1000))
        client.on_connect = self.verificaConexao  # metodo do mqtt responsavel por verificar se estabeleceu a conexão
        # ou não
        client.connect(broker)
        print('Conectado no servidor')
        return client

    # Abre o banco
    def abrirBanco(self, arquivo):
        BancoAberto = []
        with open(arquivo) as banco:
            BancoAberto = json.load(banco)
        return BancoAberto

    # Inserindo os dados no banco de dados
    def insereBanco(self):
        listaHidro = []
        with open("Nevoa/BancoNevoa/bancoNevoa.json") as banco:
            listaHidro = json.load(banco)
        if listaMensagem:
            for hidrometro in listaMensagem:
                listaHidro.append(dict(hidrometro))
                listaMensagem.remove(hidrometro)
        with open("Nevoa/BancoNevoa/bancoNevoa.json", 'w') as arquivoBanco:
            json.dump(listaHidro, arquivoBanco,
                      indent=5,
                      separators=(',', ': ')
                      )

    # se inscrevendo nos tópicos
    def inscrevendoTopico(self):
        client = self.inicia()
        client.loop_start()  # para ver o retorno das chamadas
        print('Se inscrevendo no tópico')
        c = True
        while c == True:
            client.subscribe('nevoa/Hidrometros')
            client.on_message = self.retorno  # inserindo a função de retorno
            self.insereBanco()

    # Função para pegar os hidrometros no banco e conectar o cliente ao topico de cada hidrometro
    def hidroExpecifico(self):
        client = self.inicia()
        #client.loop_start()  # para observar o retorno das chamadas
        print('Se inscrevendo no tópico')
        banco = self.abrirBanco("Nevoa/BancoNevoa/bancoNevoa.json")
        while True:
            for hidrometro in banco:
                client.subscribe(f"nevoa/Hidrometros/{hidrometro['Matricula']}")
                client.on_message = self.retrn  # inserindo a função de retorno

            # client.on_log = self.retornoLog  # retorno do log das mensagens


nova = Conexao()
threading.Thread(target=nova.inscrevendoTopico).start()
while True:
    nova.hidroExpecifico()

# def menu():
#     print('''\nPor favor, selecione uma das opcções:
#        [1] - Alterar Vazão
#        [2] - Ver Dados
#        [0] - Encerrar Hidrômetro''')
#     opt = int(input('\n'))
#     return opt
#
# def menuAux():
#     nova.inicia()
#     opt = menu()
#     if opt == 1:
#         mat = input('insira matricula:') #matricula vem do adm no caso
#
#         nova.conectaHidroexpecifico(mat)

# menuAux()
