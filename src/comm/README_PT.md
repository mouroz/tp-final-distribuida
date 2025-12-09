# Descrição
Esse módulo implementa um sistema distribuido de mensagem com replicação ativa usando gRPC e estratégia de replicação ativa, onde um cliente envia a mensagem para varios servidores de forma a garantir redundancia

# Estrutura 
├── client.py           # Envio e recebimento dos dados com o stub
├── server.py           # Responde ao cliente
├── grpc_messenger/         # Contém os arquivos gerados pelo grpc
    ├── messenger.proto     # Definição do grpc
    ├── compile_proto.sh    # Script para compilação do grpc
└── README.md

# Implementação
## Server
Define Skeleton com métodos Send e ReceiveAll

Armazena a fila de mensagem para recebimento de todos as mensagens (método Send) através de um dicionario que recebe o email como chave e apende os dados da mensagem em uma lista:

```
self.mailboxes = defaultdict(list)
self.mailboxes[email].append(message)
```

Os dados armazenados incluem todos os dados recebidos através do cliente, como definido no arquivo .proto:

```
message SendRequest {
  int32 id = 1;
  string msg = 2;
  string self_email = 3;
  string dest_email = 4; 
}
```

Ao receber a requisição ReceiveAll, equivalente ao refresh em aplicativos de email, todos os dados na fila anexadas ao email são retornados ao cliente, e a fila será esvaziada



## Cliente

Inicializa e cria conexão com uma lista de stubs para comunicar com multiplos servidores de forma simultanea.

Usa de um método auxiliar (send_messages) para invocar o método Send aos múltiplos stubs com a mesma mensagem

Usa de um método auxiliar (receive_all_messages) para invocar o método ReceiveAll para múltiplos stubs, retornando a InboxResponse de todos os servidores. Essa estrutura se consiste em uma simples lista da mensagens recebidas pelo servidor e salvas na fila interna dele. É definida como:

```
message InboxResponse {
  repeated SendRequest messages = 1;
}
```

Idealmente se nenhum servidor falhou, para 3 servidores teremos 3 cópias iguais do InboxResponsa, com multiplas mensagens em formato SendRequest. Caso contrário, é esperado que ao menos um servidor não tenha falhado para cada mensagem que foi enviada pelos clientes. 

Um método auxiliar (extract_receive_all_unique_responses) extrai as respostas únicas recebidas por todos os servidores (mesmo ID e mesmo email origem) e as retorna para o uso em outros métodos, que poderão mostrar essas mensagens obtidas ao usuário (interface), ou salvá-las no disco rígido (permanência de dados).



# Informações para Desenvolvedores

A estrutura deste projeto é altamente sensível a alterações na estrutura de diretórios (um arquivo pertencente a src/comm não pode ser movido para outro lugar).

Fora isso, os arquivos Python (pelo menos para comm/ e test/comm_test.py) atualmente podem ser executados de qualquer lugar e importados de outros scripts sem erros, desde que o caminho sys.path correto seja fornecido.

## Recompile proto:
**Alterar nomes no arquivo proto é extremamente propenso a quebras! Faça isso apenas se for um desenvolvedor.**
```
sudo chmod +x src/comm/grpc_messager/compile_proto.sh
src/comm/grpc_messager/compile_proto.sh
```

## Iniciar servidor: 
```
python src/comm/server.py --ip=[::] --port=50051
```

## Iniciar teste do cliente:
```
python src/test/comm_test.py
```