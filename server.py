import socket
import threading

users = []

rotas = [
    {'id': 1, 'origem': 'SSA', 'destino': 'SP', 'assentos-livres': [1, 2, 3]},
    {'id': 2, 'origem': 'SSA', 'destino': 'RJ', 'assentos-livres': [1, 2, 4]},
]  

lock = threading.Lock()


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('0.0.0.0', 5000))
        server.listen()
        print("Servidor iniciado e aguardando conexões...")
    
    except Exception as e:
        return print(f'\n Não foi possível iniciar o servidor: {e}')
    
    while True:
        client, address = server.accept()
        print(f"Conexão estabelecida com {address}")
        
        client.send("Digite seu nome".encode('utf-8'))
        name = client.recv(1024).decode('utf-8').strip()

        users.append(name)

        menu = send_menu(client)
        client.send(f"Bem vindo {name}\n {menu}".encode('utf-8'))

        # receiveMessages(client, server)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


def handle_client(client):

    while True:
        try:
            request = client.recv(1024).decode('utf-8')
            match request:
                case "1":
                    rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['origem']} - {rota['destino']}" for rota in rotas)
                    client.send(f"{rotas_disponiveis}\n".encode('utf-8'))
                case "2":
                    rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['origem']} - {rota['destino']}" for rota in rotas)
                    client.send(f"{rotas_disponiveis}\n Escolha o número da rota correspondente: ".encode('utf-8'))

                    id_rota = int(client.recv(1024).decode('utf-8').strip())
                    rota_selecionada = ''

                    #pega rota pelo id
                    for rota in rotas:
                        if rota['id'] == id_rota:
                            rota_selecionada = rota

    
                    if rota_selecionada:
                        assentos = ', '.join(str(assento) for assento in rota_selecionada['assentos-livres'])
                        client.send(f"Escolha o assento: {assentos}".encode('utf-8'))
                        
                        numero_assento = int(client.recv(1024).decode('utf-8').strip())

                        #remove o assento da lista de disponiveis
                        lock.acquire()
                        if numero_assento in rota_selecionada['assentos-livres']:
                            rota_selecionada['assentos-livres'].remove(numero_assento)
                            client.send("Passagem comprada!".encode('utf-8'))
                            
                            # associar ao usuario aqui de alguma forma
                        else:
                            client.send("O assento não está mais disponível.".encode('utf-8'))
                        lock.release()
                    else:
                        client.send("Rota não encontrada.".encode('utf-8'))

                        
                case "4":
                    client.send("closed".encode('utf-8'))
                    client.close()
        except Exception as e:
            print(f"Error when handling client: {e}")
        # finally:
        #     print("Conexão do cliente com o server fechada")
        #     client.close()
        

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
    #client.send(menu.encode('utf-8'))

# Mostra quais as rotas disponiveis
def get():
    pass

if __name__ == "__main__":
    main()
