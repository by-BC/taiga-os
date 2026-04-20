# =============================================================================
# TAIGA OS — database.py
# Camada de acesso ao banco de dados SQLite.
#
# Por que SQLite?
#   - Zero configuração: o banco é um arquivo local (.db)
#   - Nativo do Python (módulo `sqlite3`)
#   - Perfeito para apps desktop de uso pessoal
#
# Estrutura:
#   get_conn()   → retorna uma conexão reutilizável
#   init_db()    → cria as tabelas se ainda não existirem
# =============================================================================

import sqlite3
import os
from pathlib import Path

# Caminho do banco — fica na raiz do projeto.
DB_PATH = Path(__file__).parent / "taiga_os.db"

# Conexão global reutilizada durante a sessão.
_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    """
    Retorna a conexão SQLite singleton.
    Cria a conexão (e o banco) na primeira chamada.

    `check_same_thread=False` é necessário para CustomTkinter,
    que pode chamar callbacks em threads diferentes.
    """
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        # Retorna linhas como dicionários (row["coluna"] em vez de row[0]).
        _conn.row_factory = sqlite3.Row
        # Ativa suporte a chaves estrangeiras.
        _conn.execute("PRAGMA foreign_keys = ON")
        init_db(_conn)
    return _conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Cria todas as tabelas do sistema caso não existam.
    Chamado automaticamente na primeira conexão.
    """
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # USUÁRIO — dados de gamificação (apenas 1 registro)
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id           INTEGER PRIMARY KEY DEFAULT 1,
            xp           INTEGER DEFAULT 0,
            streak       INTEGER DEFAULT 0,
            ultimo_login TEXT    DEFAULT ''
        )
    """)

    # Garante que o registro do usuário existe.
    cursor.execute("INSERT OR IGNORE INTO usuario (id) VALUES (1)")

    # ------------------------------------------------------------------
    # TAREFAS — Kanban + Dashboard
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT    NOT NULL,
            categoria   TEXT    DEFAULT 'Estudos',
            data_limite TEXT,
            status      TEXT    DEFAULT 'A Fazer',
            descricao   TEXT    DEFAULT '',
            criado_em   TEXT    DEFAULT (date('now'))
        )
    """)

    # ------------------------------------------------------------------
    # DAILY LOG — registro diário de hábitos
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            data             TEXT    UNIQUE DEFAULT (date('now')),
            humor            TEXT    DEFAULT '',
            agua_litros      REAL    DEFAULT 0,
            sono_horas       REAL    DEFAULT 0,
            horas_estudo     REAL    DEFAULT 0,
            rotina_completa  INTEGER DEFAULT 0
        )
    """)

    # ------------------------------------------------------------------
    # CURSOS — Academic Hub
    # ------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cursos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT    NOT NULL,
            instituicao      TEXT    DEFAULT '',
            total_aulas      INTEGER DEFAULT 0,
            aulas_concluidas INTEGER DEFAULT 0,
            categoria        TEXT    DEFAULT 'Estudos',
            github           TEXT    DEFAULT '',
            doc              TEXT    DEFAULT '',
            concluido        INTEGER DEFAULT 0,
            criado_em        TEXT    DEFAULT (date('now'))
        )
    """)

    conn.commit()
