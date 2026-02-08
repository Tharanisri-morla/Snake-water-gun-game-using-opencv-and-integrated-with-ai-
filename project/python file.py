# 🔹 What is Snake–Water–Gun?
# Snake–Water–Gun is a simple logical game similar to Rock–Paper–Scissors.
# It is played between:
# User
# Computer
# The computer makes its choice randomly using Python’s random module.
# 🧩 Choices in the Game
# Each player can choose one of the following:
# 🐍 Snake
# 💧 Water
# 🔫 Gun
# If both choose the same, it’s a draw

# Otherwise:
# Snake beats Water
# Water beats Gun
# Gun beats Snake
import random
import time

# Optional: ensure UTF-8 for Windows console
import sys
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Optional imports for gesture mode — fall back to keyboard if unavailable
try:
    import cv2
    import mediapipe as mp
    mp.solutions # Verify solutions is available
    gesture_libs = True
except Exception as e:
    print(f"Warning: Could not import gesture libraries. Error: {e}")
    cv2 = None
    mp = None
    gesture_libs = False


try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ------------------ GLOBAL VARIABLES ------------------
user_score = 0
computer_score = 0
tie = 0
rounds = 1

user_history = []
user_streak = 0
computer_streak = 0


def configure_game_settings():
    # ------------------ INPUT MODE ------------------
    global input_mode
    while True:
        print("\nSelect Input Mode:")
        print("1. Keyboard ⌨️")
        print("2. Camera with Hand Gestures ✋📷")
        mode = input("Enter 1 or 2: ").strip()
        
        if mode in ("1", "2"):
            input_mode = mode
            break
        print("Invalid selection. Please enter 1 or 2.")

    if input_mode == "2" and not gesture_libs:
        print("Gesture mode unavailable (missing OpenCV/MediaPipe). Falling back to keyboard mode.")
        input_mode = "1"

    # ------------------ DIFFICULTY ------------------
    global difficulty
    while True:
        print("\nChoose Difficulty Level:")
        print("1. Easy 😄")
        print("2. Medium 🤖")
        print("3. Hard 😈")
        level = input("Enter 1, 2, or 3: ").strip()
        if level in ("1", "2", "3"):
            difficulty = "easy" if level == "1" else "hard" if level == "3" else "medium"
            break
        print("Invalid selection. Please enter 1, 2, or 3.")

# Initial Configuration
# configure_game_settings() # Called in main loop now


# Logic moved to configure_game_settings

# ------------------ KEYBOARD INPUT ------------------
def get_keyboard_input():
    while True:
        choice = input("Enter snake / water / gun: ").lower().strip()
        if choice in ["snake", "water", "gun"]:
            return choice
        print("Invalid choice. Please type 'snake', 'water', or 'gun'.")

# ------------------ OPENCV HAND GESTURE INPUT ------------------
if gesture_libs:
    mp_hands_module = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_hands = mp_hands_module.Hands(max_num_hands=1)
else:
    mp_hands = None
    mp_draw = None

def detect_gesture():
    if not gesture_libs:
        print("Gesture libraries not available — falling back to keyboard mode.")
        return None

    cap = cv2.VideoCapture(0)
    gesture = None

    print("\nShow Gesture:")
    print("✊ Fist → Gun")
    print("✋ Palm → Water")
    print("✌️ Two fingers → Snake")
    time.sleep(2)

    fail_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            fail_count += 1
            if fail_count > 10:
                print("Camera error: Could not read frames.")
                break
            continue
        fail_count = 0


        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = mp_hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands_module.HAND_CONNECTIONS)

                tips = [8, 12, 16, 20]   # finger tips
                folded = 0

                for tip in tips:
                    if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y:
                        folded += 1

                # Gesture detection rules
                if folded == 4:
                    gesture = "gun"     # fist
                elif folded == 0:
                    gesture = "water"   # open palm
                elif folded == 2:
                    gesture = "snake"   # two fingers

                if gesture:
                    cv2.putText(frame, f"Detected: {gesture.upper()}", (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.putText(frame, "Show Gesture", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Gesture Mode", frame)

        if gesture:
            time.sleep(1)
            break

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return gesture

# ------------------ AI HELPERS ------------------
def computer_ai_choice():
    choices = ["snake", "water", "gun"]

    if difficulty == "easy":
        return random.choice(choices)

    if difficulty == "medium" and random.random() < 0.6:
        return random.choice(choices)

    if difficulty == "hard" and random.random() < 0.3:
        return random.choice(choices)

    if user_history:
        predicted = max(set(user_history), key=user_history.count)
        return {"snake": "gun", "water": "snake", "gun": "water"}[predicted]

    return random.choice(choices)

def ai_coach():
    if len(user_history) >= 2:
        if user_history[-1] == user_history[-2]:
            print("🧠 AI Coach: Try changing your move 😉")
        else:
            print("🧠 AI Coach: Nice variation 👍")

def emotion_reaction():
    if user_streak == 2:
        print("🤖 AI: You're improving 😏")
    elif computer_streak == 2:
        print("🤖 AI: I'm on fire 🔥")

def confidence_meter():
    total = user_score + computer_score + tie
    if total == 0:
        return
    print("\n📊 Confidence Meter")
    print(f"You : {'█' * int((user_score/total)*10):<10}")
    print(f"AI  : {'█' * int((computer_score/total)*10):<10}")

# ------------------ GAME FUNCTION ------------------
def game():
    global user_score, computer_score, tie, rounds
    global user_streak, computer_streak

    print(f"\n--- Round {rounds} ---")
    print("Snake🐍  Water💧  Gun🔫")

    computer_choice = computer_ai_choice()  # LOCKED FIRST

    if input_mode == "1":
        user_choice = get_keyboard_input()
    else:
        user_choice = detect_gesture()

    if user_choice is None:
        if input_mode == "2":
            print("Gesture not detected 😅")
        return

    user_history.append(user_choice)

    print(f"🖥️ Computer chose: {computer_choice}")

    if user_choice == computer_choice:
        print("It's a tie 🤝")
        tie += 1
        user_streak = computer_streak = 0

    elif (user_choice == "snake" and computer_choice == "water") or \
         (user_choice == "water" and computer_choice == "gun") or \
         (user_choice == "gun" and computer_choice == "snake"):
        print("You won 🤩🥳")
        user_score += 1
        user_streak += 1
        computer_streak = 0

    else:
        print("Computer won 🤖😎")
        computer_score += 1
        computer_streak += 1
        user_streak = 0

    emotion_reaction()
    ai_coach()
    confidence_meter()

    rounds += 1
    print(f"\nScore → You: {user_score} | Computer: {computer_score} | Tie: {tie}")

# ------------------ MAIN LOOP ------------------
while True:
    configure_game_settings() # Configure before starting a set of rounds?? 
    # Or just configure once per session? User said "runing from beggining".
    # I'll put it here so they can change mode.
    
    # Reset scores regarding new game session? Maybe.
    user_score = 0
    computer_score = 0
    tie = 0
    rounds = 1
    
    while True: # Inner loop for rounds
        game()
        again = input("\nPlay another round? (yes/no): ").lower()
        if again != "yes":
            break
            
    print("\n🏁 FINAL RESULT")
    print(f"You: {user_score} | Computer: {computer_score} | Tie: {tie}")
    
    restart_game = input("Start a completely new game (change mode)? (yes/no): ").lower()
    if restart_game != "yes":
        print("Game Over 👋")
        break