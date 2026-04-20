#!/usr/bin/env python3
"""
Shared Database Module - Singleton Connection, Caching, Indexes
==============================================================
"""

import sqlite3
import threading
import time
import json
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
from typing import Optional, List, Dict, Any

DB_MAIN = '/home/node/.openclaw/workspace/data/james.db'
DB_QUESTIONS = '/home/node/.openclaw/workspace/skills/ap1-training-tracker/data/questions.db'


class CacheEntry:
    __slots__ = ('data', 'timestamp', 'ttl')
    
    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class DatabaseCache:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._cache[key]
                return None
            return entry.data
    
    def set(self, key: str, value: Any, ttl: int):
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
    
    def invalidate(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()


_stats_cache = DatabaseCache()
_question_cache = DatabaseCache()
STATS_CACHE_TTL = 300
QUESTION_CACHE_TTL = 3600


class SingletonConnection:
    _instances: Dict[str, 'SingletonConnection'] = {}
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str) -> 'SingletonConnection':
        with cls._lock:
            if db_path not in cls._instances:
                cls._instances[db_path] = super().__new__(cls)
                cls._instances[db_path]._initialized = False
            return cls._instances[db_path]
    
    def __init__(self, db_path: str):
        if self._initialized:
            return
        self._db_path = db_path
        self._local = threading.local()
        self._initialized = True
        self._ensure_indexes()
    
    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA busy_timeout=5000")
        return self._local.conn
    
    @contextmanager
    def get_cursor(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = ()):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor
        finally:
            cursor.close()
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def _ensure_indexes(self):
        with self.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            existing = {row[0] for row in cursor.fetchall()}
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_attempts_timestamp ON learning_attempts(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_attempts_correct ON learning_attempts(correct)",
                "CREATE INDEX IF NOT EXISTS idx_attempts_session ON learning_attempts(session_date)",
                "CREATE INDEX IF NOT EXISTS idx_attempts_question ON learning_attempts(question_id)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_date ON learning_sessions(session_date)",
                "CREATE INDEX IF NOT EXISTS idx_questions_id ON questions(id)",
                "CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category)",
            ]
            
            for idx_sql in indexes:
                idx_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ")[0]
                if idx_name not in existing:
                    try:
                        cursor.execute(idx_sql)
                    except sqlite3.Error:
                        pass


_main_db = SingletonConnection(DB_MAIN)
_questions_db = SingletonConnection(DB_QUESTIONS)


def get_main_db() -> SingletonConnection:
    return _main_db


def get_questions_db() -> SingletonConnection:
    return _questions_db


def cached_stats(ttl: int = STATS_CACHE_TTL):
    def decorator(func):
        cache_key = f"stats_{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            cached = _stats_cache.get(cache_key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            _stats_cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_stats_cache():
    _stats_cache.clear()


def invalidate_question_cache():
    _question_cache.clear()


