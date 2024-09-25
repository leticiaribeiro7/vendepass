import socket
import threading
import json  

# Teste de 10 clientes simulados conectando e tentando comprar o 
# mesmo assento (nem sempre mesma rota) simultaneamente

# Sugestão: deixar só a confirmação de compra pra exibir ao usuário
# para melhor visualizar somente o resultado do teste


# Função que simula um cliente
def clients_test(client_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5000))

        # Função auxiliar para receber mensagens
        def recv_json():
            data = client_socket.recv(2048).decode('utf-8')
            if not data:
                raise ValueError("Nenhuma mensagem recebida")
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise ValueError(f"Mensagem inválida recebida: {data}")

        nome_msg = recv_json()
        print(f"\n[Cliente {client_id}] recebeu: {nome_msg}\n")
        client_socket.send(json.dumps({"nome": f"Cliente_{client_id}"}).encode('utf-8'))

        # Recebe o menu e escolhe comprar passagem (opção 2)
        menu_msg = recv_json()
        print(f"[Cliente {client_id}] recebeu o menu:\n{menu_msg}\n")
        client_socket.send(json.dumps({"option": 2}).encode('utf-8'))

        # Recebe a lista de rotas e escolhe uma rota (se for par, escolhe rota 4. ímpar, rota 3)
        rotas_msg = recv_json()
        print(f"[Cliente {client_id}] recebeu as rotas:\n{rotas_msg}\n")
        rota_escolhida = 4 if int(client_id) % 2 == 0 else 3
        client_socket.send(json.dumps({"option": rota_escolhida}).encode('utf-8'))

        # Recebe lista de assentos e escolhe um (assento 1)
        assentos_msg = recv_json()
        print(f"[Cliente {client_id}] recebeu os assentos:\n{assentos_msg}\n")
        client_socket.send(json.dumps({"option": 1}).encode('utf-8'))

        # Recebe a confirmação da compra
        compra_msg = recv_json()
        print(f"[Cliente {client_id}] recebeu confirmação de compra:\n{compra_msg}\n")

    except Exception as e:
        print(f"[Erro no Cliente {client_id}] {e}\n")
    finally:
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
