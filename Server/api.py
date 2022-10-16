'''Classe responsavel por tratar os dados '''
import json, random

class Api:

#Função responsável por fazer o login do adm no sistema
    def getLoginAdm(self, bancoAdm, user, senha):
        Admins = []
        Verifica = ''
        for adm in bancoAdm:
            Admins.append(adm)
        if Admins[0]['Usuario'] == user and int(Admins[0]['Senha']) == int(senha): #verifica se as informações estão corretas
            Verifica = 'True'
        else:
            Verifica = 'False'
        return json.dumps(Verifica)

#Função responsável por retornar todos os hidrometros para o adm com os dados processados
    def getAdmTodosHidrometros(self, banco):
        listaComTodosHidrometro = []
        for objeto in banco:
            consumo = 0
            vazao = 0
            data = ''
            bloqueado = 0
            consumoAtual = 0
            hidrometroMatricula = objeto['Matricula']
            for hidrometro in banco: #pra todos os hidrometros no banco  ele vai adicionando o valor pra mostrar uma redução de todos que tem no banco e retornar o json disso
                if hidrometro['Matricula'] == hidrometroMatricula:
                    consumo += hidrometro['Consumo']
                    vazao = hidrometro['Vazao']
                    data = hidrometro['Data']
                    consumoAtual = hidrometro['ConsumoAtual']
                    bloqueado = hidrometro['Bloqueado']
            HidroPreenchido = {"Matricula": hidrometroMatricula, "Consumo": round(consumo,2), "Vazao":vazao, "Data": data, 'Bloqueado': bloqueado,'ConsumoAtual': consumoAtual}
            if HidroPreenchido not in listaComTodosHidrometro:
                listaComTodosHidrometro.append(HidroPreenchido)
        return json.dumps(listaComTodosHidrometro, indent=6)

#Função responsável por retornar um hidrometro especifico com os dados processados
    def getHidrometroEspecifico(self, banco, matriculaBuscar):
        valores = []
        mat = int(matriculaBuscar)
        matricula = 0
        consumo = 0
        vazao = 0
        data = ''
        consumoAtual =0
        bloqueado = 0
        for hidrometro in banco:  # a mesma logica do anterior ele pega cada um hidrometro no banco, e adiciona em uma lista
            dic = {'Matricula': hidrometro['Matricula'], 'Consumo': hidrometro['Consumo'], 'Vazao': hidrometro['Vazao'], 'Data': hidrometro['Data'], 'Bloqueado': hidrometro['Bloqueado'], 'ConsumoAtual': hidrometro['ConsumoAtual']}
            valores.append(dic)
        for hidro in valores: #pra cada hidrometro ele vai pegar o que o usuário deseja buscar e passar esse valor como parametro pro retorno
            if hidro['Matricula'] == mat:
                matricula = int(hidro['Matricula'])
                consumo = float(hidro['Consumo'])
                vazao = int(hidro['Vazao'])
                data = hidro['Data']
                bloqueado = int(hidro['Bloqueado'])
                consumoAtual = consumo
        informacoes = {'Matricula': matricula, 'Consumo': consumo, 'Vazao': vazao, 'Data': data, 'Bloqueado': bloqueado, 'ConsumoAtual':consumoAtual }
        dadosJson = json.dumps(informacoes, indent=6)
        return dadosJson

#Função responsável por retornar os dados de um hidrometro especifico
    def getVerificaComportamento(self, banco, matriculaBuscar):
        mat = int(matriculaBuscar)
        valores = []
        for hidrometro in banco:
            if hidrometro['Matricula'] == mat:
                valores.append(hidrometro)
        dadosJson = json.dumps(valores, indent=5)
        return dadosJson

