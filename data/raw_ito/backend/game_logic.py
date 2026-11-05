import random

class ItoGame:
    def __init__(self):
        # O baralho do Ito tem cartas de 1 a 100
        self.deck = list(range(1, 101))

        # Dicionário para guardar o nome do jogador e a carta que ele recebeu
        self.players = {}

        # O tema da rodada (ex: "O que levar para uma ilha deserta?")
        self.theme = ""

        # Cartas que foram jogadas na rodada
        self.played_cards = []

        # Indica se a rodada já começou ou não
        self.is_started = False

        # Lista de cores padrão do Ito
        self.available_colors = [
            {"name": "Preto", "hex": "#000000"},
            {"name": "Amarelo", "hex": "#FFD700"},
            {"name": "Verde", "hex": "#28A745"},
            {"name": "Roxo", "hex": "#6F42C1"},
            {"name": "Rosa", "hex": "#E83E8C"},
            {"name": "Azul", "hex": "#007BFF"},            
            {"name": "Branco", "hex": "#FFFFFF"},
            {"name": "Vermelho", "hex": "#DC3545"}
        ]

        # Dicionário para guardar as cores escolhidas pelos jogadores
        self.player_colors = {}

        # Temas padrão para o sorteio
        self.theme_deck = [
            "O que você levaria para um apocalipse zumbi?",
            "Profissões mais difíceis ou estressantes",
            "Coisas que dão muito medo",
            "Animais mais perigosos do mundo",
            "Melhores comidas para comer no final de semana",
            "Piores presentes para se ganhar de aniversário",
            "Superpoderes mais úteis na vida real",
            "Melhores invenções da humanidade"         
        ]

    def add_player(self, player_name:str):
        """
        Adiciona um jogador ao jogo, caso o jogo ainda não tenha começado.
        """

        if not self.is_started and player_name not in self.players:
            if not self.available_colors:
                return False  # Não há mais cores disponíveis
            
            self.players[player_name] = None  # O valor None significa que o jogador ainda não recebeu uma carta
           
            # Escolhe uma cor, atribui ao jogador e remove da lista de cores disponíveis
            chosen_color = random.choice(self.available_colors)
            self.available_colors.remove(chosen_color)
            self.player_colors[player_name] = chosen_color

            return True
        return False
    
    def remove_player(self, player_name: str):
        """
        Remove um jogador do jogo e devolve a cor dele para a lista de cores disponíveis.
        """

        # Verifica se o jogador existe no jogo antes de tentar remover
        if player_name in self.players:
            del self.players[player_name]

            # Devolve a cor para a lista de cores disponíveis
            if player_name in self.player_colors:
                freed_color = self.player_colors.pop(player_name)
                self.available_colors.append(freed_color)
    
    def start_round(self):
        """
        Inicia uma nova rodada e sorteia o tema automaticamente.
        """
        if len(self.players) < 2:
            return False, "Faltam jogadores para começar"
        
        self.is_started = True
        self.theme = random.choice(self.theme_deck)
        self.played_cards = []

        # Re-cria e embaralha o deck
        self.deck = list(range(1, 101))
        random.shuffle(self.deck)

        # Distribui uma carta para cada jogador
        for player in self.players:
            self.players[player] = self.deck.pop()

        return True, "Rodada iniciada"

    def get_game_state(self) -> dict:
        """
        Retorna as informações do jogo (sem revelar as cartas dos jogadores).
        """
        return {
            "players": list(self.players.keys()),
            "players_colors": self.player_colors,
            "played_cards": self.played_cards,
            "theme": self.theme,
            "is_started": self.is_started
        } 