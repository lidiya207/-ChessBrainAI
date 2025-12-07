// ===========================
// State Management
// ===========================
const state = {
    currentUser: null,
    currentScreen: 'auth',
    gameMode: null,
    selectedSquare: null,
    legalMoves: [],
    moveHistory: [],
    capturedPieces: { white: [], black: [] },
    boardFlipped: false,
    isAIThinking: false,
    promotionCallback: null
};

// Mock chess board state (8x8 grid)
// This would connect to your Python backend in production
const chessState = {
    board: initializeBoard(),
    turn: 'white',
    lastMove: null,
    isCheck: false,
    isGameOver: false,
    winner: null
};

// ===========================
// Initialization
// ===========================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Check for saved session
    const savedUser = localStorage.getItem('neurochess_user');
    if (savedUser) {
        state.currentUser = savedUser;
        showScreen('menu');
    } else {
        showScreen('auth');
    }

    // Setup event listeners
    setupKeyboardShortcuts();
}

function initializeBoard() {
    // Standard chess starting position
    const board = Array(8).fill(null).map(() => Array(8).fill(null));

    // White pieces (bottom)
    const backRow = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'];
    const pawn = '♟';

    for (let i = 0; i < 8; i++) {
        board[0][i] = backRow[i]; // Black back row
        board[1][i] = pawn;       // Black pawns
        board[6][i] = '♙';        // White pawns
        board[7][i] = backRow[i].replace(/♜|♞|♝|♛|♚/g, match => {
            return { '♜': '♖', '♞': '♘', '♝': '♗', '♛': '♕', '♚': '♔' }[match];
        });
    }

    return board;
}

// ===========================
// Screen Navigation
// ===========================
function showScreen(screenName) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    const screen = document.getElementById(`${screenName}-screen`);
    if (screen) {
        screen.classList.add('active');
        state.currentScreen = screenName;

        // Initialize screen-specific content
        if (screenName === 'menu') {
            updateUserDisplay();
        } else if (screenName === 'game') {
            initializeGameScreen();
        }
    }
}

// ===========================
// Authentication
// ===========================
function showLogin() {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('register-form').classList.remove('active');
    document.getElementById('login-username').focus();
}

function showRegister() {
    document.getElementById('register-form').classList.add('active');
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('reg-username').focus();
}

function handleLogin() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username) {
        showNotification('Please enter a username', 'error');
        return;
    }

    if (!password) {
        showNotification('Please enter a password', 'error');
        return;
    }

    // In production, this would call your Python backend
    // For now, we'll simulate authentication
    const users = JSON.parse(localStorage.getItem('neurochess_users') || '{}');

    if (users[username] && users[username].password === hashPassword(password)) {
        state.currentUser = username;
        localStorage.setItem('neurochess_user', username);
        showNotification(`Welcome back, ${username}!`, 'success');
        showScreen('menu');
    } else {
        showNotification('Invalid username or password', 'error');
    }
}

function handleRegister() {
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;

    if (!username) {
        showNotification('Please enter a username', 'error');
        return;
    }

    if (username.length < 3) {
        showNotification('Username must be at least 3 characters', 'error');
        return;
    }

    if (!password) {
        showNotification('Please enter a password', 'error');
        return;
    }

    if (password.length < 4) {
        showNotification('Password must be at least 4 characters', 'error');
        return;
    }

    if (password !== confirm) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    const users = JSON.parse(localStorage.getItem('neurochess_users') || '{}');

    if (users[username]) {
        showNotification('Username already exists', 'error');
        return;
    }

    users[username] = {
        password: hashPassword(password),
        gamesPlayed: 0,
        wins: 0,
        losses: 0,
        draws: 0,
        created: new Date().toISOString()
    };

    localStorage.setItem('neurochess_users', JSON.stringify(users));
    showNotification('Account created successfully!', 'success');
    showLogin();
}

function playAsGuest() {
    state.currentUser = 'Guest';
    showNotification('Playing as Guest', 'info');
    showScreen('menu');
}

function logout() {
    state.currentUser = null;
    localStorage.removeItem('neurochess_user');
    showNotification('Logged out successfully', 'info');
    showScreen('auth');
    showLogin();
}

function hashPassword(password) {
    // Simple hash for demo - use proper hashing in production
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
        const char = password.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash.toString(36);
}

