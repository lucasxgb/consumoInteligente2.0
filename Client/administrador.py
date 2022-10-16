'''Classe responsavél por controlar as ações do administrador'''
import json
from time import sleep
import threading, socket

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
class Adm:

    ''' Função responsável por fazer o login do adm no sistema '''
    def getLogin(self, usuario, senha):
        request = f'GET /adm/login/{usuario}/{senha} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request


    ''' Função responsável por enviar requisição ao servidor para pegar todos os Hidrômetros '''
    def getTodosHidrometros(self):
        request = f'GET /adm/matriculas HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição ao servidor para pegar um Hidrômetro especifico '''
    def getHidrometroEspecifico(self, matricula):
        request = f'GET /adm/buscaHidrometro/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para ver historico daquele Hidrômetro '''
    def getVerHistorico(self, matricula):
        request = f'GET /adm/verHistorico/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar requisição para verificar o vazamento no hidrometro '''
    def getVerificaVazamento(self, matricula):
        request = f'GET /adm/verificaVazamento/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar para cortar o fornecimento utilizando o metódo post '''
    def postCortarFornecimento(self, matricula):
        request = f'POST /adm/cortarFornecimento/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

    ''' Função responsável por enviar para reativar o fornecimento utilizando o metódo post '''
    def postReativaFornecimento(self, matricula):
        request = f'POST /adm/reativaFornecimento/{matricula} HTTP/1.1\r\nHost: {HostReq}\r\n'
        return request

'''Classe responsável pela conexão com o servidor semelhante a do hidrometro'''
class Conecta:
    '''Função principal para realizara conexao'''
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

#função responsável por verificar o login do usuário
    def verificaLogin(self, mensagem):
        if 'True' in mensagem:
            return True
        else:
           return False


def menuAux():
    print('=' * 10, '{Bem vindo}', '=' * 10)
    print(''' 
        Qual informação você deseja?
        [1] - VER TODOS OS HIDRÔMETROS
        [2] - VER HIDRÔMETRO ESPECIFICO
        [3] - VER HISTÓRICO 
        [4] - VERIFICAR VAZAMENTO
        [5] - CORTAR FORNECIMENTO
        [0] - ENCERRAR PROGRAMA
        ''')
    opt = int(input('Opção:'))
    return opt






def Menu():
    adm = Adm()
    nav = Conecta()
    print('=' * 5, 'Informe o seu usuário', '=' * 5)
    usuario = str(input('User:'))
    print('=' * 5, 'Informe sua senha', '=' * 5)
    senha = int(input('Senha: '))
    mensagem = adm.getLogin(usuario, senha)
    client = nav.main(mensagem)
    if nav.verificaLogin(nav.recebeMensagens(client)) == True:
        opt = menuAux()
        while opt != 0:
            if opt == 1:
                request = adm.getTodosHidrometros()
                client = nav.main(request)
                resposta = nav.recebeMensagens(client)
                print(resposta)
                opt = menuAux()
            elif opt == 2:
                print('=' * 5, 'Informe a matricula do hidrômetro a buscar', '=' * 5)
                mat = int(input('Matricula: '))
                request = adm.getHidrometroEspecifico(mat)
                client = nav.main(request)
                resposta = nav.recebeMensagens(client)
                print(resposta)
                opt = menuAux()
            elif opt==3:
                print('=' * 5, 'Informe a matricula do hidrômetro que deseja ver o histórico', '=' * 5)
                mat = int(input('Matricula: '))
                request = adm.getVerHistorico(mat)
                client = nav.main(request)
                resposta = nav.recebeMensagens(client)
                print(resposta)
                opt = menuAux()
            elif opt==4:
                print('=' * 5, 'Informe a matricula do hidrômetro que deseja verificar vazamento', '=' * 5)
                mat = int(input('Matricula: '))
                request = adm.getVerificaVazamento(mat)
                client = nav.main(request)
                resposta = nav.recebeMensagens(client)
                print(resposta)
                opt = menuAux()
            elif opt == 5:
                print('=' * 5, 'Informe a matricula do hidrômetro que cortar o fornecimento', '=' * 5)
                mat = int(input('Matricula: '))
                request = adm.postCortarFornecimento(mat)
                client = nav.main(request)
                resposta = nav.recebeMensagens(client)
                print(resposta)
                opt = menuAux()
    else:
        print(f'{RED}USUÁRIO NÃO CADASTRADO NO SISTEMA{RESET}')
        print(f'{BOLD}PROGRAMA ENCERRADO{RESET}')

Menu()