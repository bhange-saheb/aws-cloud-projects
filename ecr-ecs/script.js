const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreElement = document.getElementById("score");
const highScoreElement = document.getElementById("highScore");
const speedElement = document.getElementById("speed");

const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");

const startScreen = document.getElementById("startScreen");
const gameOverScreen = document.getElementById("gameOverScreen");
const pauseScreen = document.getElementById("pauseScreen");

const finalScore = document.getElementById("finalScore");

const startButton = document.getElementById("startButton");
const restartButton = document.getElementById("restartButton");
const pauseButton = document.getElementById("pauseButton");
const restartGameButton = document.getElementById("restartGameButton");
const resumeButton = document.getElementById("resumeButton");

const GRID_SIZE = 30;
const CELL_SIZE = canvas.width / GRID_SIZE;

let snake;
let food;

let direction;
let nextDirection;

let score = 0;
let highScore = Number(localStorage.getItem("ankitSnakeHighScore")) || 0;

let gameRunning = false;
let paused = false;

let gameSpeed = 120;
let gameTimer = null;

highScoreElement.textContent = highScore;


/*
    Initialize game
*/

function initializeGame() {

    snake = [
        { x: 15, y: 15 },
        { x: 14, y: 15 },
        { x: 13, y: 15 },
        { x: 12, y: 15 }
    ];

    direction = {
        x: 1,
        y: 0
    };

    nextDirection = {
        x: 1,
        y: 0
    };

    score = 0;

    gameSpeed = 120;

    updateScore();

    generateFood();

    drawGame();
}


/*
    Start game
*/

function startGame() {

    initializeGame();

    startScreen.classList.add("hidden");
    gameOverScreen.classList.add("hidden");
    pauseScreen.classList.add("hidden");

    gameRunning = true;
    paused = false;

    updateStatus("PLAYING");

    startLoop();
}


/*
    Game loop
*/

function startLoop() {

    clearInterval(gameTimer);

    gameTimer = setInterval(() => {

        if (!gameRunning || paused) {
            return;
        }

        updateGame();
        drawGame();

    }, gameSpeed);
}


/*
    Update game
*/

function updateGame() {

    direction = nextDirection;

    const head = {
        x: snake[0].x + direction.x,
        y: snake[0].y + direction.y
    };

    /*
        Wall collision
    */

    if (
        head.x < 0 ||
        head.x >= GRID_SIZE ||
        head.y < 0 ||
        head.y >= GRID_SIZE
    ) {

        endGame();

        return;
    }

    /*
        Self collision
    */

    if (snake.some(segment =>
        segment.x === head.x &&
        segment.y === head.y
    )) {

        endGame();

        return;
    }

    snake.unshift(head);

    /*
        Food collision
    */

    if (
        head.x === food.x &&
        head.y === food.y
    ) {

        score += 10;

        increaseSpeed();

        generateFood();

        updateScore();

    } else {

        snake.pop();
    }
}


/*
    Generate food
*/

function generateFood() {

    let validPosition = false;

    while (!validPosition) {

        food = {
            x: Math.floor(Math.random() * GRID_SIZE),
            y: Math.floor(Math.random() * GRID_SIZE)
        };

        validPosition = !snake.some(segment =>
            segment.x === food.x &&
            segment.y === food.y
        );
    }
}


/*
    Increase difficulty
*/

function increaseSpeed() {

    if (score >= 100) {
        gameSpeed = 75;
    } else if (score >= 70) {
        gameSpeed = 85;
    } else if (score >= 40) {
        gameSpeed = 100;
    } else {
        gameSpeed = 120;
    }

    const multiplier = (120 / gameSpeed).toFixed(1);

    speedElement.textContent = `${multiplier}x`;

    startLoop();
}


/*
    Draw everything
*/

function drawGame() {

    drawBackground();
    drawGrid();
    drawFood();
    drawSnake();
}


/*
    Background
*/

function drawBackground() {

    ctx.fillStyle = "#02050b";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    /*
        subtle gradient
    */

    const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        canvas.width
    );

    gradient.addColorStop(
        0,
        "rgba(0,255,170,0.025)"
    );

    gradient.addColorStop(
        1,
        "rgba(0,0,0,0)"
    );

    ctx.fillStyle = gradient;

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );
}


/*
    Grid
*/

function drawGrid() {

    ctx.strokeStyle = "rgba(0,255,170,0.035)";
    ctx.lineWidth = 1;

    for (let i = 0; i <= GRID_SIZE; i++) {

        const position = i * CELL_SIZE;

        ctx.beginPath();

        ctx.moveTo(position, 0);
        ctx.lineTo(position, canvas.height);

        ctx.stroke();

        ctx.beginPath();

        ctx.moveTo(0, position);
        ctx.lineTo(canvas.width, position);

        ctx.stroke();
    }
}


/*
    Draw food
*/

function drawFood() {

    const centerX =
        food.x * CELL_SIZE + CELL_SIZE / 2;

    const centerY =
        food.y * CELL_SIZE + CELL_SIZE / 2;

    /*
        Glow
    */

    const glow = ctx.createRadialGradient(
        centerX,
        centerY,
        2,
        centerX,
        centerY,
        CELL_SIZE
    );

    glow.addColorStop(
        0,
        "rgba(255,50,100,0.9)"
    );

    glow.addColorStop(
        1,
        "rgba(255,50,100,0)"
    );

    ctx.fillStyle = glow;

    ctx.beginPath();

    ctx.arc(
        centerX,
        centerY,
        CELL_SIZE,
        0,
        Math.PI * 2
    );

    ctx.fill();

    /*
        Food
    */

    ctx.fillStyle = "#ff3864";

    ctx.shadowColor = "#ff3864";
    ctx.shadowBlur = 18;

    ctx.beginPath();

    ctx.arc(
        centerX,
        centerY,
        CELL_SIZE * 0.28,
        0,
        Math.PI * 2
    );

    ctx.fill();

    ctx.shadowBlur = 0;

    /*
        Highlight
    */

    ctx.fillStyle = "#ffffff";

    ctx.globalAlpha = 0.7;

    ctx.beginPath();

    ctx.arc(
        centerX - 3,
        centerY - 3,
        2,
        0,
        Math.PI * 2
    );

    ctx.fill();

    ctx.globalAlpha = 1;
}