// ===========================
// Menu Screen
// ===========================
function updateUserDisplay() {
    const usernameDisplay = document.getElementById('username-display');
    const userInitial = document.getElementById('user-initial');
    const userStats = document.getElementById('user-stats');

    if (state.currentUser) {
        usernameDisplay.textContent = state.currentUser;
        userInitial.textContent = state.currentUser[0].toUpperCase();

        const users = JSON.parse(localStorage.getItem('neurochess_users') || '{}');
        const userData = users[state.currentUser];

        if (userData) {
            const { gamesPlayed, wins, losses, draws } = userData;
            userStats.textContent = `${gamesPlayed} games • ${wins}W ${losses}L ${draws}D`;
        } else {
            userStats.textContent = 'Ready to play';
        }
    }
}

function startGame(mode) {
    state.gameMode = mode;
    chessState.board = initializeBoard();
    chessState.turn = 'white';
    chessState.isGameOver = false;
    state.moveHistory = [];
    state.capturedPieces = { white: [], black: [] };
    showScreen('game');
}

function showTraining() {
    showNotification('Training mode coming soon!', 'info');
}

function showStats() {
    showNotification('Statistics view coming soon!', 'info');
}

// ===========================
// Game Screen
// ===========================
function initializeGameScreen() {
    createChessBoard();
    updateGameStatus();
    updateMoveHistory();

    // Set player names
    document.getElementById('player-name').textContent = state.currentUser || 'You';
    document.getElementById('opponent-name').textContent =
        state.gameMode === 'ai' ? 'AI' : 'Player 2';
}

