import socket
import struct
import threading
import argparse
import time

MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT = 5001
BUFFER_SIZE = 1024


class Server:

    def __init__(self, server_id, priority):
        self.server_id = server_id
        self.priority = priority
        self.group_members = {}  # Dicionário para armazenar {server_id: priority}
        self.master_id = None  # ID do servidor mestre
        self.sock = None
        
        print(f"\n🎉 Bem-vindo ao Servidor {self.server_id}! Prioridade: {self.priority}\n")
        threading.Thread(target=self.listen_messages, daemon=True).start()

    def listen_messages(self):
        """ Fica ouvindo mensagens de outros servidores """
        while True:
            if not self.sock or self.sock._closed:
                continue
            try:
                data, _ = self.sock.recvfrom(BUFFER_SIZE)
                message = data.decode().strip()

                if message:
                    self.handle_message(message)
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")

    def handle_message(self, message):
        """ Processa as mensagens recebidas """
        parts = message.split(":")
        if len(parts) < 2:
            return

        msg_type, sender_id = parts[:2]
        sender_id = int(sender_id)

        if msg_type == "JOIN":
            sender_priority = int(parts[2])
            if sender_id != self.server_id:
                self.group_members[sender_id] = sender_priority
                print(f"✨ Servidor {sender_id} entrou no grupo!")
                self.send_message(f"WELCOME:{self.server_id}:{self.priority}")
        elif msg_type == "WELCOME":
            sender_priority = int(parts[2])
            self.group_members[sender_id] = sender_priority
        elif msg_type == "LEAVE":
            self.group_members.pop(sender_id, None)
            print(f"🚪 Servidor {sender_id} saiu do grupo.")
        elif msg_type == "MESSAGE":
            msg_content = parts[2]
            print(f"\n📩 [SERVER {sender_id}]: {msg_content}")
        elif msg_type == "MESSAGE_TO":
            target_id, msg_content = int(parts[2]), parts[3]
            if target_id == self.server_id:
                print(f"\n📩 [SERVER {sender_id} -> YOU]: {msg_content}")

        self.update_master()
        self.print_discovered_servers()

    def join_group(self):
        """ Servidor entra no grupo multicast """
        if self.server_id in self.group_members:
            print(f"Você já está no grupo!")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", MULTICAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"🚀 Servidor {self.server_id} entrando no grupo...")
        self.group_members[self.server_id] = self.priority
        self.send_message(f"JOIN:{self.server_id}:{self.priority}")
        time.sleep(1)

        self.update_master()
        self.print_discovered_servers()

    def leave_group(self):
        """ Servidor sai do grupo """
        if not self.group_members:
            print("Você ainda não pertence a nenhum grupo!")
            return

        print(f"Servidor {self.server_id} saindo do grupo...")
        self.send_message(f"LEAVE:{self.server_id}")
        self.sock.close()
        self.group_members.clear()
        self.master_id = None

    def list_group(self):
        """ Lista servidores no grupo """
        if not self.group_members:
            print("Nenhum servidor encontrado!")
        else:
            print(f"Servidores no grupo: {self.group_members}")

    def send_message(self, message):
        """ Envia uma mensagem para o grupo multicast """
        self.sock.sendto(message.encode(), (MULTICAST_GROUP, MULTICAST_PORT))

    def send_chat_message(self, msg_content):
        """ Envia uma mensagem de chat para o grupo """
        self.send_message(f"MESSAGE:{self.server_id}:{msg_content}")
    
    def send_direct_message(self, target_id, msg_content):
        """ Envia uma mensagem diretamente para um servidor específico """
        if target_id in self.group_members:
            self.send_message(f"MESSAGE_TO:{self.server_id}:{target_id}:{msg_content}")
        else:
            print(f"❌ O servidor {target_id} não está no grupo!")

    def update_master(self):
        """ Atualiza o servidor mestre com a maior prioridade """
        if self.group_members:
            self.master_id = max(self.group_members, key=self.group_members.get)
        else:
            self.master_id = self.server_id

    def print_discovered_servers(self):
        """ Imprime os servidores descobertos e quem é o mestre """
        if self.group_members:
            print("\nServidores descobertos no grupo:")
            for server_id, priority in self.group_members.items():
                print(f"(SERVER {server_id}; PRIORITY: {priority})")

            print(f"\n⚡ SERVIDOR MESTRE: SERVER {self.master_id} (PRIORITY: {self.group_members[self.master_id]})")

        if len(self.group_members) == 3:
            print("✅ Todos os servidores estão no grupo!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=int, required=True, help="ID do servidor")
    parser.add_argument("-p", "--priority", type=int, required=True, help="Prioridade do servidor")

    args = parser.parse_args()

    print(f"🔹 Servidor iniciado com ID {args.id} e prioridade {args.priority}")

    server = Server(args.id, args.priority)

    try:
        while True:
            command = input("\nComando (join, leave, list, send <mensagem>, sendto <id> <mensagem>, exit):\n")
            if command == "join":
                server.join_group()
            elif command == "leave":
                server.leave_group()
            elif command == "list":
                server.list_group()
            elif command.startswith("send "):
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("❌ Uso correto: send <mensagem>")
                else:
                    _, msg = parts
                    server.send_chat_message(msg)
            elif command.startswith("sendto "):
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    print("❌ Uso correto: sendto <id> <mensagem>")
                else:
                    _, target_id, msg = parts
                    server.send_direct_message(int(target_id), msg)
            elif command == "exit":
                break
            else:
                print("❌ Comando inválido! Tente novamente.")
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        if server.sock and not server.sock._closed:
            server.sock.close()
