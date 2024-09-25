import socket
import threading
import time
import json

def main():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('0.0.0.0', 5000))
        print("Conectado ao servidor.")

        # Recebe e imprime o menu inicial enviado pelo servidor
        response = json.loads(client.recv(2048).decode('utf-8'))
        print(response.get("message"))


    except Exception as e:
        return print(f"\n Não foi possível se conectar: {e}")

    run_client(client)



def run_client(client):
    
    while True:
        try:
                  
            msg = input("> ")

            if not msg.strip():
                print('Digite alguma opção')
                continue

            req = {"option": msg}   
            client.send(json.dumps(req).encode("utf-8"))

            response = json.loads(client.recv(2048).decode('utf-8'))

            status = response.get("status")
            
            # se a resposta estiver vazia é pq o server caiu
            if not response:
                raise ConnectionResetError

            # se server enviar closed, sai do loop e fecha a conexão
            if status == "closed":
                print("Conexão finalizada.")
                client.close()
                break
            
            elif status == "timeout":
                print("\033[0;31m Conexão finalizada por inatividade.")
                client.close()
                break
            
            message = response.get('message')

            print(f"\n{message}")

        except (ConnectionResetError, BrokenPipeError, OSError, Exception):
            print("Conexão com o servidor foi perdida.")
            client.close()
            break

if __name__ == "__main__":
    main()