function createChessBoard() {
    const boardElement = document.getElementById('chess-board');
    boardElement.innerHTML = '';

    // Create coordinates
    createCoordinates();

    // Create squares
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = `square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
            square.dataset.row = row;
            square.dataset.col = col;
            square.onclick = () => handleSquareClick(row, col);

            const piece = chessState.board[row][col];
            if (piece) {
                square.textContent = piece;
            }

            boardElement.appendChild(square);
        }
    }
}

function createCoordinates() {
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

    // Top and bottom coordinates
    ['coords-top', 'coords-bottom'].forEach(id => {
        const container = document.getElementById(id);
        container.innerHTML = '';
        files.forEach(file => {
            const span = document.createElement('span');
            span.textContent = file;
            span.style.width = 'calc(min(600px, 80vw) / 8)';
            span.style.textAlign = 'center';
            container.appendChild(span);
        });
    });

    // Left and right coordinates
    ['coords-left', 'coords-right'].forEach(id => {
        const container = document.getElementById(id);
        container.innerHTML = '';
        ranks.forEach(rank => {
            const span = document.createElement('span');
            span.textContent = rank;
            span.style.height = 'calc(min(600px, 80vw) / 8)';
            span.style.display = 'flex';
            span.style.alignItems = 'center';
            container.appendChild(span);
        });
    });
}

function handleSquareClick(row, col) {
    if (chessState.isGameOver) return;

    const clickedSquare = { row, col };

    if (state.selectedSquare) {
        // Try to make a move
        if (isLegalMove(state.selectedSquare, clickedSquare)) {
            makeMove(state.selectedSquare, clickedSquare);
        } else {
            // Select new piece or deselect
            if (state.selectedSquare.row === row && state.selectedSquare.col === col) {
                clearSelection();
            } else {
                selectSquare(row, col);
            }
        }
    } else {
        selectSquare(row, col);
    }
}

// Helper function to check if a piece is white
function isWhitePiece(piece) {
    if (!piece) return false;
    // White pieces: ♔ ♕ ♖ ♗ ♘ ♙ (Unicode 9812-9817)
    // Black pieces: ♚ ♛ ♜ ♝ ♞ ♟ (Unicode 9818-9823)
    const code = piece.charCodeAt(0);
    return code >= 9812 && code <= 9817;
}

function selectSquare(row, col) {
    const piece = chessState.board[row][col];

    if (!piece) {
        clearSelection();
        return;
    }

    // Check if it's the correct turn
    const pieceIsWhite = isWhitePiece(piece);
    const isWhiteTurn = chessState.turn === 'white';

    if (pieceIsWhite !== isWhiteTurn) {
        clearSelection();
        return;
    }

    state.selectedSquare = { row, col };
    state.legalMoves = calculateLegalMoves(row, col);

    updateBoardHighlights();
}

function clearSelection() {
    state.selectedSquare = null;
    state.legalMoves = [];
    updateBoardHighlights();
}

function updateBoardHighlights() {
    const squares = document.querySelectorAll('.square');

    squares.forEach(square => {
        square.classList.remove('selected', 'legal-move', 'last-move', 'check');

        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);

        // Highlight selected square
        if (state.selectedSquare &&
            state.selectedSquare.row === row &&
            state.selectedSquare.col === col) {
            square.classList.add('selected');
        }

        // Highlight legal moves
        if (state.legalMoves.some(move => move.row === row && move.col === col)) {
            square.classList.add('legal-move');
        }

        // Highlight last move
        if (chessState.lastMove) {
            if ((chessState.lastMove.from.row === row && chessState.lastMove.from.col === col) ||
                (chessState.lastMove.to.row === row && chessState.lastMove.to.col === col)) {
                square.classList.add('last-move');
            }
        }

        // Highlight check
        if (chessState.isCheck) {
            const piece = chessState.board[row][col];
            if (piece && (piece === '♔' || piece === '♚')) {
                const isWhiteKing = piece === '♔';
                if ((isWhiteKing && chessState.turn === 'white') ||
                    (!isWhiteKing && chessState.turn === 'black')) {
                    square.classList.add('check');
                }
            }
        }
    });
}

function calculateLegalMoves(row, col) {
    // Simplified legal move calculation for basic gameplay
    const moves = [];
    const piece = chessState.board[row][col];

    if (!piece) return moves;

    const pieceIsWhite = isWhitePiece(piece);
    const pieceSymbol = piece;

    // Pawn moves (♙ white pawn, ♟ black pawn)
    if (pieceSymbol === '♙' || pieceSymbol === '♟') {
        const direction = pieceIsWhite ? -1 : 1; // White moves up (-1), black moves down (+1)
        const startRow = pieceIsWhite ? 6 : 1;

        // Move forward one square
        const newRow = row + direction;
        if (newRow >= 0 && newRow < 8 && !chessState.board[newRow][col]) {
            moves.push({ row: newRow, col });

            // Move forward two squares from starting position
            if (row === startRow) {
                const twoSquaresRow = row + (direction * 2);
                if (!chessState.board[twoSquaresRow][col]) {
                    moves.push({ row: twoSquaresRow, col });
                }
            }
        }

        // Diagonal captures
        [-1, 1].forEach(dc => {
            const newCol = col + dc;
            if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
                const targetPiece = chessState.board[newRow][newCol];
                if (targetPiece && isWhitePiece(piece) !== isWhitePiece(targetPiece)) {
                    moves.push({ row: newRow, col: newCol });
                }
            }
        });
    } else {
        // For other pieces, show moves in all directions (simplified)
        const directions = [
            [-1, 0], [1, 0], [0, -1], [0, 1],
            [-1, -1], [-1, 1], [1, -1], [1, 1]
        ];

        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;

            if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
                const targetPiece = chessState.board[newRow][newCol];
                if (!targetPiece || (isWhitePiece(piece) !== isWhitePiece(targetPiece))) {
                    moves.push({ row: newRow, col: newCol });
                }
            }
        });
    }

    return moves;
}

function isOpponentPiece(piece1, piece2) {
    return isWhitePiece(piece1) !== isWhitePiece(piece2);
}

function isLegalMove(from, to) {
    return state.legalMoves.some(move =>
        move.row === to.row && move.col === to.col
    );
}

function makeMove(from, to) {
    const piece = chessState.board[from.row][from.col];
    const capturedPiece = chessState.board[to.row][to.col];

    // Handle capture
    if (capturedPiece) {
        const isWhiteCaptured = isWhitePiece(capturedPiece);
        const captureList = isWhiteCaptured ? 'white' : 'black';
        state.capturedPieces[captureList].push(capturedPiece);
        updateCapturedPieces();
    }

    // Move piece
    chessState.board[to.row][to.col] = piece;
    chessState.board[from.row][from.col] = null;

    // Record move
    const moveNotation = getMoveNotation(from, to, piece, capturedPiece);
    state.moveHistory.push({
        from,
        to,
        piece,
        captured: capturedPiece,
        notation: moveNotation
    });

    chessState.lastMove = { from, to };

    // Switch turn
    chessState.turn = chessState.turn === 'white' ? 'black' : 'white';

    // Update display
    clearSelection();
    createChessBoard();
    updateGameStatus();
    updateMoveHistory();

    // Check for game over
    checkGameOver();

    // AI move if needed
    if (state.gameMode === 'ai' && chessState.turn === 'black' && !chessState.isGameOver) {
        setTimeout(makeAIMove, 1000);
    }
}

function getMoveNotation(from, to, piece, captured) {
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

    const fromSquare = files[from.col] + ranks[from.row];
    const toSquare = files[to.col] + ranks[to.row];

    return captured ? `${fromSquare}x${toSquare}` : `${fromSquare}-${toSquare}`;
}

function updateGameStatus() {
    const statusText = document.getElementById('game-status');
    const turnIndicator = document.getElementById('turn-indicator');

    if (chessState.isGameOver) {
        if (chessState.winner) {
            statusText.textContent = `${chessState.winner} wins!`;
            turnIndicator.style.background = chessState.winner === 'White' ?
                'var(--success)' : 'var(--danger)';
        } else {
            statusText.textContent = 'Draw';
            turnIndicator.style.background = 'var(--text-muted)';
        }
    } else {
        const turn = chessState.turn === 'white' ? 'White' : 'Black';
        statusText.textContent = `${turn} to move`;
        turnIndicator.style.background = chessState.turn === 'white' ?
            'var(--success)' : 'var(--primary)';
    }
}

function updateMoveHistory() {
    const historyElement = document.getElementById('move-history');

    if (state.moveHistory.length === 0) {
        historyElement.innerHTML = '<p class="empty-state">No moves yet</p>';
        return;
    }

    let html = '';
    for (let i = 0; i < state.moveHistory.length; i += 2) {
        const moveNum = Math.floor(i / 2) + 1;
        const whiteMove = state.moveHistory[i]?.notation || '';
        const blackMove = state.moveHistory[i + 1]?.notation || '';

        html += `
            <div class="move-pair">
                <span class="move-number">${moveNum}.</span>
                <span class="move">${whiteMove}</span>
                ${blackMove ? `<span class="move">${blackMove}</span>` : ''}
            </div>
        `;
    }

    historyElement.innerHTML = html;
    historyElement.scrollTop = historyElement.scrollHeight;
}

function updateCapturedPieces() {
    document.getElementById('captured-white').textContent =
        state.capturedPieces.white.join(' ');
    document.getElementById('captured-black').textContent =
        state.capturedPieces.black.join(' ');
}

function checkGameOver() {
    // Simplified game over detection
    // In production, use your chess engine
    const hasWhiteKing = chessState.board.some(row => row.includes('♔'));
    const hasBlackKing = chessState.board.some(row => row.includes('♚'));

    if (!hasWhiteKing) {
        endGame('Black');
    } else if (!hasBlackKing) {
        endGame('White');
    }
}

function endGame(winner) {
    chessState.isGameOver = true;
    chessState.winner = winner;

    updateGameStatus();

    // Show game over modal
    setTimeout(() => {
        showGameOverModal(winner);
    }, 500);

    // Update user stats
    if (state.currentUser && state.currentUser !== 'Guest') {
        updateUserStats(winner);
    }
}

function showGameOverModal(winner) {
    const modal = document.getElementById('game-over-modal');
    const title = document.getElementById('game-over-title');
    const message = document.getElementById('game-over-message');
    const trophy = document.getElementById('trophy-icon');

    if (winner) {
        title.textContent = 'Game Over';
        message.textContent = `${winner} wins!`;
        trophy.textContent = '🏆';
    } else {
        title.textContent = 'Game Over';
        message.textContent = "It's a draw!";
        trophy.textContent = '🤝';
    }

    modal.classList.add('active');
}

function updateUserStats(winner) {
    const users = JSON.parse(localStorage.getItem('neurochess_users') || '{}');
    const userData = users[state.currentUser];

    if (userData) {
        userData.gamesPlayed++;

        if (winner === 'White') {
            userData.wins++;
        } else if (winner === 'Black') {
            userData.losses++;
        } else {
            userData.draws++;
        }

        localStorage.setItem('neurochess_users', JSON.stringify(users));
    }
}

// ===========================
// Game Controls
// ===========================
function undoMove() {
    if (state.moveHistory.length === 0) {
        showNotification('No moves to undo', 'info');
        return;
    }

    const lastMove = state.moveHistory.pop();

    // Restore piece
    chessState.board[lastMove.from.row][lastMove.from.col] = lastMove.piece;
    chessState.board[lastMove.to.row][lastMove.to.col] = lastMove.captured;

    // Restore captured piece
    if (lastMove.captured) {
        const isWhiteCaptured = lastMove.captured === lastMove.captured.toUpperCase();
        const captureList = isWhiteCaptured ? 'white' : 'black';
        state.capturedPieces[captureList].pop();
        updateCapturedPieces();
    }

    // Switch turn back
    chessState.turn = chessState.turn === 'white' ? 'black' : 'white';

    // Update last move
    const previousMove = state.moveHistory[state.moveHistory.length - 1];
    chessState.lastMove = previousMove ? { from: previousMove.from, to: previousMove.to } : null;

    clearSelection();
    createChessBoard();
    updateGameStatus();
    updateMoveHistory();

    showNotification('Move undone', 'info');
}

function flipBoard() {
    state.boardFlipped = !state.boardFlipped;
    // Reverse the board array
    chessState.board.reverse();
    chessState.board.forEach(row => row.reverse());

    createChessBoard();
    showNotification('Board flipped', 'info');
}

function newGame() {
    // Close modals
    document.getElementById('game-over-modal').classList.remove('active');

    // Reset state
    chessState.board = initializeBoard();
    chessState.turn = 'white';
    chessState.isGameOver = false;
    chessState.winner = null;
    chessState.lastMove = null;
    chessState.isCheck = false;

    state.selectedSquare = null;
    state.legalMoves = [];
    state.moveHistory = [];
    state.capturedPieces = { white: [], black: [] };

    createChessBoard();
    updateGameStatus();
    updateMoveHistory();
    updateCapturedPieces();

    showNotification('New game started', 'success');
}

function backToMenu() {
    // Close modals
    document.getElementById('game-over-modal').classList.remove('active');
    showScreen('menu');
}

function requestAIMove() {
    if (state.gameMode !== 'ai') {
        showNotification('AI move only available in AI mode', 'info');
        return;
    }

    if (chessState.turn !== 'black') {
        showNotification("It's not AI's turn", 'info');
        return;
    }

    makeAIMove();
}

function makeAIMove() {
    if (state.isAIThinking) return;

    state.isAIThinking = true;
    document.getElementById('ai-thinking').style.display = 'block';

    // Simulate AI thinking
    setTimeout(() => {
        // Find a random legal move
        const aiMoves = [];

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = chessState.board[row][col];
                if (piece && piece !== piece.toUpperCase()) {
                    const moves = calculateLegalMoves(row, col);
                    moves.forEach(move => {
                        aiMoves.push({ from: { row, col }, to: move });
                    });
                }
            }
        }

        if (aiMoves.length > 0) {
            const randomMove = aiMoves[Math.floor(Math.random() * aiMoves.length)];
            state.selectedSquare = randomMove.from;
            state.legalMoves = [randomMove.to];
            makeMove(randomMove.from, randomMove.to);
        }

        state.isAIThinking = false;
        document.getElementById('ai-thinking').style.display = 'none';
    }, 1500);
}

// ===========================
// Notifications
// ===========================
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// ===========================
// Keyboard Shortcuts
// ===========================
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (state.currentScreen === 'game') {
            if (e.key === 'u' || e.key === 'U') {
                undoMove();
            } else if (e.key === 'f' || e.key === 'F') {
                flipBoard();
            } else if (e.key === 'n' || e.key === 'N') {
                newGame();
            } else if (e.key === 'Escape') {
                backToMenu();
            }
        }
    });
}

// ===========================
// Promotion Dialog
// ===========================
function selectPromotion(piece) {
    if (state.promotionCallback) {
        state.promotionCallback(piece);
        state.promotionCallback = null;
    }
    document.getElementById('promotion-dialog').classList.remove('active');
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});
