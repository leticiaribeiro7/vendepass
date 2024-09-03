import socket
import threading

users = []

rotas = [
    {'id': 1, 'trecho': 'SSA -> SP', 'assentos-livres': [1, 2, 3]},
    {'id': 2, 'trecho': 'SSA -> RJ', 'assentos-livres': [1, 2, 4]},
]  



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
                    rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['trecho']}" for rota in rotas)
                    client.send(f"{rotas_disponiveis}\n".encode('utf-8'))
                case "2":
                    rotas_disponiveis = "\n".join(f"{rota['id']}. {rota['trecho']}" for rota in rotas)
                    client.send(f"{rotas_disponiveis}\n Escolha o número da rota correspondente: ".encode('utf-8'))

                    for rota in rotas:
                        if rota['id'] == request:
                            assentos = ', '.join(str(assento) for assento in rota['assentos-livres'])

                    client.send(f"Escolha o assento: {assentos}".encode('utf-8'))
                    # lock começando aqui
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