#Função responsável por gerar a fatura do hidrometro
# metódo consiste em fazer uma verificação no banco, gerando uma media de consumo para calcular a conta de cada usuário
    def getGerarFatura(self, arquivo, banco, matriculaBuscar):
        dados = json.loads(self.getHidrometroEspecifico(banco,matriculaBuscar))
        mediaConsumo = 0
        cont = 0
        consumoAtual = 0
        with open(arquivo) as banco:
            listaHidro = json.load(banco)
        for hidrometro in listaHidro:
            if hidrometro['Matricula'] == dados['Matricula']:
                mediaConsumo += float(hidrometro['Consumo'])
                cont+=1
        consumoAtual = (mediaConsumo / cont)
        valoraPagar = consumoAtual * 20
        for hidrometro in listaHidro:
            if hidrometro['Matricula'] == dados['Matricula']:
                hidrometro['consumoAtual'] = consumoAtual
        with open(arquivo, 'w') as arquivoBanco:
            json.dump(listaHidro, arquivoBanco,
                      indent=5,
                      separators=(',', ': ')
            )


        # dadosConsumo = dados['Consumo']
        # dadosConsumoAtual = dados['ConsumoAtual']
        # dadosNovoConsumo = dadosConsumoAtual
        # if dadosNovoConsumo == 0:
        #     dadosNovoConsumo = dadosConsumo
        # else:
        #     if dadosConsumo != dadosConsumoAtual:
        #         dadosNovoConsumo = dadosConsumo - dadosConsumoAtual
        #     else:
        #         dadosNovoConsumo = dadosConsumo
        # valoraPagar = dadosNovoConsumo * 20

        codigo = random.randint(0, 1231231215594142)
        informacoes = {'Matricula': dados['Matricula'], 'Consumo': dados['Consumo'], 'ConsumoConta': round(consumoAtual,2),
                       'Valor a Pagar': round(valoraPagar,2), 'Codigo': codigo}
        return json.dumps(informacoes, indent=5)



#Função responsável por verificar se há vazamentos
    def getVerificaVazamentos(self,  banco ,matriculaBuscar):
        vazamento = json.loads(self.getVerificaComportamento(banco, matriculaBuscar))
        list = []
        cont = 0
        for hidro in vazamento:
            if int(matriculaBuscar) == int(hidro['Matricula']):
                list.append(hidro)
        for valores in list:
            hidrometro = list.pop()
            if int(hidrometro['Bloqueado']) == 0 and int(hidrometro['Vazao']) == 0:
                cont += 1
        if cont > 1:
            Mensagem = 'Existe supeita de vazamento na rede'
        else:
            Mensagem = 'Rede em funcionamento normal'
        return json.dumps(Mensagem)

#Função responsável por bloquear o hidrometro
    def postBloquearHidrometro(self, arquivo, matriculaBloquear):
        matriculaBloq = int(matriculaBloquear)
        with open(arquivo) as banco:
            listaHidro = json.load(banco)
        for hidrometro in listaHidro:
            if hidrometro['Matricula'] == matriculaBloq:
                hidrometro['Bloqueado'] = 1
        with open(arquivo, 'w') as arquivoBanco:
            json.dump(listaHidro, arquivoBanco,
                      indent=5,
                      separators=(',', ': ')
                      )
        return json.dumps('Sucesso')

#Função responsável por desbloquear o hidrometro
    def postDesbloquearHidrometro(self, arquivo , matriculaBloquear):
        matriculaBloq = int(matriculaBloquear)
        with open(arquivo) as banco:
            listaHidro = json.load(banco)
        for hidrometro in listaHidro:
            if hidrometro['Matricula'] == matriculaBloq:
                hidrometro['Bloqueado'] = 0
        with open(arquivo, 'w') as arquivoBanco:
            json.dump(listaHidro, arquivoBanco,
                      indent=5,
                      separators=(',', ': ')
                      )
        return json.dumps('Sucesso')

    #Função responsável por pagar conta
    def postPagarConta(self,arquivo, matricula, codigo):
        if int(codigo) != '':
           return self.postDesbloquearHidrometro(arquivo, matricula)
        else:
            return json.dumps('Falhou')