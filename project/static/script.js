let currentMode = '1';
let currentDifficulty = 'easy';
let currentAvatar = 'rusty';
let webcamStream = null;
let gestureInterval = null;

function selectMode(mode, btn) {
    currentMode = mode;
    document.querySelectorAll('.mode-select .btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function selectDifficulty(diff, btn) {
    currentDifficulty = diff;
    document.querySelectorAll('.difficulty-select .btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function selectAvatar(avatar, el) {
    currentAvatar = avatar;
    document.querySelectorAll('.avatar-card').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
}

async function startGame() {
    const startBtn = document.querySelector('.start-btn');
    const originalText = startBtn.innerText;
    startBtn.innerText = "ENTERING...";
    startBtn.disabled = true;

    try {
        const response = await fetch('/api/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input_mode: currentMode,
                difficulty: currentDifficulty,
                avatar: currentAvatar
            })
        });

        if (!response.ok) throw new Error("Failed to configure game");

        const data = await response.json();

        // Update Opponent UI
        document.getElementById('opponent-name').innerText = data.avatar_name;
        document.getElementById('coach-name').innerText = `${data.avatar_name.toUpperCase()}'S THOUGHTS`;
        document.getElementById('opponent-avatar-icon').innerText = getAvatarIcon(currentAvatar);
        document.getElementById('commentary-text').innerText = data.catchphrase;

        document.getElementById('setup-screen').classList.add('hidden');
        document.getElementById('game-screen').classList.remove('hidden');
        resetUI();

        if (currentMode === '2') {
            document.getElementById('keyboard-controls').classList.add('hidden');
            document.getElementById('camera-container').classList.remove('hidden');
            startCamera();
        } else {
            document.getElementById('keyboard-controls').classList.remove('hidden');
            document.getElementById('camera-container').classList.add('hidden');
            stopCamera();
        }
    } catch (err) {
        console.error("Game Start Error:", err);
        alert("Oops! The arena is temporarily closed (Server Error). Please try again or check the console.");
    } finally {
        startBtn.innerText = originalText;
        startBtn.disabled = false;
    }
}


function getAvatarIcon(avatar) {
    const icons = { 'rusty': '🤖', 'zappy': '⚡', 'luna': '🌙' };
    return icons[avatar] || '🤖';
}

function resetGame() {
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('setup-screen').classList.remove('hidden');
    stopCamera();
}

function resetUI() {
    document.getElementById('score-user').innerText = '0';
    document.getElementById('score-computer').innerText = '0';
    document.getElementById('round-val').innerText = '1';
    document.getElementById('result-msg').innerText = 'Ready?';
    // Keep catchphrase if it's the first round, otherwise generic
    if (document.getElementById('round-val').innerText == '1') {
        // Catchphrase already set in startGame
    } else {
        document.getElementById('commentary-text').innerText = 'Ready for another?';
    }
    document.getElementById('coach-text').innerText = 'Watch the patterns...';
    document.getElementById('player-anim').innerText = '❔';
    document.getElementById('computer-anim').innerText = '❔';

    // Clear animations
    document.getElementById('player-anim').className = 'player-side';
    document.getElementById('computer-anim').className = 'computer-side';
}

async function playMove(move) {
    const pAnim = document.getElementById('player-anim');
    const cAnim = document.getElementById('computer-anim');
    const overlay = document.getElementById('countdown-overlay');
    const countNum = document.getElementById('countdown-number');

    // Start Countdown
    overlay.classList.remove('hidden');

    const count = async (num) => {
        countNum.innerText = num;
        await new Promise(r => setTimeout(r, 600));
    };

    await count("3");
    await count("2");
    await count("1");
    await count("GO!");

    overlay.classList.add('hidden');

    // Reset animations
    pAnim.className = 'player-side';
    cAnim.className = 'computer-side';

    // Fetch result while showing "GO!" or just after
    const response = await fetch('/api/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: move })
    });

    const data = await response.json();

    // Simultaneous Reveal
    pAnim.innerText = getEmoji(move);
    cAnim.innerText = getEmoji(data.computer_choice);

    document.getElementById('result-msg').innerText = data.message;
    document.getElementById('commentary-text').innerText = data.commentary;
    document.getElementById('coach-text').innerText = data.coach_advice;

    document.getElementById('score-user').innerText = data.scores.user;
    document.getElementById('score-computer').innerText = data.scores.computer;
    document.getElementById('round-val').innerText = data.scores.rounds;

    // Apply animations
    if (data.winner === 'user') {
        pAnim.classList.add('win-anim');
        cAnim.classList.add('lose-anim');
    } else if (data.winner === 'computer') {
        cAnim.classList.add('win-anim');
        pAnim.classList.add('lose-anim');
    }
}


function getEmoji(choice) {
    if (choice === 'snake') return '🐍';
    if (choice === 'water') return '💧';
    if (choice === 'gun') return '🔫';
    return '❔';
}

// --- Camera Logic ---
async function startCamera() {
    const video = document.getElementById('webcam');
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = webcamStream;
        gestureInterval = setInterval(processGesture, 1000);
    } catch (err) {
        console.error("Camera error: ", err);
        document.getElementById('gesture-detected').innerText = "Camera access denied.";
    }
}

function stopCamera() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    if (gestureInterval) clearInterval(gestureInterval);
}

let stableGesture = null;
let gestureCount = 0;

async function processGesture() {
    const video = document.getElementById('webcam');
    if (!video || !video.videoWidth) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg', 0.4);

    try {
        const response = await fetch('/api/gesture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        const gesture = data.gesture;

        const statusEl = document.getElementById('gesture-detected');

        if (gesture) {
            if (gesture === 'detected') {
                statusEl.innerText = "Hand Detected. Form a gesture!";
                statusEl.style.color = 'var(--accent)';
                stableGesture = null;
                gestureCount = 0;
                return;
            }

            if (gesture === stableGesture) {
                gestureCount++;
            } else {
                stableGesture = gesture;
                gestureCount = 1;
            }

            if (gestureCount >= 2) {
                statusEl.innerText = `LOCKED: ${gesture.toUpperCase()}!`;
                statusEl.style.color = 'var(--secondary)';

                clearInterval(gestureInterval);
                stableGesture = null;
                gestureCount = 0;

                await playMove(gesture);

                setTimeout(() => {
                    statusEl.innerText = "Scanning...";
                    statusEl.style.color = '';
                    if (currentMode === '2' && !document.getElementById('game-screen').classList.contains('hidden')) {
                        gestureInterval = setInterval(processGesture, 800);
                    }
                }, 2500);
            } else {
                statusEl.innerText = `Detecting... ${gesture.toUpperCase()}`;
                statusEl.style.color = 'var(--warning)';
            }
        } else {
            stableGesture = null;
            gestureCount = 0;
            statusEl.innerText = "Scanning...";
            statusEl.style.color = '';
        }
    } catch (err) {
        console.error("Gesture processing error:", err);
    }
}
