import socket
import threading

# Script para testar 10 clientes ao mesmo tempo
# realizando a mesma operação: comprar passagem na rota 1 e assento 1

# Função que simula um cliente
def clients_test(client_id):
    try:
        # Conecta ao servidor
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5002))

        # Recebe mensagem de boas-vindas e digita o nome do cliente
        nome_msg = client_socket.recv(1024).decode('utf-8')
        print(f"\n[Cliente {client_id}] recebeu: {nome_msg}\n")
        client_socket.send(f"Cliente_{client_id}".encode('utf-8'))

        # Recebe o menu e escolhe comprar passagem (opção 2)
        menu_msg = client_socket.recv(1024).decode('utf-8')
        print(f"[Cliente {client_id}] recebeu o menu:\n{menu_msg}\n")
        client_socket.send("2".encode('utf-8'))

        # Recebe a lista de rotas e escolhe uma rota (se for par, escolhe rota 4. ímpar, rota 3)
        rotas_msg = client_socket.recv(1024).decode('utf-8')
        print(f"[Cliente {client_id}] recebeu as rotas:\n{rotas_msg}\n")
        if int(client_id) % 2 == 0:
            client_socket.send("4".encode('utf-8'))
        else:
            client_socket.send("3".encode('utf-8'))  
         

        # Recebe lista de assentos e escolhe um (assento 1)
        assentos_msg = client_socket.recv(1024).decode('utf-8')
        print(f"[Cliente {client_id}] recebeu os assentos:\n{assentos_msg}\n")
        client_socket.send("1".encode('utf-8'))

        # Recebe a confirmação da compra
        compra_msg = client_socket.recv(1024).decode('utf-8')
        print(f"[Cliente {client_id}] recebeu confirmação de compra:\n{compra_msg}\n")

    except Exception as e:
        print(f"[Erro no Cliente {client_id}] {e}\n")
    finally:
        # Fecha a conexão
        client_socket.close()


# Função para criar vários clientes em threads
def concorrencia_teste(num_clients):
    threads = []

    # Cria várias threads de clientes
    for i in range(num_clients):
        thread = threading.Thread(target=clients_test, args=(i,))
        threads.append(thread)
        thread.start()

    # Espera todas as threads terminarem
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # Testa o servidor com 10 clientes simultâneos
    print("\n--- Iniciando script de concorrência com 10 clientes. ---\n")
    concorrencia_teste(10)
    print("\n--- Script de concorrência finalizado. ---\n")

