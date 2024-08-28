import socket

def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('127.0.0.1', 5000))
        server.listen()
        print("Servidor iniciado e aguardando conexões...")
    except Exception as e:
        return print(f'\n Não foi possível iniciar o servidor: {e}')
    
    
    while True:
        client, address = server.accept()
        print(f"Conexão estabelecida com {address}")
        send_menu(client)
        receiveMessages(client, server)


def receiveMessages(client, server):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                print(f"Mensagem do cliente: {msg}")
                if (msg == '1'):
                    print("Pressionou 1")
                if (msg == '3'):
                    server.close()
                    print("Servidor finalizado")
        except Exception as e:
            print(f'Erro ao receber mensagem: {e}')
            break

def sendMessages(client):
    while True:
        try:
            msg = input()
            client.send(msg).decode('utf-8')
        except Exception as e:
            print(f'Erro ao enviar mensagem: {e}')
            break

def send_menu(client):
    menu = (
        "\n--- Menu ---\n"
        "1. Ver rotas\n"
        "2. Comprar passagem\n"
        "3. Sair\n"
        "Digite a opção desejada: "
    )

    try:
        client.send(menu.encode('utf-8'))
    except Exception as e:
        print(f'Erro ao enviar o menu: {e}')


if __name__ == "__main__":
    main()
