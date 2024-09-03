import socket
import threading

users = []

# Tratamento quando não tiver mais assentos disponíveis
# Travando no "Digite seu nome" quando entra 2 clientes no mesmo servidor
# Exibir trechos em exibição e comprar

rotas = [
    {'id': 1, 'origem': 'SSA', 'destino': 'SP', 'tipo': 'direta', 'assentos-livres': [1, 2, 3]},
    {'id': 2, 'origem': 'SSA', 'destino': 'RJ', 'tipo': 'direta', 'assentos-livres': [1, 2, 4]},
    {'id': 3, 'origem': 'SP', 'destino': 'RJ', 'tipo': 'direta', 'assentos-livres': [1, 3, 5]},
    {'id': 4, 'origem': 'SSA', 'trecho': 'SP', 'destino': 'RJ', 'tipo': 'trecho', 'assentos-livres': [1, 2, 3]}
]

lock = threading.Lock()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('0.0.0.0', 7722))
        server.listen()
        print("Servidor iniciado e aguardando conexões...")
    
    except Exception as e:
        return print(f'\n Não foi possível iniciar o servidor: {e}')
    
    while True:
        client, address = server.accept()
        print(f"Conexão estabelecida com {address}")

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

def handle_client(client):
    client.send("Digite seu nome".encode('utf-8'))
    name = client.recv(1024).decode('utf-8').strip()

    users.append(name)

    menu = send_menu(client)
    client.send(f"Bem-vindo {name}\n {menu}".encode('utf-8'))
    while True:
        try:
            request = client.recv(1024).decode('utf-8')
            if request == "1":
                rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['origem']} - {rota['destino']}" for rota in rotas)
                client.send(f"{rotas_disponiveis}".encode('utf-8'))

            if request == "2":
                rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['origem']} - {rota['destino']}" for rota in rotas)
                client.send(f"{rotas_disponiveis}\nEscolha o número da rota correspondente: ".encode('utf-8'))

                id_rota = int(client.recv(1024).decode('utf-8').strip())
                rota_selecionada = next((rota for rota in rotas if rota['id'] == id_rota), None)

                if rota_selecionada:
                    assentos = ', '.join(str(assento) for assento in rota_selecionada['assentos-livres'])
                    client.send(f"Escolha o assento: {assentos}".encode('utf-8'))
                    
                    numero_assento = int(client.recv(1024).decode('utf-8').strip())

                    if numero_assento in rota_selecionada['assentos-livres']:
                        lock.acquire()
                        reserva_efetuada = reserva_assento(rota_selecionada, numero_assento)
                        lock.release()

                        if reserva_efetuada:
                            client.send("Passagem comprada!".encode('utf-8'))
                        else:
                            client.send("Não foi possível reservar o assento. Pode estar ocupado em uma conexão de trecho.".encode('utf-8'))
                    else:
                        client.send("O assento não está mais disponível.".encode('utf-8'))
                else:
                    client.send("Rota não encontrada.".encode('utf-8'))

            if request == "4":
                client.send("closed".encode('utf-8'))
                client.close()
                break

        except Exception as e:
            print(f"Error when handling client: {e}")
            client.close()
            break

def reserva_assento(rota_selecionada, numero_assento):
    if rota_selecionada['tipo'] == 'direta':
        rota_selecionada['assentos-livres'].remove(numero_assento)
        return True
    elif rota_selecionada['tipo'] == 'trecho':
        for rota in rotas:
            if rota['origem'] == rota_selecionada['trecho'] and rota['destino'] == rota_selecionada['destino'] and rota['tipo'] == 'direta':
                if numero_assento in rota['assentos-livres']:
                    rota['assentos-livres'].remove(numero_assento)
                    rota_selecionada['assentos-livres'].remove(numero_assento)
                    return True
    return False

def send_menu(client):
    menu = (
        "\n--- VendePass ---\n"
        "1. Ver rotas\n"
        "2. Comprar passagem\n"
        "3. Cancelar passagem\n"
        "4. Sair\n"
        "Digite a opção desejada: "
    )
    return menu

if __name__ == "__main__":
    main()
