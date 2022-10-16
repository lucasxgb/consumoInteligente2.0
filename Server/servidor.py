import threading, socket, json
import api

''' Chamada da classe da api rest'''
ApiRest = api.Api()

listaClient = []

''' Ligando o servidor'''
def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inicialização do servidor
    ''' Tenta ligar o servidor, se não conseguir envia o print de retorno'''
    try:
        servidor.bind(('localhost', 8888))
        servidor.listen() #ouvindo as conexões
    except:
        return print('\nNão foi possivel iniciar o servidor')

    while True:
        conexao, addr = servidor.accept() # aceita as conexões
        listaClient.append(conexao)
        threadTratamento = threading.Thread(target=tratamentoMensagens, args=[conexao]) #inicia a thread para tratar as mensagens
        threadTratamento.start()

'''Função que recebe as mensagens do cliente '''
def tratamentoMensagens(client):
    while True:
        try:
            mensagem = client.recv(2048) #recebe a mensagem do cliente
            requisicao = mensagem.decode() #decodifica a mensagem
            print(requisicao)
            print('\nChegou ao servidor')
            verificaElemento = requisicao.split('|') #Verificar se a informação que chega ao servidor é uma requisicao ou informação vinda de um hidrometro
            if verificaElemento[0][0].isdigit() == True:
                insereBanco(requisicao) #se o primeiro elemento for uma matricula, ele insere no banco de hidrometro
                resposta = returnSolicitaHidrometro(verificaElemento[0])
                resp = resposta
                transmite(resp, client) #envia a resposta ao cliente devido
            else: #se for uma requisição ele começa a tratar!
                controle = Controle()
                resposta = controle.respostasSolicita(mensagem)  # envia a solicitação para classe que executa as respostas
                transmite(resposta, client)
            if not mensagem:  # verificar se os dados chegaram
                print('Conexão Fechada')
                client.close()
        except:
            listaClient.remove(client)
            break

''' Função para retornar alguma informação para um cliente especifico '''
def transmite(mensagem, client):
    for objetoClient in listaClient:
        if objetoClient == client:
            try:
                objetoClient.send(mensagem)
            except:
                listaClient.remove(objetoClient) #se o objeto nao estiver na lista

''' Função para retornar dados do servidor para o hidrometro, para o hidrometro atualizar o envio de informações caso 
esteja bloqueado ou desbloqueado'''
def returnSolicitaHidrometro(matriculaBuscar):
    valores = []
    mat = int(matriculaBuscar)
    matricula = 0
    consumo = 0
    vazao = 0
    data = ''
    consumoAtual = 0
    bloqueado = 0
    for hidrometro in abrirBanco("Banco/bancoHidrometros.json"):
        if hidrometro['Matricula'] == mat:
            dic = {'Matricula': hidrometro['Matricula'], 'Consumo': hidrometro['Consumo'], 'Vazao': hidrometro['Vazao'],
                   'Data': hidrometro['Data'], 'Bloqueado': hidrometro['Bloqueado'],
                   'ConsumoAtual': hidrometro['ConsumoAtual']}
            valores.append(dic)
    for hidro in valores:
        matricula = int(hidro['Matricula'])
        consumo = float(hidro['Consumo'])
        vazao = int(hidro['Vazao'])
        data = hidro['Data']
        consumoAtual = float(hidro['Consumo'])
    hidroBloquea = valores[0]
    if int(hidroBloquea['Bloqueado']) == 1:
        bloqueado = int(hidroBloquea['Bloqueado'])
    else:
        bloqueado = 0
    informacoes = {'Matricula': matricula, 'Consumo': consumo, 'Vazao': vazao, 'Data': data, 'Bloqueado': bloqueado,
                   'ConsumoAtual': consumoAtual}
    dadosJson = json.dumps(informacoes, indent=6)
    return dadosJson.encode()

''' Função para abri o banco de dados para os hidrometros'''
def abrirBanco(arquivo):
    BancoAberto = []
    with open(arquivo) as banco:
        BancoAberto = json.load(banco)
    return BancoAberto

''' Função responsavel por inserir valores no banco'''
def insereBanco(mensagem):
    men = mensagem.split('|')
    user = men[0]
    menDic = dict(json.loads(men[1]))
    infoHidro = {'Matricula': menDic['Matricula'], 'Consumo': menDic['Consumo'], 'Vazao': menDic['Vazao'], 'Data': menDic['Data'], 'Bloqueado': menDic['Bloqueado'], 'ConsumoAtual': 0}
    listaHidro = []
    with open("Banco/bancoHidrometros.json") as banco:
        listaHidro = json.load(banco)
    listaHidro.append(infoHidro)
    with open("Banco/bancoHidrometros.json", 'w') as arquivoBanco:
        json.dump(listaHidro, arquivoBanco,
                  indent=5,
                  separators=(',',': ')
    )

'''Classe responsável pelo controle das requisições'''

