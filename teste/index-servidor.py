import threading
import socket
#import keyboard


clientes = []

def main():

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        servidor.bind(('localhost', 7777))
        servidor.listen()
    except:
        return print('\nServidor não iniciado.')
    
    while True:
        cliente, endereco = servidor.accept()
        clientes.append(cliente)

        thread = threading.Thread(target=tratamentoMsg, args=[cliente])
        thread.start()

'''       if keyboard.is_pressed('esc'):
            servidor.close()
            print('\nServidor encerrado.')
            break
'''

def tratamentoMsg(cliente):
    while True:
        try:
            msg = cliente.recv(2048)
            transmissao(msg, cliente)
        except:
            deletaCliente(cliente)
            break


def transmissao(msg, cliente):
    for clienteItem in clientes:
        if clienteItem != cliente:
            try:
                clienteItem.send(msg)
            except:
                deletaCliente(clienteItem)


def deletaCliente(cliente):
    clientes.remove(cliente)






main()