# -*- coding: utf-8 -*-

import json

class Api:
    
    # Metodos de Login

    def POST_Login_hidrometro(self, matricula):
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
            
            retorno = '{"consumoAtual" : "-", "bloqueado" : "_"}'.replace("-", str(consumoAtual)).replace("_", str(bloq))
            return json.dumps(retorno) # Retornar validação existente e quanto o hidrometro consumiu até o momento
        
        else:
            # Adicionar novo hidrometro
            hidrometros[matricula.lower()] = {"ultimoConsumo" : "0", "consumoAtual" : "0", "bloqueado" : "0", "vazando" : "0"}
            
            #Salvar alterações no banco
            with open("banco/hidrometros.json", 'w' , encoding='utf-8') as database:
                json.dump(hidrometros, database, indent=4)   
            
            # adicionar Cliente
            self.POST_NovoCliente(matricula)

            # Retornar 
            retorno = '{"Hidrometro" : "Foi Criado", "consumoAtual" : "0", "bloqueado" : "0"}'  # Consumo atual é 0, pois não foi criado agora
            return json.dumps(retorno) # Retornar validação existente e quanto o hidrometro consumiu até o momento
    

    def POST_LoginCliente(self, matricula):
        """ rota POST que verifica se o cliente já existe na base de dados

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: Json contendo informações se o usuario existe ou não
        """

        # Ler dados do banco
        with open("banco/clientes.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)
        
        # Verificar se a matricula existe
        if matricula.lower() in clientes:
            return json.dumps('{ "validar" : "True"}') # Retornar validação existente e quanto o hidrometro consumiu até o momento
        
        else:
            return json.dumps('{ "validar" : "False"}') # Retornar validação existente e quanto o hidrometro consumiu até o momento


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
            with open("banco/hidrometros.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # Verificar se o hidrometro existe
            if matricula in hidrometros:
                # bloquar hidrometro
                uc = str(hidrometros[matricula.lower()]["ultimoConsumo"])
                ca = str(hidrometros[matricula.lower()]["consumoAtual"])
                va = str(hidrometros[matricula.lower()]["vazando"])
                
                # Mudar bloqueio para 1
                hidrometros[matricula.lower()] = {"ultimoConsumo" : uc, "consumoAtual" : ca, "bloqueado" : "1", "vazando" : va}
            
                #Salvar alterações no banco
                with open("banco/hidrometros.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
                return json.dumps('{ "validar" : "True" , "bloqueado" : "1" }')
            else:
                return json.dumps('{ "validar" : "False" }')
        except:
            return json.dumps('{ "validar" : "False" }')


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
            with open("banco/hidrometros.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # Verificar se o hidrometro existe
            if matricula in hidrometros:
                # bloquar hidrometro
                uc = str(hidrometros[matricula.lower()]["ultimoConsumo"])
                ca = str(hidrometros[matricula.lower()]["consumoAtual"])
                va = str(hidrometros[matricula.lower()]["vazando"])
                
                # Mudar bloqueio para 2
                hidrometros[matricula.lower()] = {"ultimoConsumo" : uc, "consumoAtual" : ca, "bloqueado" : "0", "vazando" : va}
            
                #Salvar alterações no banco
                with open("banco/hidrometros.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
                return json.dumps('{ "validar" : "True" , "bloqueado" : "0" }')
            else:
                return json.dumps('{ "validar" : "False" }')
        except:
            return json.dumps('{ "validar" : "False" }')
    


    # Metodos Cliente

    def POST_NovoCliente(self, matricula):
        """ Rota POST que insere um novo cliente no banco

            Args:
                matricula (str): matricula do cliente
 
        """
        
        # Criar novo cliente ao ser criado um hidrometro
        
        # Ler dados do banco
        with open("banco/clientes.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)
        
        # Adicionar novo cliente
        clientes[matricula.lower()] = {"divida" : "0"}
        
        #Salvar alterações no banco
        with open("banco/clientes.json", 'w' , encoding='utf-8') as database:
            json.dump(clientes, database, indent=4)   


    def GET_GerarBoleto(self, matricula):
        """ Rota GET gera o boleto do cliente

            Args:
                matricula (str): matricula do Cliente
            
            Returns:
                Json: Json contendo informações do cliente
        """
        
        # Fazez consulta no banco, e gerar conta para o cliente
        with open("banco/clientes.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)
        
        # Verificar se o Cliente já tem divida, se sim, retornar a divida dele atual.
        if int(clientes[matricula]["divida"]) > 0:
            return json.dumps(clientes[matricula])
        
        else:
            # Jogar para ultimo consumo o dado de consumo atual do hidrometro e colocar divida no cliente
            # Pegar dados do banco
            with open("banco/hidrometros.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)
            
            # atualizar o Ultimo consumo atual e gerar conta
            uc = str(hidrometros[matricula.lower()]["ultimoConsumo"])
            ca = str(hidrometros[matricula.lower()]["consumoAtual"])
            bl = str(hidrometros[matricula.lower()]["bloqueado"])
            va = str(hidrometros[matricula.lower()]["vazando"])
            
            metrosCubicosGastos =  int(ca) - int(uc)
            valorPagar = metrosCubicosGastos * 6      # Cada Metro cubico ta saindo a 6 Reais
            
            hidrometros[matricula.lower()] = {"ultimoConsumo" : ca, "consumoAtual" : ca, "bloqueado" : bl, "vazando" : va}

            #Salvar alterações do hidrometro no banco
            with open("banco/hidrometros.json", 'w' , encoding='utf-8') as database:
                    json.dump(hidrometros, database, indent=4)  
            

            #Atualizar divida no cliente e salvar
            clientes[matricula.lower()] = {"divida" : str(valorPagar)}

            with open("banco/clientes.json", 'w' , encoding='utf-8') as database:
                    json.dump(clientes, database, indent=4)  

            return json.dumps(clientes[matricula])

    
    def PUT_Pagarconta(self, matricula):
        """ Rota PUT para pagar conta

            Args:
                matricula (str): matricula do cliente
            
            Returns:
                Json: Json contendo a informação que a conta foi paga
        """
        # Desbloquear Hidrometro automaticamente
        self.PUT_DesbloquearHidrometro(matricula)
        
        #Abrir database de clientes
        with open("banco/clientes.json", 'r' , encoding='utf-8') as database:
            clientes = json.load(database)

        # zerar a divida
        clientes[matricula.lower()] = {"divida" : "0"}
        
        #Salvar alterações no banco
        with open("banco/clientes.json", 'w' , encoding='utf-8') as database:
            json.dump(clientes, database, indent=4)  
        
        return json.dumps('{"conta": "paga"}')


    # Metodos Hidrometro


    def PUT_NovoConsumoTotal(self, matricula, novoConsumo, vazando):
        """ Rota PUT para mandar os dados de consumo do hidrometro para o banco

            Args:
                matricula (str): matricula do cliente
                novoConsumo (str): consumo atual do hidrometro
                vazando (str): informação se tem vazamento nesse hidrometro 
            
            Returns:
                Json: Json contendo a informação se o hidrometro ta bloqueado ou não 
        """
        # Mandar os dados de consumo para o banco
        try:
            # Pegar dados do banco
            with open("banco/hidrometros.json", 'r' , encoding='utf-8') as database:
                hidrometros = json.load(database)

            # bloquar hidrometro
            uc = str(hidrometros[matricula.lower()]["ultimoConsumo"])
            bl = str(hidrometros[matricula.lower()]["bloqueado"])
            hidrometros[matricula.lower()] = {"ultimoConsumo" : uc, "consumoAtual" : novoConsumo, "bloqueado" : bl, "vazando" : vazando}
        
            #Salvar alterações no banco
            with open("banco/hidrometros.json", 'w' , encoding='utf-8') as database:
                json.dump(hidrometros, database, indent=4)  

            # Chamar função para gerar boleto do dono do hidrometro.
            self.GET_GerarBoleto(matricula)  
            
            retorno = '{ "bloqueado" : "-" }'.replace("-",bl)
            return json.dumps(retorno)
        except:
            return json.dumps('{ "validar" : "False" }')
    