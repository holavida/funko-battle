from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from web3 import Web3
import json
import random

# Cargar variables de entorno solo en desarrollo
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
if os.environ.get('RENDER'):
    # Configuración para Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
else:
    # Configuración local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///funko_battle.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-123')

db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    funko_coins = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Funko(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    level = db.Column(db.Integer, default=1)
    power = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Battle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    funko_coins_reward = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas para servir archivos estáticos
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# API Routes
@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.session.add(user)
        db.session.commit()
    
    return jsonify({
        'id': user.id,
        'funko_coins': user.funko_coins,
        'level': user.level
    })

@app.route('/api/mystery-box', methods=['POST'])
def open_mystery_box():
    data = request.json
    user_id = data.get('user_id')
    box_type = data.get('box_type')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Verificar si el usuario tiene suficientes monedas
    costs = {
        'common': 100,
        'rare': 250,
        'legendary': 500
    }
    
    if user.funko_coins < costs[box_type]:
        return jsonify({'error': 'Monedas insuficientes'}), 400
    
    # Generar Funko aleatorio
    funko = generate_random_funko(box_type)
    user.funko_coins -= costs[box_type]
    
    new_funko = Funko(
        user_id=user_id,
        type=funko['type'],
        rarity=funko['rarity'],
        power=funko['power']
    )
    
    db.session.add(new_funko)
    db.session.commit()
    
    return jsonify({
        'funko': {
            'id': new_funko.id,
            'type': new_funko.type,
            'rarity': new_funko.rarity,
            'power': new_funko.power,
            'level': new_funko.level
        },
        'user_coins': user.funko_coins
    })

@app.route('/api/battle/start', methods=['POST'])
def start_battle():
    data = request.json
    user_id = data.get('user_id')
    funko_id = data.get('funko_id')
    
    # Generar oponente AI
    opponent = generate_ai_opponent()
    
    battle = Battle(
        player1_id=user_id,
        player2_id=0,  # 0 representa AI
        funko_coins_reward=random.randint(50, 200)
    )
    
    db.session.add(battle)
    db.session.commit()
    
    return jsonify({
        'battle_id': battle.id,
        'opponent': opponent,
        'reward': battle.funko_coins_reward
    })

@app.route('/api/exchange', methods=['POST'])
def exchange_coins():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    crypto_type = data.get('crypto_type')
    
    user = User.query.get(user_id)
    if not user or user.funko_coins < amount:
        return jsonify({'error': 'Monedas insuficientes'}), 400
    
    # Simular tasas de cambio
    rates = {
        'btc': 0.0000001,
        'eth': 0.000001
    }
    
    crypto_amount = amount * rates[crypto_type]
    user.funko_coins -= amount
    db.session.commit()
    
    return jsonify({
        'success': True,
        'crypto_amount': crypto_amount,
        'remaining_coins': user.funko_coins
    })

# Funciones auxiliares
def generate_random_funko(box_type):
    funko_types = ['Pop', 'Deluxe', 'Exclusive', 'Chase', 'Limited']
    rarity_pools = {
        'common': ['common', 'rare'],
        'rare': ['rare', 'epic'],
        'legendary': ['epic', 'legendary']
    }
    
    rarity = random.choice(rarity_pools[box_type])
    power_ranges = {
        'common': (10, 20),
        'rare': (20, 35),
        'epic': (35, 50),
        'legendary': (50, 75)
    }
    
    return {
        'type': random.choice(funko_types),
        'rarity': rarity,
        'power': random.randint(*power_ranges[rarity])
    }

def generate_ai_opponent():
    return {
        'name': f'AI Opponent #{random.randint(1000, 9999)}',
        'funko': generate_random_funko('rare')
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
