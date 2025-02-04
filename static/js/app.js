// Inicialización de Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// Estado del juego
let gameState = {
    funkoCoins: 0,
    playerLevel: 1,
    collection: [],
    currentBattle: null
};

// Elementos DOM
const navButtons = document.querySelectorAll('.nav-btn');
const sections = document.querySelectorAll('.game-section');
const funkoCollection = document.getElementById('funkoCollection');
const findBattleBtn = document.getElementById('findBattle');
const exchangeBtn = document.getElementById('exchangeBtn');

// Navegación
navButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetSection = button.dataset.section;
        
        // Actualizar botones activos
        navButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Mostrar sección correspondiente
        sections.forEach(section => {
            section.classList.remove('active');
            if (section.id === targetSection) {
                section.classList.add('active');
            }
        });
    });
});

// Funciones de la tienda
function buyMysteryBox(tier) {
    const prices = {
        common: 100,
        rare: 250,
        legendary: 500
    };

    if (gameState.funkoCoins >= prices[tier]) {
        gameState.funkoCoins -= prices[tier];
        updateCoins();
        openMysteryBox(tier);
    } else {
        showNotification('No tienes suficientes FunkoCoins!');
    }
}

function openMysteryBox(tier) {
    const rarities = {
        common: ['common', 'rare'],
        rare: ['rare', 'epic'],
        legendary: ['epic', 'legendary']
    };

    const funko = generateRandomFunko(rarities[tier]);
    gameState.collection.push(funko);
    showFunkoReveal(funko);
    updateCollection();
}

// Sistema de batalla
function initiateBattle() {
    if (!gameState.collection.length) {
        showNotification('Necesitas al menos un Funko para batallar!');
        return;
    }

    const opponent = generateOpponent();
    gameState.currentBattle = {
        player: selectBestFunko(),
        opponent: opponent,
        round: 0
    };

    showBattleScene();
}

function selectBestFunko() {
    return gameState.collection.reduce((best, current) => 
        current.power > best.power ? current : best
    );
}

function battleRound() {
    const battle = gameState.currentBattle;
    const playerDamage = calculateDamage(battle.player);
    const opponentDamage = calculateDamage(battle.opponent);

    animateBattleRound(playerDamage, opponentDamage);

    battle.opponent.health -= playerDamage;
    battle.player.health -= opponentDamage;

    if (battle.opponent.health <= 0) {
        endBattle('win');
    } else if (battle.player.health <= 0) {
        endBattle('lose');
    } else {
        battle.round++;
        updateBattleUI();
    }
}

// Sistema de intercambio de criptomonedas
function initializeExchange() {
    const exchangeAmount = document.getElementById('exchangeAmount').value;
    const selectedCrypto = document.getElementById('cryptoSelect').value;
    
    if (exchangeAmount > gameState.funkoCoins) {
        showNotification('No tienes suficientes FunkoCoins!');
        return;
    }

    // Simular tasa de cambio
    const rates = {
        btc: 0.0000001,
        eth: 0.000001
    };

    const cryptoAmount = exchangeAmount * rates[selectedCrypto];
    showExchangeConfirmation(exchangeAmount, cryptoAmount, selectedCrypto);
}

// Utilidades
function showNotification(message) {
    // Integración con la API de Telegram para mostrar notificaciones nativas
    tg.showPopup({
        title: 'Funko Battle',
        message: message
    });
}

function updateCoins() {
    document.getElementById('funkoCoins').textContent = `FunkoCoins: ${gameState.funkoCoins}`;
}

function generateRandomFunko(rarityPool) {
    const funkoTypes = ['Pop', 'Deluxe', 'Exclusive', 'Chase', 'Limited'];
    const type = funkoTypes[Math.floor(Math.random() * funkoTypes.length)];
    const rarity = rarityPool[Math.floor(Math.random() * rarityPool.length)];
    
    return {
        id: Date.now(),
        type: type,
        rarity: rarity,
        level: 1,
        power: calculateBasePower(rarity),
        health: 100
    };
}

function calculateBasePower(rarity) {
    const powerLevels = {
        common: 10,
        rare: 20,
        epic: 35,
        legendary: 50
    };
    return powerLevels[rarity];
}

// Animaciones
function animateBattleRound(playerDamage, opponentDamage) {
    const playerFunko = document.querySelector('.player-funko');
    const opponentFunko = document.querySelector('.opponent-funko');

    playerFunko.classList.add('attack-animation');
    setTimeout(() => {
        opponentFunko.classList.add('attack-animation');
        playerFunko.classList.remove('attack-animation');
    }, 500);
    setTimeout(() => {
        opponentFunko.classList.remove('attack-animation');
    }, 1000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar la colección con algunos Funkos de prueba
    gameState.collection = [
        generateRandomFunko(['common']),
        generateRandomFunko(['rare'])
    ];
    updateCollection();
    
    // Event listeners para la tienda
    document.querySelectorAll('.mystery-box').forEach(box => {
        box.addEventListener('click', () => {
            buyMysteryBox(box.dataset.tier);
        });
    });

    // Event listener para batalla
    findBattleBtn.addEventListener('click', initiateBattle);

    // Event listener para intercambio
    exchangeBtn.addEventListener('click', initializeExchange);
});

// Actualizar la colección en la UI
function updateCollection() {
    funkoCollection.innerHTML = '';
    gameState.collection.forEach(funko => {
        const funkoCard = document.createElement('div');
        funkoCard.className = 'funko-card';
        funkoCard.innerHTML = `
            <h3>${funko.type}</h3>
            <p>Rareza: ${funko.rarity}</p>
            <p>Nivel: ${funko.level}</p>
            <p>Poder: ${funko.power}</p>
        `;
        funkoCollection.appendChild(funkoCard);
    });
}
