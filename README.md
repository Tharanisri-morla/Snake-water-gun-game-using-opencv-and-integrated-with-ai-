# Snake-water-gun-game-using-opencv-and-integrated-with-ai-<br>
The Snake Water Gun Game (AI & Hand Gesture Recognition) is an Interactive Snake, Water, and Gun game that lets you compete against the computer using actual hand gestures seen in real-time through a webcam with OpenCV (and optionally with MediaPipe).This project merges traditional gaming logic with AI technology to create a game that is both fun to play as well as a futuristic experience.<br>
Project Overview:~<br>

This project includes an upgrade from the common Snake-Water-Gun Game.

The user makes the moves by using their hands.

The computer randomly generates the computer's moves.

The game uses the usual rules to determine who wins.

The computer uses a webcam feed to detect the user's hand motion in real time.

The game has a smooth and interactive user interface.<br>
Match Rules:~<br>
Player's Pick Computer's Pick Result Snake , Water , Snake wins Water , Gun , Water wins Gun , Snake , Gun wins Two players choose same thing Two players choose same thing Draw Specifications

Realtime gesture detection via webcam
Live view of webcam using Opencv
Computer generated move (random logic)
Computer announces winner based on rules
Accumulate scores (if desired)
Browser UI (Flask with HTML templates)
Very well written / modular code base (app.py/game.logic.py)<br>
Tech Stack Used:~<br>
Python

OpenCV

Flask

HTML / CSS

MediaPipe (if used for hand detection)

NumPy<br>
Project Structure:~<br>
project/
│── app.py
│── game_logic.py
│── requirements.txt
│── templates/
│── static/
│── Procfile
