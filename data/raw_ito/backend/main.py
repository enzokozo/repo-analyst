import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .game_logic import ItoGame

# Inicializa a aplicação
app = FastAPI(title = "Servidor Ito")

# Instância do jogo
game = ItoGame()

# Classe quem está conectado no jogo
class ConnectionManager:
    def __init__(self):
        # Guarda o nome do jogador associado à sua conexão 
        self.active_connections: dict[str, WebSocket] = {}
    
    # Adiciona um jogador à lista de conexões ativas
    async def connect(self, websocket: WebSocket, player_name: str):
        await websocket.accept()
        self.active_connections[player_name] = websocket
        game.add_player(player_name)
    
    # Remove a conexão de um jogador
    def disconnect(self, player_name : str):
        if player_name in self.active_connections:
            del self.active_connections[player_name]
            game.remove_player(player_name)

    # Envia mensagem para um jogador específico
    async def send_personal_message(self, message: dict, player_name: str):
        websocket = self.active_connections.get(player_name)
        if websocket:
            await websocket.send_json(message)

    # Envia uma mensagem para todos os jogadores conectados
    async def broadcast(self, message: dict):
        disconnected = []
        for player_name, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Conexão foi fechada, marca para remover
                disconnected.append(player_name)
        
        # Remove conexões que foram fechadas
        for player_name in disconnected:
            self.disconnect(player_name)

manager = ConnectionManager()

# Função auxiliar para disparar as atualizações do jogo para todos os jogadores 
async def broadcast_game_state():
    state = game.get_game_state()

    # Avisa quem está jogando e o tema
    await manager.broadcast({"type": "game_state", "data": state})

    # Se o jogo começou, mostra a carta para cada um
    if game.is_started:
        for player_name in game.players:
            secret_card = game.players[player_name]
            await manager.send_personal_message(
                {"type": "secret_card", "card": secret_card},
                player_name
            )

# Rota do WebSocket para os jogadores se conectarem
@app.websocket("/ws/{player_name}")
async def websocket_endpoint(websocket: WebSocket, player_name: str):
    await manager.connect(websocket, player_name)

    await manager.broadcast({"type": "chat", "message": f"{player_name} entrou no jogo"})
    await broadcast_game_state()

    try:
        # Fica escutando qualquer ação do jogador infinitamente
        while True:
            # Recebe o texto do navegador
            data = await websocket.receive_text()
            
            # Converte o texto para um dicionário python
            parsed_data = json.loads(data)

            # Se a ação for um chat
            if parsed_data["action"] == "chat":
                await manager.broadcast({"type": "chat", "message": f"{player_name}: {parsed_data['message']}"})

            # Se a ação for o botão de Iniciar o jogo:
            elif parsed_data["action"] == "start_game":
                success, msg = game.start_round()

                await manager.broadcast({"type": "chat", "message": msg})
                if success:
                    await broadcast_game_state()
        
    except WebSocketDisconnect:
        manager.disconnect(player_name)
        await manager.broadcast({"type": "chat", "message": f"{player_name} saiu do jogo"})
        await broadcast_game_state()