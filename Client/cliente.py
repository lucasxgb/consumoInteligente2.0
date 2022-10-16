'''Classe responsavél por controlar as ações do Cliente'''
import json
import socket, threading

######## código cores #########
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD   = "\033[;1m"
REVERSE = "\033[;7m"


HOST = 'localhost'
PORT = 8888
HostReq = f'{HOST}:{PORT}'
class Cliente:

    ''' Função responsável por enviar requisição ao servidor para pegar um Hidrômetro especifico '''
    def getHidrometroEspecifico(self, matricula):
        request = f'GET /cliente/buscaHidrometro/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para ver historico daquele Hidrômetro '''
    def getVerHistorico(self, matricula):
        request = f'GET /cliente/verHistorico/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para verificar o vazamento no hidrometro '''
    def getVerificaVazamento(self, matricula):
        request = f'GET /cliente/verificaVazamento/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para gerar a conta de um determinado hidrometro '''
    def getGerarConta(self, matricula):
        request = f'GET /cliente/gerarConta/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para gerar a conta de um determinado hidrometro '''
    def postPagarConta(self, matricula, codigo):
        request = f'POST /cliente/pagarConta/{matricula}/{codigo} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

'''Classe responsável pela conexão com o servidor semelhante a do hidrometro'''
class Conecta:
    def main(self, mensagem):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Iniciando o socket como ipv4 e protocolo tcp
        try:
            client.connect((HOST, PORT))  # tenta realizar a conexao com o servidor
        except:
            return print('Não foi possivel conectar ao servidor')

        print('Dados enviados')
        threadEnvia = threading.Thread(target=self.enviaMensagens, args=[client, mensagem])
        threadEnvia.start()
        return client

    # Função responsavel por receber alguma info do servidor
    def recebeMensagens(self, client):
        mensagemServidor = ''
        try:
            msg = client.recv(2048)
            mensagemServidor = msg.decode()

        except:
            print('Não foi possivel permanecer conectado')
            client.close()
        return mensagemServidor

    # Função responsavel por enviar mensagem
    def enviaMensagens(self, client, mensagem):
        try:
            msg = mensagem.encode()
            client.send(msg)
        except:
            return


def menuAux():
    print('=' * 10, '{Bem vindo}', '=' * 10)
    print('''
        Qual informação você deseja?
        [1] - VER HIDRÔMETRO ESPECÍFICO
        [2] - VER HISTORICO HIDRÔMETRO 
        [3] - GERAR CONTA
        [4] - PAGAR CONTA
        [5] - VERIFICAR VAZAMENTO
        [0] - FECHAR PROGRAMA
        ''')
    opt = int(input('Opção: '))
    return opt

def Menu():
    cliente = Cliente()
    nav = Conecta()
    opt = menuAux()
    while opt != 0:
        if opt == 1:
            print('=' * 5, 'Informe a matricula do hidrômetro a buscar', '=' * 5)
            mat = int(input('Matricula: '))
            request = cliente.getHidrometroEspecifico(mat)
            client = nav.main(request)
            resposta = nav.recebeMensagens(client)
            print(resposta)
            opt = menuAux()
        elif opt == 2:
            print('=' * 5, 'Informe a matricula do hidrômetro a ver o histórico', '=' * 5)
            mat = int(input('Matricula: '))
            request = cliente.getVerHistorico(mat)
            client = nav.main(request)
            resposta = nav.recebeMensagens(client)
            print(resposta)
            opt = menuAux()

        elif opt == 3:
            print('=' * 5, 'Informe a matricula do hidrômetro que deseja gerar conta', '=' * 5)
            mat = int(input('Matricula: '))
            request = cliente.getGerarConta(mat)
            client = nav.main(request)
            resposta = nav.recebeMensagens(client)
            print(resposta)
            print(f'{RED} Copie o código acima {RESET}')
            opt = menuAux()

        elif opt == 4:
            print('=' * 5, 'Informe a matricula do hidrômetro que deseja pagar a conta', '=' * 5)
            mat = int(input('Matricula: '))
            print('=' * 5, 'Informe o codigo da conta do hidrômetro que deseja pagar', '=' * 5)
            codigo = int(input('Código: '))
            request = cliente.postPagarConta(mat,codigo)
            client = nav.main(request)
            resposta = nav.recebeMensagens(client)
            print(resposta)
            opt = menuAux()

        elif opt == 5:
            print('=' * 5, 'Informe a matricula do hidrômetro que deseja verificar vazamento', '=' * 5)
            mat = int(input('Matricula: '))
            request = cliente.getVerificaVazamento(mat)
            client = nav.main(request)
            resposta = nav.recebeMensagens(client)
            print(resposta)
            opt = menuAux()

    print(f'{RED}PROGRAMA ENCERRADO{RESET}')

Menu()