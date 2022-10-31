''' Se inscreve no tópico e manda para o servidor principal '''
import random, json
from time import sleep
import paho.mqtt.client as mqtt
import threading

listaMensagem = []
class Conexao():
    def retorno(self, cliente, dadosUsuario, mensagem):
        """ Função para tratar as mensagens que chega ao tópico que está escrito

            Caso a mensagem venha no tópico geral de hidrômetros ela será convertida em dict e enviada para o banco.

            Caso seja uma mensagem especifica, ocorre o tratamento de dados

         """
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        if mensagem.topic == 'nevoa/Hidrometros': #se a mensagem chegar no tópico de hidrometros, ele guarda a informação no banco
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
        client = mqtt.Client('nevoa', random.randint(1, 1000))
        client.on_connect = self.verificaConexao  # metodo do mqtt responsavel por verificar se estabeleceu a conexão
        # ou não
        client.connect(broker)
        print('Conectado no servidor')
        return client

    def abrirBanco(self, arquivo):
        """ Função para abrir o banco de dados

            arquivo é o caminho onde o banco se encontra

        """
        BancoAberto = []
        with open(arquivo) as banco:
            BancoAberto = json.load(banco)
        return BancoAberto

    def bancoSimplificado(self, banco):
        """ Função que retorna o dado de um hidrômetro de maneira geral, com o consumo completo e etc... """
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

    def insereBanco(self):
        """ Função responsável por inserir os dados que chegam do hidrômetro no banco de dados """
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

    def inscrevendoTopico(self):
        """ Função responsável por inscrever a névoa no tópico do hidrômetro utilizando mqtt """
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


    def calculaMedia(self):
        """ Função para realizar o cálculo da média dos hidrometros conectados a esta névoa

            Precisa definir um tempo para recalcular a media sempre """
        abrirBanco = self.abrirBanco("BancoNevoa/bancoNevoa.json")
        banco = self.bancoSimplificado(abrirBanco)
        mediaAtual = 0
        somaConsumo = 0
        quantidadeConsumo = 0
        for hidrometro in banco:
            somaConsumo += float(hidrometro['Consumo'])
            quantidadeConsumo +=1
        mediaAtual = (somaConsumo/quantidadeConsumo)
        return mediaAtual

    def hidrometroEspecifico(self, matriculaBuscar):
        ''' Função responsável por retornar um hidrômetro especifico e mais atualizado '''
        listaHidrometro = []
        abrirBanco = self.abrirBanco("BancoNevoa/bancoNevoa.json")
        for hidrometro in abrirBanco:
            if matriculaBuscar == hidrometro['Matricula']:
                listaHidrometro.append(hidrometro)
        maisAtual = listaHidrometro.pop()
        return maisAtual

    def maiorConsumo(self):
        ''' Função responsável por retornar os 10 hidrômetros de maior consumo '''
        abrirBanco = self.abrirBanco("BancoNevoa/bancoNevoa.json")
        banco = self.bancoSimplificado(abrirBanco)
        listaOrdenada = []
        max = 0
        matricula = 0
        while banco:
            for hidrometro in banco:
                hidrometro['Consumo'] = hidrometro['Consumo']
                if hidrometro['Consumo'] > max:
                    max = hidrometro['Consumo']
                    matricula = hidrometro['Matricula']
            for hidro in banco:
                if hidro[matricula] == hidro:
                    listaOrdenada.append(hidro)
                    banco.remove(hidro)
        return listaOrdenada

nova = Conexao()
threading.Thread(target=nova.inscrevendoTopico).start()
while True:
    nova.maiorConsumo()

