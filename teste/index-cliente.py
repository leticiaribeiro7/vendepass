import threading
import socket

def main():

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect(('localhost', 7777))
    except:
        return print("Não conectou ao servidor.")
    
    nome = input("Nome do usuário: ")
    print("\nConectado")

    thread1 = threading.Thread(target=recebeMsg, args=[cliente])
    thread2 = threading.Thread(target=enviaMsg, args=[cliente, nome])

    thread1.start()
    thread2.start()


def recebeMsg(cliente):
    while True:
        try:
            msg = cliente.recv(2048).decode('utf-8')
            print(msg+'\n')
        except:
            print('Desconectado do servidor.')
            print('<ENTER> para continuar.')
            cliente.close()
            break


def enviaMsg(cliente, nome):
    while True:
        try:
            msg = input("\n")
            cliente.send(f'[{nome}]: {msg}'.encode('utf-8'))
        except:
            return



main()

