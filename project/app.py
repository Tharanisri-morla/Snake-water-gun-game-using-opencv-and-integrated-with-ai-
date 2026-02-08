from flask import Flask, render_template, request, jsonify, session
import uuid
from game_logic import Game

app = Flask(__name__)
app.secret_key = "super_secret_snake_key_replace_in_prod"

# Store game instances. 
# Session ID -> Game()
games = {}

def get_game(create=False):
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    sid = session['session_id']
    if sid not in games or create:
        games[sid] = Game()
    return games[sid]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/configure', methods=['POST'])
def configure_game():
    data = request.json
    game = get_game(create=True) # Reset/Create on configure
    
    # Set settings
    game.difficulty = data.get('difficulty', 'easy')
    game.input_mode = data.get('input_mode', '1') # 1=Keyboard, 2=Gesture
    game.avatar = data.get('avatar', 'rusty')
    game.reset_stats()
    
    return jsonify({
        "status": "ok", 
        "message": "Game configured", 
        "difficulty": game.difficulty,
        "avatar": game.avatar,
        "avatar_name": game.avatars[game.avatar]["name"],
        "catchphrase": game.avatars[game.avatar]["catchphrase"]
    })


@app.route('/api/play', methods=['POST'])
def play_round():
    game = get_game()
    data = request.json
    user_move = data.get('move')
    
    if not user_move:
        return jsonify({"error": "No move provided"}), 400
        
    result = game.play_round(user_move)
    return jsonify(result)

@app.route('/api/gesture', methods=['POST'])
def detect_gesture():
    game = get_game()
    data = request.json
    image_data = data.get('image') # Base64 string
    
    if not image_data:
        return jsonify({"error": "No image provided"}), 400
        
    detected = game.process_gesture_frame(image_data)
    # Return detected gesture or null
    return jsonify({"gesture": detected})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    game = get_game()
    return jsonify({
        "user_score": game.user_score,
        "computer_score": game.computer_score,
        "tie_score": game.tie_score,
        "rounds": game.rounds,
        "user_streak": game.user_streak,
        "computer_streak": game.computer_streak
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
