import socket

def main():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('0.0.0.0', 5002))
        print("Conectado ao servidor.")

        # Recebe e imprime o menu inicial enviado pelo servidor
        response = client.recv(1024).decode('utf-8')
        
        print(f"Received from server: {response}")

    except Exception as e:
        return print(f"\n Não foi possível se conectar: {e}")

    run_client(client)



def run_client(client):
    
    while True:
        try:
                  
            msg = input("> ")
            client.send(msg.encode("utf-8"))

            response = client.recv(1024)
            response = response.decode("utf-8")


            # se server enviar closed, sai do loop e fecha a conexão
            if response.lower() == "closed":
                client.close()
                break

            print(f"\n{response}")

        except Exception as e:
            print(f"Error: {e}")
            break
        # finally:
        #     # close client socket (connection to the server)
        #     client.close()
        #     print("Connection to server closed")

# def receiveMessages(client):
#     try:
#         msg = client.recv(1024).decode('utf-8')
#         if msg:
#             print(msg)
#     except Exception as e:
#         print(f'Erro ao receber mensagem: {e}')


# def sendMessages(client):
#     while True:
#         try:
#             msg = input()
#             client.send(msg.encode('utf-8'))
#         except Exception as e:
#             print(f'Erro ao enviar mensagem: {e}')
#             break


if __name__ == "__main__":
    main()
