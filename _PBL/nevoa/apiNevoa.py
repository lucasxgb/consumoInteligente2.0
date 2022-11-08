# -*- coding: utf-8 -*-

import json

class Api:
    
    # Metodos de Login

    def POST_LoginHidrometro(self, matricula):
        """Rota post que verifica se o hidrometro já existe na base de dados

            Args:
                matricula (str): matricula do hidrometro
            
            Returns:
                Json: Json contendo informações do Hidrometro, se já existia, se está bloqueado, consumo atual, etc...
        """
        
        # Ler dados do banco
        with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
            hidrometros = json.load(database)
        
        # Verificar se a matricula existe
        if matricula.lower() in hidrometros:
            consumoAtual = hidrometros[matricula.lower()]["consumoAtual"]
            bloq = hidrometros[matricula.lower()]["bloqueado"]
            
            retorno = '{"login" : "sucesso", "consumoAtual" : "-", "bloqueado" : "_"}'.replace("-", str(consumoAtual)).replace("_", str(bloq))
            return retorno # Retornar validação existente e quanto o hidrometro consumiu até o momento
        
        else:
            # Adicionar novo hidrometro
            
            hidrometros[matricula.lower()] = {
                "bloqueado": "0",
                "consumoAtual" : "0",
                "consumoAnterior01" : "0",
                "consumoAnterior02" : "0",
                "consumoAnterior03" : "0",
                "consumoAnterior04" : "0",
                "contaPagar" : "0",
                "vazamento": "0"
            }
            
            #Salvar alterações no banco
            with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
                json.dump(hidrometros, database, indent=4)   

            # Retornar 
            retorno = '"login" : "sucesso","consumoAtual" : "0", "bloqueado" : "0"}'  # Consumo atual é 0, pois não foi criado agora
            return json.dumps(retorno) # Retornar validação existente e quanto o hidrometro consumiu até o momento
    

    def POST_LoginCliente(self, matricula):
        """ rota POST que verifica se o cliente já existe na base de dados

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: Json contendo informações se o usuario existe ou não
        """

        reultado = self.POST_LoginHidrometro(matricula)

        return json.dumps('{"login": "sucesso"}')


    # Metodos ADM


    def PUT_bloquear_hidrometro(self, matricula):
        """ Rota PUT que bloqueia um hidrometro

            Args:
                matricula (str): matricula associada ao hidrometro
            
            Returns:
                Json: Json contendo informações de bloqueio do hidrometro
        """
        try:
            # Pegar dados do banco
            with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # Verificar se o hidrometro existe
            if matricula in hidrometros:
                # bloquar hidrometro
                # Mudar bloqueio para 1
                hidrometros[matricula.lower()]["bloqueado"] = "1" 

                #Salvar alterações no banco
                with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
                return json.dumps('{"resultado" : "bloqueado" }')
            else:
                return json.dumps('{ "resultado" : "inexistente" }')
        except:
            return json.dumps('{ "resultado" : "bloqueado" }')


    def PUT_DesbloquearHidrometro(self, matricula):
        """ Rota PUT que desbloqueia um hidrometro

            Args:
                matricula (str): matricula associada ao hidrometro
            
            Returns:
                Json: Json contendo informações de bloqueio do hidrometro
        """
        # Mandar um dado para tirar block para o hidrometro do cliente, tratar no servidor para mandar apenas para o cliente especifico
        try:
            # Pegar dados do banco
            with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # Verificar se o hidrometro existe
            if matricula in hidrometros:
                # desbloquar hidrometro
                # Mudar bloqueio para 0
                hidrometros[matricula.lower()]["bloqueado"] = "0" 

                #Salvar alterações no banco
                with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
                return json.dumps('{"resultado" : "bloqueado" }')
            else:
                return json.dumps('{ "resultado" : "inexistente" }')
        except:
            return json.dumps('{ "resultado" : "bloqueado" }')
    

    # Metodos Cliente


    def GET_pegarInformacoesHidro(self, matricula):
        """ Rota GET para pegar informações do hidrometro

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: 
        """
        #Abrir database
        with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
            hidrometros = json.load(database)
        
        return json.dumps(hidrometros)


    def GET_GerarBoleto(self, matricula):
        """ Rota GET gera o boleto do cliente

            Args:
                matricula (str): matricula do Cliente
            
            Returns:
                Json: Json contendo informações do cliente
        """
        
        # Fazez consulta no banco, e gerar conta para o cliente
        with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)
        
        # Verificar se o Cliente já tem divida, se sim, retornar a divida dele atual.
        if int(clientes[matricula]["contaPagar"]) > 0:
            retorno = "{-}"
            return retorno.replace("-",f'"conta" : "{clientes[matricula]["contaPagar"]}"')
        
        else:
            # Pegar dados do banco
            with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # atualizar o consumo atual e gerar conta
            consAtu = str(hidrometros[matricula.lower()]["consumoAtual"])
            consAnt01 = str(hidrometros[matricula.lower()]["consumoAnterior01"])
            
            metrosCubicosGastos =  int(consAtu) - int(consAnt01)
            valorPagar = metrosCubicosGastos * 1.3      # preço de Cada Metro cubico
            
            hidrometros[matricula.lower()]["contaPagar"] = valorPagar
            
            hidrometros[matricula.lower()]["consumoAnterior04"] = hidrometros[matricula.lower()]["consumoAnterior03"]
            hidrometros[matricula.lower()]["consumoAnterior03"] = hidrometros[matricula.lower()]["consumoAnterior02"]
            hidrometros[matricula.lower()]["consumoAnterior02"] = hidrometros[matricula.lower()]["consumoAnterior01"]
            hidrometros[matricula.lower()]["consumoAnterior01"] = hidrometros[matricula.lower()]["consumoAtual"]

            #Salvar alterações do hidrometro no banco
            with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
            
            retorno = "{-}"
            return retorno.replace("-",f'"conta" : "{valorPagar}"')

    
    def PUT_Pagarconta(self, matricula):
        """ Rota PUT para pagar conta

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: Json contendo a informação que a conta foi paga
        """
        # Desbloquear Hidrometro automaticamente
        self.PUT_DesbloquearHidrometro(matricula)
        
        #Abrir database
        with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)

        # zerar a divida
        clientes[matricula.lower()]["contaPagar"] = "0"
        
        #Salvar alterações no banco
        with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
            json.dump(clientes, database, indent=4)  
        
        return '{"conta": "paga"}'

    # Metodos Hidro

    def PUT_novoConsumo(self, matricula, novoConsumo, vazamento):
        """ Rota PUT para atualizar consumo

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: 
        """
        #Abrir database
        with open("banco/bancoNevoa.json", 'r' , encoding='utf-8') as database:
            hidrometros = json.load(database)

        # Atualizar consumo
        hidrometros[matricula.lower()]["consumoAtual"] = str(novoConsumo)
        hidrometros[matricula.lower()]["vazamento"] = str(vazamento)
        
        #Salvar alterações no banco
        with open("banco/bancoNevoa.json", 'w' , encoding='utf-8') as database:
            json.dump(hidrometros, database, indent=4)  
        
        return json.dumps('{"consumo": "atualizado"}')
