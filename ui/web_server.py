"""
Web server for NeuroChess UI
Serves the modern web interface and provides API endpoints for the chess engine
"""

import os
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Try to import the chess engine components
try:
    from engine.game import ChessGame
    from engine.mcts import MCTS
    from engine.neural_net import ChessNet
    import torch
    import chess
    CHESS_ENGINE_AVAILABLE = True
except ImportError:
    CHESS_ENGINE_AVAILABLE = False
    print("Warning: Chess engine not available. Running in demo mode.")


class NeuroChessHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for NeuroChess web interface"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = str(Path(__file__).parent / 'web')
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Serve the main page
        if parsed_path.path == '/' or parsed_path.path == '':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for API endpoints"""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        # API endpoints
        if parsed_path.path == '/api/ai-move':
            self.handle_ai_move(data)
        elif parsed_path.path == '/api/validate-move':
            self.handle_validate_move(data)
        elif parsed_path.path == '/api/new-game':
            self.handle_new_game(data)
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_ai_move(self, data):
        """Get AI move using MCTS"""
        if not CHESS_ENGINE_AVAILABLE:
            # Return a random legal move in demo mode
            response = {
                'success': True,
                'move': {'from': {'row': 1, 'col': 0}, 'to': {'row': 3, 'col': 0}},
                'demo': True
            }
            self.send_json_response(response)
            return
        
        try:
            # Get board state from request
            board_fen = data.get('board', chess.STARTING_FEN)
            
            # Create game and MCTS
            game = ChessGame()
            game.board = chess.Board(board_fen)
            
            # Load model if available
            model = None
            device = 'cpu'
            
            # Try to load the latest checkpoint
            checkpoint_dir = Path(__file__).parent.parent / 'models' / 'checkpoints'
            if checkpoint_dir.exists():
                checkpoints = list(checkpoint_dir.glob('*.pth'))
                if checkpoints:
                    latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
                    model = ChessNet()
                    model.load_state_dict(torch.load(latest_checkpoint, map_location=device))
                    model.eval()
            
            if model is None:
                model = ChessNet()
            
            # Get AI move
            mcts = MCTS(model, device=device, temperature=0.1)
            move, _ = mcts.search(game)
            
            if move:
                response = {
                    'success': True,
                    'move': {
                        'from': {'row': 7 - (move.from_square // 8), 'col': move.from_square % 8},
                        'to': {'row': 7 - (move.to_square // 8), 'col': move.to_square % 8},
                        'uci': move.uci()
                    }
                }
            else:
                response = {'success': False, 'error': 'No legal moves available'}
            
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def handle_validate_move(self, data):
        """Validate if a move is legal"""
        if not CHESS_ENGINE_AVAILABLE:
            # In demo mode, accept all moves
            self.send_json_response({'success': True, 'legal': True, 'demo': True})
            return
        
        try:
            board_fen = data.get('board', chess.STARTING_FEN)
            move_uci = data.get('move')
            
            board = chess.Board(board_fen)
            move = chess.Move.from_uci(move_uci)
            
            is_legal = move in board.legal_moves
            
            response = {
                'success': True,
                'legal': is_legal,
                'check': board.is_check() if is_legal else False,
                'checkmate': board.is_checkmate() if is_legal else False,
                'stalemate': board.is_stalemate() if is_legal else False
            }
            
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def handle_new_game(self, data):
        """Start a new game"""
        response = {
            'success': True,
            'board': chess.STARTING_FEN if CHESS_ENGINE_AVAILABLE else None
        }
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[NeuroChess] {format % args}")


def run_server(port=8000, host='localhost'):
    """Run the web server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, NeuroChessHandler)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                    NeuroChess Web UI                      ║
╚═══════════════════════════════════════════════════════════╝

🚀 Server running at: http://{host}:{port}
🎮 Open this URL in your browser to play!

{'✅ Chess engine: ACTIVE' if CHESS_ENGINE_AVAILABLE else '⚠️  Chess engine: DEMO MODE (install requirements.txt)'}

Press Ctrl+C to stop the server
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for playing!")
        httpd.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='NeuroChess Web Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to')
    
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
