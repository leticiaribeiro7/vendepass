class User:
    def __init__(self, name):
        # passagem: rota:{}, assento:0
        self.name = name
        self.passagens = []

    def set_passagem(self, passagem):
        self.passagens.append(passagem)

    def cancel_passagem(self, passagem):
        self.passagens.remove(passagem)

    def get_passagem(self, id):
        return self.passagens[id]
    