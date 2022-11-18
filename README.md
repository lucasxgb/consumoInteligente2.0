# Consumo de água inteligente - parte 2

<p align="center">

<h4 align="center" > Universidade Estadual de Feira de Santana </h4>
<h4 align="center" >  TEC502 - Concorrência e Conectividade  </h4>
</p>


- Esse projeto foi desenvolvido por: 
    
  	- [Lucas Gabriel da Silva Lima Reis](https://github.com/lucasxgb), 
	- [Silas Silva Costa](https://github.com/silas-silva)
	
- Avaliado por: 
	- [Antonio Augusto Teixeira Ribeiro Coutinho](https://linkedin.com/in/antonio-augusto-teixeira-ribeiro-coutinho-03a3217)


## Introdução:

- Após o desenvolvimento do protótipo para automação do sistema de coleta e envio de dados, relacionados ao abastecimento de água da população. Onde o principal objetivo era promover o uso consciente da água junto a população, recebendo dados de um hidrômetro inteligente, e a partir desses dados gerando todas as informações possíveis que facilitasse tanto para os administradores ao verificar os hidrômetros, quanto para os clientes ao visualizar dados do seu consumo de água.

	- Veja um pouco mais sobre a Parte 1 desse problema em:
		- Código de Lucas - [ConsumoInteligente](https://github.com/lucasxgb/consumoInteligente 'Lucas'),	
		- Código de Silas - [redeControleAgua](https://github.com/silas-silva/rede_controle_agua_SOCKET 'Silas')

- Foi solicitado a nós da equipe de desenvolvimento a continuação desse trabalho, agora sendo necessário a mudança para um modelo de servidor descentralizado,no qual os computadores conectados ao sistema funcionam também como servidores (Infomoney 2022). Onde ao invés de realizar todo processamento de informações na nuvem ou servidor principal, as informações de menor prioridade, ou que não exigem conhecimento de todos os dados do sistema sempre serão tratados na névoa que está mais próxima ao usuário.
	
## Arquitetura do sistema:
![Arquitetura do sistema](https://github.com/lucasxgb/consumoInteligente2.0/blob/main/_PBL/imagens/Hidrometro.jpg)
- O sistema é constituído pelas seguintes partes:
	- `Conexão Mqtt`: Toda estrutura de conexão entre itens foi feita utilizando o protocolo MQTT. Tendo como broker o mosquitto, que foi configurado manualmente para que fosse possível sua execução na porta e no host adequado. A forma como o servidor recebia e enviava as requisições para os tópicos MQTT foi construída utilizando os princípios de API REST, passando em toda mensagem de tópico mqtt, informações como, Verbo, Status, Contéudo simulando o HTTP.
	- `Nuvem`: Servidor centralizado, que serve para realizar funcionalidades em que necessite da informação de todas as nuvens, sendo elas:
		- `Listagem de N hidrômetros`: Listar os N hidrômetros de maior consumo na nuvem.
		- `Bloqueio hidrômetros`: Bloquear os hidrômetros, tanto utilizando a média como solicitado por um Adm.
	- `Névoa`: Máquinas descentralizadas, que atuam como clientes e servidores, possuindo cada uma o seu próprio banco de dados e tratando tudo que for "mais simples" e que não precise de informações de todos os outros. A névoa pode gerenciar as médias dos hidrômetros e também pode transmitir informações sobre os mesmos diretamente para o cliente ou administrador.
	- `Cliente / Administrador`: São os usuários do sistema, responsáveis pela solicitação de informações relacionadas aos hidrômetros.
	- `Hidrômetros`: Enviam os dados relacionados ao consumo, matrícula, vazão para névoa.



## Resultados e Conclusões:
Conclui-se que o desenvolvimento do projeto foi bem sucedido, uma vez que ao testar todas as suas funcionalidades, o mesmo conseguiu atendê-las bem, sanando assim todos os requisitos solicitados pelos clientes.
Um ponto a melhorar é a interface que pode ser melhor desenvolvida, pois, no momento está sendo somente por linhas de comando.


## Referências: 
***Infomoney. "O que é Peer - to- Peer(P2P)".https://blog.feabhas.com/2020/02/running-the-eclipse-mosquitto-mqtt-broker-in-a-docker-container/
https://www.digitalocean.com/community/questions/how-to-setup-a-mosquitto-mqtt-server-and-receive-data-from-owntracks. Acesso em 18 de Out de 2022.***

***Steve. "MQTT and Python For Beginners -Tutorials".[https://blog.feabhas.com/2020/02/running-the-eclipse-mosquitto-mqtt-broker-in-a-docker-container/
https://www.digitalocean.com/community/questions/how-to-setup-a-mosquitto-mqtt-server-and-receive-data-from-owntracks.](http://www.steves-internet-guide.com/mqtt-python-beginners-course/) Acesso em 18 de Out de 2022.***
