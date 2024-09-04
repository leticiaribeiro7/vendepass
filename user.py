class User:
    def __init__(self, name):
        # passagem: (id_rota, numero_assento)
        self.name = name
        self.passagens = []

    def set_passagem(self, passagem):
        self.passagens.append(passagem)

    def cancel_passagem(self, passagem):
        self.passagens.remove(passagem)
        

# u = User("leti")
# u.set_passagem(1, 3)