class Controle:
    '''Método que inicia o cabeçalho e os codigos referentes a cada informação se ta ok ou se não achou'''
    def __init__(self):
        self.cabecalhos = {
        'Server': 'CrudeServer',
        'Content-Type': 'application/json'
        }
        self.codigo = { 200: 'OK',
        404: 'Not Found'
        }

    ''' Função responsavel por tratar a solicitação e responde-lá'''
    def respostasSolicita(self, resposta):
        request = AnalisaSolicita(resposta)
        handler = getattr(self, f'Http_{request.metodo}')
        response = handler(request)
        return response

    '''Função referente a linha de resposta, retorna o codigo se está OK ou se nao achou'''
    def respLinha(self, numero):
        cod = self.codigo[numero]
        linha = f'HTTP/1.1 {numero} {cod} \r\n'
        return linha.encode()

    '''Função referente ao cabeçalho da requisição de resposta'''
    def respCabe(self):
        cabeca = self.cabecalhos.copy()
        cab =''
        for h in cabeca:
            cab += f'{h}: {cabeca[h]}\r\n'
        return cab.encode()

    '''Função que trata a requisição a partir do metodo que vem dela
    Método GET, estão separados pelos ifs, buscando na api qual funcionalidade a determinada requisição irá receber'''
    def Http_GET(self, request):
        banc = 'Banco/bancoHidrometros.json'
        bancoAdm = abrirBanco('Banco/dadosAdm.json')
        banco = abrirBanco('Banco/bancoHidrometros.json')
        linhaemBranco = b'\r\n' #criar linha em branco
        requisicao = request.uri.strip('/') #dividir a url nas barras
        req = requisicao.split('/') # metodo auxiliar para pegar as demais informações

        #Resposta a solicitação de todas as matriculas do adm
        if requisicao == 'adm/matriculas':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getAdmTodosHidrometros(banco)
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        #Resposta a solicitação de login do adm
        elif len(req)> 3 and requisicao == f'adm/login/{req[2]}/{req[3]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getLoginAdm(bancoAdm, req[2], req[3])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        #Resposta a solicitação de verificação de vazamento, tanto do cliente como do servidor
        elif len(req) > 2 and requisicao == f'adm/verificaVazamento/{req[2]}' or requisicao == f'cliente/verificaVazamento/{req[2]}' :
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getVerificaVazamentos(banco, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        #resposta da requisição de buscar hidrometros
        elif len(req) > 2 and requisicao == f'adm/buscaHidrometro/{req[2]}' or requisicao == f'cliente/buscaHidrometro/{req[2]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getHidrometroEspecifico(banco, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        # resposta da requisição para ver historicos do hidrometro
        elif len(req)>2 and requisicao == f'adm/verHistorico/{req[2]}' or requisicao == f'cliente/verHistorico/{req[2]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getVerificaComportamento(banco, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        # resposta da requisição de gerar contas
        elif len(req)>2 and requisicao == f'cliente/gerarConta/{req[2]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.getGerarFatura(banc, banco, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        # resposta caso não encontre a rota especifica
        else:
            linhaResposta = self.respLinha(404)
            cabecalhos = self.respCabe()
            corpoResposta = b"<h1>404 Not Found</h1>"
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

    '''Função que trata a requisição a partir do metodo que vem dela
        Método POST'''
    def Http_POST(self, request):
        banc = 'Banco/bancoHidrometros.json'
        bancoAdm = abrirBanco('Banco/dadosAdm.json')
        banco = abrirBanco('Banco/bancoHidrometros.json')
        linhaemBranco = b'\r\n'
        requisicao = request.uri.strip('/')
        req = requisicao.split('/')
        if len(req)>2 and requisicao == f'adm/cortarFornecimento/{req[2]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.postBloquearHidrometro(banc, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        elif len(req)>2 and requisicao == f'adm/reativaFornecimento/{req[2]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.postDesbloquearHidrometro(banc, req[2])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])

        elif len(req) > 3 and requisicao == f'cliente/pagarConta/{req[2]}/{req[3]}':
            linhaResposta = self.respLinha(200)
            cabecalhos = self.respCabe()
            resp = ApiRest.postPagarConta(banc, req[2], req[3])
            corpoResposta = resp.encode()
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])
        else:
            linhaResposta = self.respLinha(404)
            cabecalhos = self.respCabe()
            corpoResposta = b"<h1>404 Not Found</h1>"
            return b''.join([linhaResposta, cabecalhos, linhaemBranco, corpoResposta])


'''Classe responsavel por Analisar solicitações, dividindo em pedaços e analisando os mesmo separadamente'''
class AnalisaSolicita:
    def __init__(self, solicitacoes):
        self.metodo = None
        self.uri = None
        self.versaoHttp = '1.1'

        self.analisar(solicitacoes)

    def analisar (self, solicita):
        linhas = solicita.split(b'\r\n') #dividir as linhas
        linhaRequest = linhas[0] #pega a primeira linha da lista que foi gerada após a divisão
        words = linhaRequest.split(b' ')

        self.metodo = words[0].decode()

        if len(words) > 1:
            self.uri = words[1].decode()

        if len(words) > 2:
            self.versaoHttp = words[2]


main()
