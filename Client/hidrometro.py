'''Import das bibliotecas utilizadas no pacote'''
import threading, socket, json, random, socket
from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import time

######## código cores #########
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD   = "\033[;1m"
REVERSE = "\033[;7m"


bloquear = 0
###################### Funções auxiliares para o hidrometro ######################
''' Função responsável por gerar o valor da matricula automaticamente'''
def valorMat():
    valor1 = random.randint(1, 10)
    valor = random.sample(range(501123), 2)
    mat = (valor1 * valor[0]) % valor[1]
    if len(str(mat)) != 5:
        while len(str(mat)) !=5:
            valor1 = random.randint(1, 10)
            valor = random.sample(range(712351), 2)
            mat = (valor1 * valor[0]) % valor[1]
    return int(mat)

''' Função responsável por  erar valor inicial para vazao entre 0 e 10'''
def gerarVazaoInicial():
    vaz = random.randint(0,9)
    valorVaz = vaz
    return valorVaz


''' Classe e metódos do hidrometro '''
class Hidrometro:
    def __init__(self, mat):
        self.matricula = mat
        self.consumo = 0
        self.vazao = None
        self.dataeHora = None
        self.bloqueado = 0
        self.pararThreads = threading.Event()

    '''Método para parar threads'''
    def stop(self, controle):
        if controle:
            self.pararThreads.set()
        else:
            self.pararThreads.clear()

    ''' Método para alterar o valor da matricula'''
    def setMatricula (self, alteraMat):
        self.matricula = alteraMat

    ''' Método para alterar o valor do consumo'''
    def setConsumo (self, alterarConsum):
        vaz = (alterarConsum/1000)*10
        valorVaz = round(vaz, 2)
        self.consumo += valorVaz

    ''' Método para alterar o valor da vazao'''
    def setVazao(self, alteraVazao):
        self.vazao = alteraVazao
        threading.Thread(target=self.hidrometroAuto).start()

    ''' Método para alterar o valor da matricula'''
    def setBloqueio(self, alteraBloqueio):
        self.bloqueado = alteraBloqueio

    ''' Método para retornar a vazao'''
    def getVazao(self):
        return self.vazao

    ''' Método para retornar a matricula'''
    def getMatricula (self):
       return self.matricula

    ''' Método para retornar o valor do consumo'''
    def getConsumo (self):
       return self.consumo

    ''' Método responsável por gerar data do hidrometro'''
    def getDataHora(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M')

    ''' Método responsável por retornar se o hidrometro está bloqueado ou não'''
    def getBloqueio(self):
        return self.bloqueado

    ''' Método para encaminhar json dos dados'''
    def getDados(self):
        informacoes = {'Matricula': self.matricula, 'Consumo':  round(self.consumo,2), 'Vazao': self.vazao, 'Data': self.getDataHora(), 'Bloqueado': self.getBloqueio()}
        dadosJson = json.dumps(informacoes, indent=5)
        return dadosJson

    '''Método responsável por calcular o consumo do hidrometro automaticamente'''
    def hidrometroAuto(self):
        if self.getVazao() != 0:
            while self.getVazao() != 0:
                sleep(5)
                self.setConsumo(self.getVazao())
        else:
            self.consumo = self.getConsumo()

    '''Função para verificar alteração para ver se está cortado ou não'''
    def verificaAltera(self, dados):
        carregar = json.loads(dados)
        carga = int(carregar['Bloqueado'])
        if carga == 1:
            self.setBloqueio(1)
            self.setVazao(0)
        elif carga == 0:
            self.setBloqueio(0)
            self.setVazao(self.getVazao())


    '''Função principal, inicia a conexão socket e chama as demais threads'''
    def main(self, username):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Iniciando o socket como ipv4 e protocolo tcp
        try:
            client.connect(('127.0.0.1', 8888))  # tenta realizar a conexao com o servidor
        except:
            return print('Não foi possivel conectar ao servidor')

        print('Conectado')
        threadRecebe = threading.Thread(target=self.recebeMensagens, args=[client])
        threadEnvia = threading.Thread(target=self.enviaMensagens, args=[client, username])
        threadRecebe.start()
        threadEnvia.start()

    ''' Função responsavel por receber alguma info do servidor '''
    def recebeMensagens(self, client):
        while True:
            try:
                msg = client.recv(2048)
                mensagemServidor = msg.decode()
                self.verificaAltera(mensagemServidor)
            except:
                print('Não foi possivel permanecer conectado')
                client.close()
                break

    ''' Função responsavel por enviar dados para o servidor'''
    def enviaMensagens(self, client, username):
        while self.pararThreads:
            sleep(10)
            dadosHidrometro = self.getDados()
            try:
                client.send(f'{username} | {dadosHidrometro}'.encode())
            except:
                return



    ''' Função responsavel por inicializar o mqtt '''
    import paho.mqtt.client as mqtt  # importação cliente mqtt
    import time
    ########### instanciando um cliente ###############
    # cliente = mqtt.Client('Id_cliente')

    ############ Se conectando a um broker ############
    # cliente.connect('Broker')

    ############ publicando em um tópico ##############
    # cliente.publish('topico/publicar', 'o que vai publicar')

    ############ Função de retorno para processar as mensagens ##############
    def retorno(self, cliente, dadosUsuario, mensagem):
        mensagemDecode = str(mensagem.payload.decode('utf-8'))
        print("Mensagem recebida", mensagemDecode)
        print('Tópico da Mensagem', mensagem.topic)

    ########### Log - Registro do cliente #################
    def retornoLog(self, cliente, dadosUsuario, nivel, buf):
        print('Log: ', buf)

    ######## Verifica conexão ################
    def verifcaConexao(self, cliente, dadosUsuario, flags, rc):
        if rc == 0:
            print('Conectado, código de retorno= ', rc)
        else:
            print('Não foi possível se conectar, código= ', rc)

    ###### metodo para publicar no tópico #######
    #def publica(self, urlTopico, dadosEnviar):
    #   return urlTopico, dadosEnviar
    def inicia(self, matriculaHidrometro, dados):
        broker = 'broker.hivemq.com'
        client = mqtt.Client(matriculaHidrometro)
        client.connect(broker)
        print('Conectado no servidor')
        client.loop_start()
        print('Se inscrevendo no tópico')
        client.subscribe('enviarDados/Hidrometros', qos=0)
        print('Publicando no tópico')
        client.publish('enviarDados/Hidrometros', dados)
        client.on_message = self.retorno  # inserindo a função de retorno
        client.on_log = self.retornoLog  # retorno do log das mensagens
        time.sleep(4)
        client.loop_stop()




################# Métodos de exibição ###################
    def exibeMenu(self):
        print('''\nPor favor, selecione uma das opcções: 
        [1] - Alterar Vazão
        [2] - Ver Dados
        [0] - Encerrar Hidrômetro''')
        opt = int(input('\n'))
        return opt

    def exibeHidrometro(self, infoHidro):
        infoHidrometro = json.loads(infoHidro)
        matricula = infoHidrometro['Matricula']
        consumo = infoHidrometro['Consumo']
        vazao = infoHidrometro['Vazao']
        print(f'{"Hidrômetro":^30}')
        print("=" * 10,{matricula}, "=" * 10)
        print(f'{"Consumo: ":^31}')
        print(f'{CYAN}{consumo:^30}{RESET}')
        print(f'{"Vazão: ":>30}')
        print(f'{RED}{vazao:>27}{RESET}')
        print("=" * 9,"{Embrasa}", "=" * 9)

def Menu():
    Matricula = valorMat()
    Vazao = gerarVazaoInicial()
    Hidro = Hidrometro(Matricula)
    Hidro.setVazao(Vazao)
    # Hidro.main(Hidro.getMatricula())
    # Hidro.exibeHidrometro(Hidro.getDados())
    # opt = Hidro.exibeMenu()
    Hidro.inicia(str(Hidro.getMatricula()), Hidro.getDados())


Menu()