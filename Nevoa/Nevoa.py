''' Se inscreve no tópico e manda para o servidor principal '''
import random, json
from time import sleep
import paho.mqtt.client as mqtt
import threading

listaMensagem = []  # mensagens que recebo entram na lista
class Conexao():
     # insere as mensagens que chegam na lista
    def retorno(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        if mensagem.topic == 'nevoa/Hidrometros': #se a mensagem chegar no tópico de hidrometros, ele guarda a informação no banco
            listaMensagem.append(json.loads(mensagemDecode))
        else:  #se não ele tem que verificar se a mensagem que chega é pra bloquear ou não
            print("Mensagem recebida", mensagemDecode)
            print('Tópico da Mensagem', mensagem.topic)

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

    # função retorna banco simplificado
    def bancoSimplificado(self, banco):
        listaComTodosHidrometro = []
        for objeto in banco:
            consumo = 0
            vazao = 0
            data = ''
            bloqueado = 0
            hidrometroMatricula = objeto['Matricula']
            for hidrometro in banco:  # pra todos os hidrometros no banco  ele vai adicionando o valor pra mostrar uma redução de todos que tem no banco e retornar o json disso
                if hidrometro['Matricula'] == hidrometroMatricula:
                    consumo += hidrometro['Consumo']
                    vazao = hidrometro['Vazao']
                    data = hidrometro['Data']
                    bloqueado = hidrometro['Bloqueado']
            HidroPreenchido = {"Matricula": hidrometroMatricula, "Consumo": round(consumo, 2), "Vazao": vazao,
                               "Data": data, 'Bloqueado': bloqueado}
            if HidroPreenchido not in listaComTodosHidrometro:
                listaComTodosHidrometro.append(HidroPreenchido)
        return listaComTodosHidrometro

    # Inserindo os dados no banco de dados
    def insereBanco(self):
        listaHidro = []
        with open("BancoNevoa/bancoNevoa.json") as banco:
            listaHidro = json.load(banco)
        if listaMensagem:
            for hidrometro in listaMensagem:
                listaHidro.append(dict(hidrometro))
                listaMensagem.remove(hidrometro)
        with open("BancoNevoa/bancoNevoa.json", 'w') as arquivoBanco:
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
            client.subscribe('nevoa/Hidrometros', 1)
            client.on_message = self.retorno# inserindo a função de retorno
            self.insereBanco()
            sleep(10)
            banco = self.abrirBanco("BancoNevoa/bancoNevoa.json")
            listaHidro = self.bancoSimplificado(banco)
            for hidrometro in listaHidro:
                client.subscribe(f"nevoa/Hidrometros/{hidrometro['Matricula']}", 2)



nova = Conexao()
threading.Thread(target=nova.inscrevendoTopico).start()
#while True:
#    nova.hidroExpecifico()

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
