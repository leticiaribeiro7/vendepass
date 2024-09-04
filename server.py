import socket
import threading
from user import User

users = []

# Tratamento quando não tiver mais assentos disponíveis
# Travando no "Digite seu nome" quando entra 2 clientes no mesmo servidor
# Exibir trechos em exibição e comprar

rotas = [
    {'id': 1, 'trechos': ['SSA', 'SP'], 'tipo': 'direta', 'assentos-livres': [1, 2, 3]},
    {'id': 2, 'trechos': ['SSA', 'MG'], 'tipo': 'direta', 'assentos-livres': [1, 2, 4]},
    {'id': 3, 'trechos': ['SP', 'RJ'], 'tipo': 'direta', 'assentos-livres': [1, 3, 5]},
    {'id': 4, 'trechos': ['SSA', 'MG', 'SP', 'RJ'], 'tipo': 'trecho', 'assentos-livres': [1, 2, 3]}
]

lock = threading.Lock()

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

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

def handle_client(client):
    client.send("Digite seu nome".encode('utf-8'))
    name = client.recv(1024).decode('utf-8').strip()

    user = User(name)
    users.append(user)

    menu = send_menu()
    client.send(f"Bem-vindo {user.name}\n {menu}".encode('utf-8'))

    while True:
        try:
            request = client.recv(1024).decode('utf-8')
            match (request):
                
                case "1":
                    rotas_disponiveis = get_rotas()
                    client.send(f"{rotas_disponiveis}".encode('utf-8'))

                case "2":
                    rotas_disponiveis = get_rotas()
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
                        assentos = ', '.join(str(assento) for assento in rota_selecionada['assentos-livres'])
                        client.send(f"Escolha o assento: {assentos}".encode('utf-8'))
                        
                        numero_assento = int(client.recv(1024).decode('utf-8').strip())

                        # lock ate finalizar a compra do assento
                        lock.acquire()

                        if numero_assento in rota_selecionada['assentos-livres']:
                            reserva_efetuada = reserva_assento(rota_selecionada, numero_assento)

                            if reserva_efetuada:
                                user.set_passagem({'rota': rota_selecionada, 'assento': numero_assento})
                                print(user.name)
                                client.send("Passagem comprada!".encode('utf-8'))

                        else: client.send("O assento não está mais disponível.".encode('utf-8'))

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
                            cancelar_passagem(user, passagem_selecionada)

                            client.send("Passagem cancelada com sucesso.".encode('utf-8'))
                        else:
                            client.send("Passagem inválida.".encode('utf-8'))    
                        
                case "4":
                    client.send("closed".encode('utf-8'))
                    client.close()
                    break

        except Exception as e:
            print(f"Erro: {e}")
            client.close()
            break

def cancelar_passagem(user, passagem):
    user.passagens.remove(passagem)
    assento = passagem['assento']

    for rota in rotas:
        if (passagem['rota'] == rota):
            rota['assentos-livres'].append(assento)
            rota['assentos-livres'].sort()


def reserva_assento(rota_selecionada, numero_assento):
    if rota_selecionada['tipo'] == 'direta':
        rota_selecionada['assentos-livres'].remove(numero_assento)

        return True
    
    elif rota_selecionada['tipo'] == 'trecho':
            if numero_assento in rota_selecionada['assentos-livres']:
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


def get_rotas():
    return "\n".join(
        f"{rota['id']}. {' -> '.join(rota['trechos'])} ({rota['tipo']})"
        for rota in rotas
    )

def send_menu():
    return (
        "\n--- VendePass ---\n"
        "1. Ver rotas\n"
        "2. Comprar passagem\n"
        "3. Cancelar passagem\n"
        "4. Sair\n"
        "Digite a opção desejada: "
    )

if __name__ == "__main__":
    main()