def init_main_db():
    db = get_main_db()
    with db.get_cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_attempts (
            id INTEGER PRIMARY KEY,
            question_id TEXT,
            user_answer TEXT,
            correct INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_date DATE
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_sessions (
            session_date DATE PRIMARY KEY,
            questions_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            percentage REAL DEFAULT 0,
            topics TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_questions (
            id TEXT PRIMARY KEY,
            category TEXT,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            last_shown TIMESTAMP
        )''')


def get_random_questions_efficient(count: int = 3) -> List[Dict]:
    """
    Efficient random question selection using random offset.
    Avoids ORDER BY RANDOM() which scans entire table.
    """
    import random
    db = get_questions_db()
    
    total = db.fetchone("SELECT COUNT(*) FROM questions")[0]
    
    if total == 0:
        return []
    
    selected_ids = set()
    questions = []
    attempts = 0
    max_attempts = count * 10
    
    while len(questions) < count and attempts < max_attempts and len(selected_ids) < total:
        attempts += 1
        offset = random.randrange(total)
        
        if selected_ids:
            placeholders = ','.join('?' * len(selected_ids))
            row = db.fetchone(
                f"""SELECT * FROM questions WHERE id NOT IN ({placeholders}) LIMIT 1 OFFSET ?""",
                (*selected_ids, offset)
            )
        else:
            row = db.fetchone("SELECT * FROM questions LIMIT 1 OFFSET ?", (offset,))
        
        if row and row['id'] not in selected_ids:
            selected_ids.add(row['id'])
            questions.append({
                'id': row['id'],
                'question': row['question'],
                'options': json.loads(row['options']),
                'correct': row['correct'],
                'explanation': row['explanation'],
                'category': row['category'],
                'difficulty': row['difficulty']
            })
    
    return questions


def save_attempt(question_id: str, user_answer: str, is_correct: bool, category: str = ""):
    from datetime import date
    today = date.today().isoformat()
    db = get_main_db()
    
    with db.get_cursor() as cursor:
        cursor.execute('''
            INSERT INTO learning_attempts 
            (question_id, user_answer, correct, timestamp, session_date)
            VALUES (?, ?, ?, datetime('now'), ?)
        ''', (question_id, user_answer, 1 if is_correct else 0, today))
        
        cursor.execute('''
            INSERT INTO learning_questions 
            (id, category, total_attempts, correct_attempts, last_shown)
            VALUES (?, ?, 1, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                total_attempts = total_attempts + 1,
                correct_attempts = correct_attempts + ?,
                last_shown = datetime('now')
        ''', (question_id, category, 1 if is_correct else 0, 1 if is_correct else 0))
    
    invalidate_stats_cache()


@cached_stats(STATS_CACHE_TTL)
def get_weekly_stats() -> Dict:
    db = get_main_db()
    
    row = db.fetchone('''
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(correct), 0) as correct
        FROM learning_attempts 
        WHERE timestamp >= date('now', '-7 days')
    ''')
    
    total = row['total'] or 0
    correct = row['correct'] or 0
    
    days = db.fetchall('''
        SELECT 
            date(timestamp) as day,
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE timestamp >= date('now', '-7 days')
        GROUP BY date(timestamp)
        ORDER BY day ASC
    ''')
    
    topics = db.fetchall('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(la.correct) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        WHERE la.timestamp >= date('now', '-7 days')
        GROUP BY lq.category
    ''')
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'days': [(d['day'], d['total'], d['correct']) for d in days],
        'topics': [(t['category'], t['attempts'], t['correct']) for t in topics]
    }


@cached_stats(STATS_CACHE_TTL)
def get_monthly_stats(year: int = None, month: int = None) -> Dict:
    from datetime import datetime
    
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    month_str = f"{year}-{month:02d}"
    db = get_main_db()
    
    row = db.fetchone('''
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(correct), 0) as correct
        FROM learning_attempts 
        WHERE strftime('%Y-%m', timestamp) = ?
    ''', (month_str,))
    
    total = row['total'] or 0
    correct = row['correct'] or 0
    
    days = db.fetchall('''
        SELECT 
            date(timestamp) as day,
            COUNT(*) as total,
            SUM(correct) as correct
        FROM learning_attempts 
        WHERE strftime('%Y-%m', timestamp) = ?
        GROUP BY date(timestamp)
        ORDER BY day ASC
    ''', (month_str,))
    
    topics = db.fetchall('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(la.correct) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        WHERE strftime('%Y-%m', la.timestamp) = ?
        GROUP BY lq.category
    ''', (month_str,))
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'days': [(d['day'], d['total'], d['correct']) for d in days],
        'topics': [(t['category'], t['attempts'], t['correct']) for t in topics],
        'month': month_str
    }


@cached_stats(STATS_CACHE_TTL)
def get_all_time_stats() -> Dict:
    db = get_main_db()
    
    row = db.fetchone('''
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(correct), 0) as correct
        FROM learning_attempts
    ''')
    
    total = row['total'] or 0
    correct = row['correct'] or 0
    
    topics = db.fetchall('''
        SELECT 
            lq.category,
            COUNT(*) as attempts,
            SUM(la.correct) as correct
        FROM learning_attempts la
        JOIN learning_questions lq ON la.question_id = lq.id
        GROUP BY lq.category
    ''')
    
    days_row = db.fetchone('''
        SELECT COUNT(DISTINCT date(timestamp)) FROM learning_attempts
    ''')
    learning_days = days_row[0] if days_row else 0
    
    return {
        'total': total,
        'correct': correct,
        'wrong': total - correct,
        'percentage': round(100 * correct / total, 1) if total > 0 else 0,
        'topics': [(t['category'], t['attempts'], t['correct']) for t in topics],
        'learning_days': learning_days
    }
