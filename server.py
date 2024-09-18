import socket
import threading
import json
import os
import time

from user import User

users = []

lock = threading.Lock()

TIMEOUT = 120

def main():
    
    with open('data.json', 'r') as file:
        rotas = json.load(file)

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

        thread = threading.Thread(target=handle_client, args=(client, rotas))
        #threadConect = threading.Thread(target=conexao, args=(client,), daemon=True)
        thread.start()
        #threadConect.start()


# def conexao(client):
#     while True:
#         client.send('ping'.encode('utf-8'))
#         res = client.recv(1024).decode('utf-8')

#         if res != 'pong':
#             print('Conexão interrompida por erro no servidor.')
#             client.close()
#             break

#         time.sleep(2)

def handle_client(client, rotas):
    client.settimeout(TIMEOUT)
    client.send("Digite seu nome".encode('utf-8'))
    name = client.recv(1024).decode('utf-8').strip()

    user = None

    # Recupera o usuario existente se o nome for igual, senão cria um novo
    user_exist = find_user(name)

    if user_exist:
        user = user_exist
    else:
        user = User(name)
        users.append(user)

    menu = send_menu()
    client.send(f"Bem-vindo, {user.name}\n {menu}".encode('utf-8'))

    while True:
        try:
            request = client.recv(1024).decode('utf-8')
            if not request:
                break

            # reseta o tempo a cada request
            client.settimeout(TIMEOUT)
            
            match (request):     
                case "1":
                    rotas_disponiveis = get_rotas(rotas)
                    client.send(f"{rotas_disponiveis}".encode('utf-8'))

                case "2":
                    rotas_disponiveis = get_rotas(rotas)
                    client.send(f"{rotas_disponiveis}\nEscolha o número da rota correspondente: ".encode('utf-8'))

                    id_rota = int(client.recv(1024).decode('utf-8').strip())

                    # busca a rota na lista pelo id
                    rota_selecionada = None
                    for rota in rotas:
                        if rota['id'] == id_rota:
                            rota_selecionada = rota
                            break
                        
                    # se o id enviado existir, continua o fluxo mandando escolher assento
                    if rota_selecionada:

                        if not rota_selecionada['assentos-livres']:
                            client.send(f"Não há mais assentos disponíveis nesta rota. \n {menu}".encode('utf-8'))

                        else:
                            assentos = ', '.join(str(assento) for assento in rota_selecionada['assentos-livres'])
                            client.send(f"Escolha o assento: {assentos}".encode('utf-8'))
                            
                            numero_assento = int(client.recv(1024).decode('utf-8').strip())

                            # lock ate finalizar a compra do assento
                            lock.acquire()

                            if numero_assento in rota_selecionada['assentos-livres']:
                                reserva_efetuada = reserva_assento(rota_selecionada, numero_assento, rotas)

                                if reserva_efetuada:
                                    user.set_passagem({'rota': rota_selecionada, 'assento': numero_assento})
                                    print(user.name)
                                    client.send(f"Passagem comprada!\n {menu}".encode('utf-8'))
                                    time.sleep(3)
                                    os.system('clear')

                            else: client.send("O assento não está disponível.".encode('utf-8'))

                            lock.release()

                    else:
                        client.send("Rota não encontrada.".encode('utf-8'))

                case "3":

                    if not user.passagens:
                        client.send("Você não tem passagens compradas.".encode('utf-8'))
                    else:
                        
                        passagens = "\n".join(
                            f"{i + 1}. - Rota: {' -> '.join(passagem['rota']['trechos'])} - Assento: {passagem['assento']}"
                            for i, passagem in enumerate(user.passagens)
                        )
                        client.send(f"Suas passagens:\n{passagens}\nEscolha o número da passagem para cancelar: ".encode('utf-8'))
                        
                    
                        idx_passagem = int(client.recv(1024).decode('utf-8').strip()) - 1

                        if idx_passagem < len(user.passagens):
                            passagem_selecionada = user.get_passagem(idx_passagem)
                            cancelar_passagem(user, passagem_selecionada, rotas)

                            client.send(f"Passagem cancelada com sucesso.\n {menu}".encode('utf-8'))
                        else:
                            client.send("Passagem inválida.".encode('utf-8'))    
                        
                case "4":
                    client.send("closed".encode('utf-8'))
                    client.close()
                    break

                case _:
                    client.send(f"Opção inválida. Por favor, escolha uma opção do menu.\n {menu}".encode('utf-8'))
                  
                     


        except socket.timeout:
            printf(f"{user.name} desconectado por inatividade")
            client.send("timeout".encode('utf-8'))
            client.close()
            break
        except Exception as e:
            print(f"Erro: {e}")
            client.close()
            break


