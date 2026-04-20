import sqlite3

DB_PATH = 'taiga_data.db'

def iniciar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp_total INTEGER DEFAULT 0, nivel_atual TEXT DEFAULT 'Estagiário', streak_atual INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_logs (data TEXT PRIMARY KEY, humor TEXT, agua_litros REAL, sono_horas REAL, horas_estudo REAL, rotina_concluida BOOLEAN)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, titulo TEXT, categoria TEXT, data_limite TEXT, status TEXT DEFAULT 'A Fazer', cor_hex TEXT)''')
    
    # --- NOVA TABELA: CURSOS E PROJETOS ACADÊMICOS ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        instituicao TEXT,
        total_aulas INTEGER,
        aulas_concluidas INTEGER DEFAULT 0,
        categoria TEXT,
        github TEXT,
        doc TEXT,
        status TEXT DEFAULT 'Em Andamento',
        data_inicio TEXT
    )''')
    
    # Setup Inicial (Popula dados na primeira vez que rodar)
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_stats (xp_total) VALUES (1000)")
        tarefas = [("Criar artes IRPF 2026 - SILVANA CANDIDO", "Trabalho", "2026-04-25", "A Fazer", "#E6A15A"),("Estudar Auditoria de Sistemas", "Estudos", "2026-04-21", "A Fazer", "#4E6B50")]
        cursor.executemany("INSERT INTO tasks (titulo, categoria, data_limite, status, cor_hex) VALUES (?, ?, ?, ?, ?)", tarefas)
    
    conn.commit()
    conn.close()