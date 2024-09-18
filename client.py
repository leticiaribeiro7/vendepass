import socket
import threading
import time

def main():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('localhost', 5000))
        print("Conectado ao servidor.")

        # Recebe e imprime o menu inicial enviado pelo servidor
        response = client.recv(1024).decode('utf-8')
        
        print(response)

    except Exception as e:
        return print(f"\n Não foi possível se conectar: {e}")

   # threading.Thread(target=conexao, args=(client,), daemon=True).start()
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
                print("Conexão finalizada.")
                client.close()
                break
            
            elif response.lower() == "timeout":
                print("Conexão finalizada por inatividade.")
                client.close()
                break

            print(f"\n{response}")

        except (ConnectionResetError, BrokenPipeError):
            print("Conexão com o servidor foi perdida.")
            client.close()
            break
        except Exception as e:
            print(f"Error: {e}")
            break


# def conexao(client):
#     while True:
#         res = client.recv(1024).decode('utf-8')
#         client.send('pong'.encode('utf-8'))

#         if res != 'ping':
#             print('Conexão interrompida por erro no servidor.')
#             client.close()
#             break

#         time.sleep(5)
        
if __name__ == "__main__":
    main()