def cancelar_passagem(user, passagem, rotas):
    user.passagens.remove(passagem)
    assento = passagem['assento']
    rota_cancelada = passagem['rota']

    # Atualiza as rotas afetadas
    for rota in rotas:
        if rota['id'] == rota_cancelada['id']:
            # Adiciona o assento da cancelada de volta nas rotas
            if assento not in rota['assentos-livres']:
                rota['assentos-livres'].append(assento)
                rota['assentos-livres'].sort()
        
        # Se a rota cancelada é do tipo 'trecho', atualize também as rotas diretas correspondentes
        if rota_cancelada['tipo'] == 'trecho':
            for i in range(len(rota_cancelada['trechos']) - 1):
                origem_trecho = rota_cancelada['trechos'][i]
                destino_trecho = rota_cancelada['trechos'][i + 1]

                if rota['trechos'] == [origem_trecho, destino_trecho] and rota['tipo'] == 'direta':
                    if assento not in rota['assentos-livres']:
                        rota['assentos-livres'].append(assento)
                        rota['assentos-livres'].sort()
        
        # Se a rota cancelada é do tipo 'direta', atualize também as rotas de trechos correspondentes
        if rota_cancelada['tipo'] == 'direta':
            origem_trecho = rota_cancelada['trechos'][0]
            destino_trecho = rota_cancelada['trechos'][1]

            if rota['tipo'] == 'trecho' and origem_trecho in rota['trechos'] and destino_trecho in rota['trechos']:
                if assento not in rota['assentos-livres']:
                    rota['assentos-livres'].append(assento)
                    rota['assentos-livres'].sort()


def reserva_assento(rota_selecionada, numero_assento, rotas):
    
    if rota_selecionada['tipo'] == 'direta':
        rota_selecionada['assentos-livres'].remove(numero_assento)

        # bloqueia o assento nas rotas que tem trecho tbm
        for rota in rotas:
            for i in range(len(rota['trechos']) - 1):
                origem = rota['trechos'][i]
                destino = rota['trechos'][i + 1]
            
                if [origem, destino] == rota_selecionada['trechos']:
                    if numero_assento in rota['assentos-livres']:
                        rota['assentos-livres'].remove(numero_assento)

        return True
    
    elif rota_selecionada['tipo'] == 'trecho':
        rota_selecionada['assentos-livres'].remove(numero_assento)

        trechos_count = len(rota_selecionada['trechos'])

        # Itera por cada trecho da rota
        for i in range(trechos_count - 1):
            origem_trecho = rota_selecionada['trechos'][i]
            destino_trecho = rota_selecionada['trechos'][i + 1]

            # Bloqueia o assento nas rotas diretas correspondentes a cada trecho
            for rota in rotas:
                if rota['trechos'] == [origem_trecho, destino_trecho] and rota['tipo'] == 'direta':
                    if numero_assento in rota['assentos-livres']:
                        rota['assentos-livres'].remove(numero_assento)

        # Verifica se o assento foi bloqueado com sucesso na rota selecionada
        return numero_assento not in rota_selecionada['assentos-livres']
    return False


def get_rotas(rotas):
    return "\n".join(
        f"{rota['id']}. {' -> '.join(rota['trechos'])} ({rota['tipo']})"
        for rota in rotas
    )

def send_menu():
    return (
        "\n--- VendePass ---\n"
        "=======================\n"
        "1. Ver rotas\n"
        "=======================\n"
        "2. Comprar passagem\n"
        "=======================\n"
        "3. Cancelar passagem\n"
        "=======================\n"
        "4. Sair\n"
        "=======================\n"
        "Digite a opção desejada: "
    )


def find_user(name):
    for usuario in users:
        if name == usuario.name:
            return usuario


if __name__ == "__main__":
    main()
