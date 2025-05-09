# 🖧 Distributed Server Group com Eleição de Mestre

Este projeto implementa um sistema distribuído de servidores que se comunicam usando **multicast UDP**, com descoberta dinâmica de membros e eleição automática de um **servidor mestre** com base em prioridades.

## 🔧 Tecnologias

- Python 3
- `socket`
- `struct`
- `threading`
- Comunicação via Multicast UDP

## 🎯 Funcionalidades

- Entrada e saída de servidores em um grupo multicast.
- Descoberta automática de novos membros.
- Eleição automática de mestre com base na maior prioridade.
- Envio de mensagens de broadcast (`send`) e direcionadas (`sendto`).
- Interface de linha de comando simples.

## 🚀 Como executar

1. **Clone o repositório:**

```bash
git clone https://github.com/Bonifacio258/distributed-filesystem.git
cd distributed-filesystem
```

2. **Execute múltiplos servidores com diferentes IDs e prioridades (em terminais separados):**

```bash
python3 server.py -i 1 -p 10
python3 server.py -i 2 -p 20
python3 server.py -i 3 -p 30
```

3. **Comandos disponíveis dentro de cada servidor:**

- `join`: Entra no grupo multicast.
- `leave`: Sai do grupo.
- `list`: Lista servidores conhecidos e o mestre atual.
- `send <mensagem>`: Envia uma mensagem para todos.
- `sendto <id> <mensagem>`: Envia uma mensagem privada para um servidor específico.
- `exit`: Encerra o servidor.

## 🧠 Lógica de Eleição de Mestre

- Cada servidor tem uma **prioridade** (inteiro).
- O mestre é automaticamente atualizado para o servidor com a **maior prioridade** no grupo.
- Sempre que um novo servidor entra ou sai, os demais reavaliam quem é o mestre.

## 📦 Estrutura

```
server.py         # Código principal do servidor
README.md         # Este arquivo
```

## 📌 Observações

- O grupo multicast utilizado é `224.1.1.1` e a porta `5001`.
- Para testes locais, você pode abrir vários terminais no mesmo computador.

## ✅ Exemplo de Uso

```bash
# Terminal 1
python3 server.py -i 1 -p 10

# Terminal 2
python3 server.py -i 2 -p 50

# Ambos digitam "join" no prompt para entrar no grupo
# O servidor com prioridade 50 será eleito como mestre
```

---

Feito com 💻 por [Bonifacio258](https://github.com/Bonifacio258)