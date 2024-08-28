import socket

def main():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('localhost', 7774))
        print("Conectado ao servidor.")
    except Exception as e:
        return print(f"\n Não foi possível se conectar: {e}")

    receiveMessages(client)
    sendMessages(client)


def receiveMessages(client):
    try:
        msg = client.recv(1024).decode('utf-8')
        if msg:
            print(msg)
    except Exception as e:
        print(f'Erro ao receber mensagem: {e}')


def sendMessages(client):
    while True:
        try:
            msg = input()
            client.send(msg.encode('utf-8'))
        except Exception as e:
            print(f'Erro ao enviar mensagem: {e}')
            break


if __name__ == "__main__":
    main()