/*
    Draw snake
*/

function drawSnake() {

    snake.forEach((segment, index) => {

        const x =
            segment.x * CELL_SIZE;

        const y =
            segment.y * CELL_SIZE;

        const padding = 2;

        /*
            Head
        */

        if (index === 0) {

            ctx.fillStyle = "#00ffaa";

            ctx.shadowColor = "#00ffaa";
            ctx.shadowBlur = 18;

        } else {

            const gradient = ctx.createLinearGradient(
                x,
                y,
                x + CELL_SIZE,
                y + CELL_SIZE
            );

            gradient.addColorStop(
                0,
                "#00ffaa"
            );

            gradient.addColorStop(
                1,
                "#00aaff"
            );

            ctx.fillStyle = gradient;

            ctx.shadowColor = "#00ffaa";
            ctx.shadowBlur = 8;
        }

        roundRect(
            ctx,
            x + padding,
            y + padding,
            CELL_SIZE - padding * 2,
            CELL_SIZE - padding * 2,
            6
        );

        ctx.fill();

        ctx.shadowBlur = 0;

        /*
            Head eyes
        */

        if (index === 0) {

            drawEyes(
                x,
                y
            );
        }
    });
}


/*
    Draw eyes
*/

function drawEyes(x, y) {

    const eyeSize = 3;

    let eye1X;
    let eye1Y;

    let eye2X;
    let eye2Y;

    if (direction.x === 1) {

        eye1X = x + 19;
        eye1Y = y + 8;

        eye2X = x + 19;
        eye2Y = y + 17;

    } else if (direction.x === -1) {

        eye1X = x + 9;
        eye1Y = y + 8;

        eye2X = x + 9;
        eye2Y = y + 17;

    } else if (direction.y === -1) {

        eye1X = x + 8;
        eye1Y = y + 9;

        eye2X = x + 17;
        eye2Y = y + 9;

    } else {

        eye1X = x + 8;
        eye1Y = y + 19;

        eye2X = x + 17;
        eye2Y = y + 19;
    }

    ctx.fillStyle = "#02100c";

    ctx.beginPath();

    ctx.arc(
        eye1X,
        eye1Y,
        eyeSize,
        0,
        Math.PI * 2
    );

    ctx.fill();

    ctx.beginPath();

    ctx.arc(
        eye2X,
        eye2Y,
        eyeSize,
        0,
        Math.PI * 2
    );

    ctx.fill();
}


/*
    Rounded rectangle helper
*/

function roundRect(
    context,
    x,
    y,
    width,
    height,
    radius
) {

    context.beginPath();

    context.roundRect(
        x,
        y,
        width,
        height,
        radius
    );
}


/*
    Score
*/

function updateScore() {

    scoreElement.textContent = score;

    if (score > highScore) {

        highScore = score;

        localStorage.setItem(
            "ankitSnakeHighScore",
            highScore
        );

        highScoreElement.textContent = highScore;
    }
}


/*
    Game over
*/

function endGame() {

    gameRunning = false;

    clearInterval(gameTimer);

    finalScore.textContent = score;

    gameOverScreen.classList.remove("hidden");

    updateStatus("GAME OVER");

    statusDot.style.background = "#ff3864";

    statusDot.style.boxShadow =
        "0 0 10px #ff3864";
}


/*
    Pause
*/

function togglePause() {

    if (!gameRunning) {
        return;
    }

    paused = !paused;

    if (paused) {

        pauseScreen.classList.remove("hidden");

        pauseButton.textContent = "▶ RESUME";

        updateStatus("PAUSED");

    } else {

        pauseScreen.classList.add("hidden");

        pauseButton.textContent = "⏸ PAUSE";

        updateStatus("PLAYING");
    }
}


/*
    Status
*/

function updateStatus(status) {

    statusText.textContent = status;

    statusDot.style.background = "#00ffaa";

    statusDot.style.boxShadow =
        "0 0 10px #00ffaa";
}


/*
    Keyboard controls
*/

document.addEventListener("keydown", event => {

    const key = event.key.toLowerCase();

    const directions = {

        arrowup: { x: 0, y: -1 },
        w: { x: 0, y: -1 },

        arrowdown: { x: 0, y: 1 },
        s: { x: 0, y: 1 },

        arrowleft: { x: -1, y: 0 },
        a: { x: -1, y: 0 },

        arrowright: { x: 1, y: 0 },
        d: { x: 1, y: 0 }
    };

    /*
        Pause with Space
    */

    if (key === " ") {

        event.preventDefault();

        togglePause();

        return;
    }

    if (!directions[key]) {
        return;
    }

    event.preventDefault();

    const newDirection = directions[key];

    /*
        Prevent reversing
    */

    if (
        newDirection.x === -direction.x &&
        newDirection.y === -direction.y
    ) {
        return;
    }

    nextDirection = newDirection;
});


/*
    Buttons
*/

startButton.addEventListener(
    "click",
    startGame
);

restartButton.addEventListener(
    "click",
    startGame
);

restartGameButton.addEventListener(
    "click",
    startGame
);

pauseButton.addEventListener(
    "click",
    togglePause
);

resumeButton.addEventListener(
    "click",
    togglePause
);


/*
    Initial screen
*/

initializeGame();