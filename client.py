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

    run_client(client)



def run_client(client):
    
    while True:
        try:
                  
            msg = input("> ")

            if not msg.strip():
                print('Digite alguma opção\n')
                continue
                
            client.send(msg.encode("utf-8"))

            response = client.recv(1024)
            response = response.decode("utf-8")

            # se a resposta estiver vazia é pq o server caiu
            if not response:
                raise ConnectionResetError

            # se server enviar closed, sai do loop e fecha a conexão
            if response.lower() == "closed":
                print("Conexão finalizada.")
                client.close()
                break
            
            elif response.lower() == "timeout":
                print("\033[0;31m Conexão finalizada por inatividade.")
                client.close()
                break

            print(f"\n{response}")

        except (ConnectionResetError, BrokenPipeError, OSError):
            print("Conexão com o servidor foi perdida.")
            client.close()
            break
        except Exception as e:
            print(f"Erro: {e}")
            break

if __name__ == "__main__":
    main()
