import random
import cv2
import mediapipe as mp
import numpy as np
import base64

# --- Game Logic ---
class Game:
    def __init__(self):
        self.user_score = 0
        self.computer_score = 0
        self.tie_score = 0
        self.rounds = 1
        self.history = []
        self.computer_streak = 0
        self.user_streak = 0
        self.repetitive_count = 0
        self.last_move = None
        self.avatar = "rusty" # Default avatar
        
        self.avatars = {
            "rusty": {
                "name": "Rusty",
                "catchphrase": "Let's see if you can handle the pro!",
                "win": ["Calculated. 📈", "Too easy! Try harder next time.", "My algorithms are superior.", "Victory is logical."],
                "loss": ["An anomaly in my data...", "Wait, that wasn't supposed to happen.", "Nice move... for a human.", "I need a reboot after that one."],
                "tie": ["A statistical stalemate.", "We are perfectly matched.", "Interesting choice.", "Back to square one."],
                "advice": ["You're leaning on {move} too much. Predictable.", "My sensors detect a pattern. Shake it up!", "High probability you'll lose if you keep this up."]
            },
            "zappy": {
                "name": "Zappy",
                "catchphrase": "Ready to get zapped by my awesome moves?",
                "win": ["BOOM! Roasted! 🔥", "ZAP! Gotcha!", "I'm on fire today!", "Can't touch this! ⚡"],
                "loss": ["Ouch! That hurt!", "Hey! No fair!", "You got lucky that time!", "I'm still the coolest though! 😎"],
                "tie": ["Copycat! 🐈", "Stop reading my mind!", "Let's go again, double time!", "Twin powers, activate!"],
                "advice": ["Boring! Try something new!", "You're acting like a robot! Oh wait, that's me!", "Mix it up or I'll zap you!"]
            },
            "luna": {
                "name": "Luna",
                "catchphrase": "May the flow of the game guide us.",
                "win": ["The tides have turned in my favor.", "Balance is restored.", "A graceful victory.", "Walk in peace, but I won."],
                "loss": ["A lesson in humility for me.", "You have found your center.", "The universe smiles upon you.", "Well played, traveler."],
                "tie": ["We are one with the game.", "Harmonious result.", "Peaceful coexistence.", "Energy in equilibrium."],
                "advice": ["Seek the path less traveled.", "Your spirit is repetitive.", "Let go of your attachment to {move}."]
            }
        }
        
        # Init Gesture (static_image_mode=True for separate frame requests)
        self.mp_hands = None
        try:
            import mediapipe as mp
            # Try different ways to access solutions in case of weird installation
            mp_hands_module = None
            if hasattr(mp, 'solutions'):
                mp_hands_module = mp.solutions.hands
            else:
                # Fallback if solutions is missing but module exists
                try:
                    import mediapipe.python.solutions.hands as mp_hands_module
                except:
                    pass
            
            if mp_hands_module:
                self.mp_hands = mp_hands_module.Hands(
                    static_image_mode=True,
                    max_num_hands=1, 
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("Mediapipe hands initialized successfully via solution mapping.")
            else:
                print("Mediapipe module found but 'solutions' attribute is missing. Gesture mode will be limited.")
        except Exception as e:
            print(f"Mediapipe Initialization Error: {e}")
            self.mp_hands = None

        self.input_mode = "1"
        self.difficulty = "easy"


    def reset_stats(self):
        self.user_score = 0
        self.computer_score = 0
        self.tie_score = 0
        self.rounds = 1
        self.history = []
        self.computer_streak = 0
        self.user_streak = 0
        self.repetitive_count = 0
        self.last_move = None

    def get_ai_choice(self):
        choices = ["snake", "water", "gun"]
        
        if self.difficulty == "easy":
            return random.choice(choices)
        
        if self.difficulty == "medium" and random.random() < 0.6:
            return random.choice(choices)
            
        if self.difficulty == "hard":
            if random.random() < 0.3: # Random factor
                 return random.choice(choices)
            # Prediction logic
            if self.history:
                predicted = max(set(self.history), key=self.history.count)
                # Counter the predicted user move
                return {"snake": "gun", "water": "snake", "gun": "water"}[predicted]
                
        return random.choice(choices)

    def play_round(self, user_choice):
        computer_choice = self.get_ai_choice()
        self.history.append(user_choice)
        
        winner = "computer"
        message = ""
        
        if user_choice == computer_choice:
            winner = "tie"
            self.tie_score += 1
            self.user_streak = 0
            self.computer_streak = 0
            message = "It's a tie! 🤝"
        elif (user_choice == "snake" and computer_choice == "water") or \
             (user_choice == "water" and computer_choice == "gun") or \
             (user_choice == "gun" and computer_choice == "snake"):
            winner = "user"
            self.user_score += 1
            self.user_streak += 1
            self.computer_streak = 0
            message = "You won! 🥳"
        else:
            winner = "computer"
            self.computer_score += 1
            self.computer_streak += 1
            self.user_streak = 0
            message = "Computer won! 🤖"

        self.rounds += 1
        
        return {
            "winner": winner,
            "computer_choice": computer_choice,
            "user_choice": user_choice,
            "message": message,
            "scores": {
                "user": self.user_score,
                "computer": self.computer_score,
                "tie": self.tie_score,
                "rounds": self.rounds
            },
            "coach_advice": self.get_coach_advice(user_choice),
            "commentary": self.get_commentary(winner),
            "avatar_name": self.avatars[self.avatar]["name"]
        }

    def get_coach_advice(self, user_choice):
        if user_choice == self.last_move:
            self.repetitive_count += 1
        else:
            self.repetitive_count = 0
        self.last_move = user_choice

        personality = self.avatars[self.avatar]
        
        if self.repetitive_count >= 2:
            return random.choice(personality["advice"]).replace("{move}", user_choice)
        
        if self.computer_streak >= 3:
            return f"I'm winning too much! Maybe try {random.choice(['snake', 'water', 'gun'])}?"
            
        return "Keep going! You're doing great."

    def get_commentary(self, winner):
        personality = self.avatars[self.avatar]
        if winner == "user": return random.choice(personality["loss"])
        if winner == "computer": return random.choice(personality["win"])
        return random.choice(personality["tie"])


    def process_gesture_frame(self, image_data_base64):
        """
        Expects base64 encoded image string.
        Returns: "snake", "water", "gun", "detected" (if just hand is seen), or None
        """
        try:
            if "," in image_data_base64:
                image_data_base64 = image_data_base64.split(",")[1]
            
            nparr = np.frombuffer(base64.b64decode(image_data_base64), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None or self.mp_hands is None:
                return None

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.mp_hands.process(rgb)

            if result.multi_hand_landmarks:
                # We saw a hand! 
                hand_landmarks = result.multi_hand_landmarks[0]
                
                # --- Improved Finger Counting Logic ---
                # tips of 4 fingers: Index (8), Middle (12), Ring (16), Pinky (20)
                # joints: 6, 10, 14, 18 (PIP joints)
                tips = [8, 12, 16, 20]
                folded = 0
                
                # We use the distance from the wrist (0) or MCP joint to be more robust
                # but simple Y comparison is okay if we use the PIP joint as reference.
                for i in range(4):
                    tip = hand_landmarks.landmark[tips[i]]
                    pip = hand_landmarks.landmark[tips[i] - 2]
                    
                    # If tip.y > pip.y, the finger is folded (Y increases downwards)
                    if tip.y > pip.y:
                        folded += 1
                
                # Thumb logic: Thumb tip (4) vs Thumb MCP (2)
                # Comparing X coordinates (after flip)
                thumb_tip = hand_landmarks.landmark[4]
                thumb_mcp = hand_landmarks.landmark[2]
                thumb_folded = False
                if abs(thumb_tip.x - hand_landmarks.landmark[17].x) < abs(thumb_mcp.x - hand_landmarks.landmark[17].x):
                    thumb_folded = True
                
                # Final Gesture Logic
                if folded == 4:
                    return "gun"      # Fist
                elif folded == 0:
                    return "water"    # Open Palm
                elif folded == 2:
                    # Specifically Index and Middle fingers up
                    index_folded = hand_landmarks.landmark[8].y > hand_landmarks.landmark[6].y
                    middle_folded = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y
                    ring_folded = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
                    pinky_folded = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
                    
                    if not index_folded and not middle_folded and ring_folded and pinky_folded:
                        return "snake" # V-Sign
                    return "detected" # 2 fingers, but maybe not V-sign
                
                return "detected" # Hand seen but no clear gesture
                
            return None
        except Exception as e:
            print(f"Gesture Error: {e}")
            return None

# Singleton or session usage? For Flask, best to keep session state in Flask session or a global dict keyed by session ID.
# For simplicity, we can use a single global game instance if it's single user, 
# but for a web app it's better to store state.
