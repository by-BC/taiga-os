# =============================================================================
# TAIGA OS — controllers/gamification.py
# Lógica de gamificação: XP, níveis e streak.
#
# Sistema de níveis baseado no tema florestal do Taiga OS:
#
#   Nível        │ XP mínimo │ Cor
#   ─────────────┼───────────┼──────────
#   🌱 Semente   │         0 │ #7A9E7A
#   🌿 Broto     │       500 │ #4E6B50
#   🌳 Árvore    │     1.500 │ #3D6050
#   🌲 Floresta  │     3.500 │ #2F4F3E
#   🏔️ Montanha  │     7.000 │ #7A6AAE
#   ⭐ Guardião  │    12.000 │ #E6A15A
# =============================================================================

from datetime import date
from database import get_conn


# ------------------------------------------------------------------
# TABELA DE NÍVEIS
# Cada tupla: (xp_mínimo, nome_do_nível, cor_hex)
# ------------------------------------------------------------------
NIVEIS = [
    (0,      "🌱 Semente",  "#7A9E7A"),
    (500,    "🌿 Broto",    "#4E6B50"),
    (1500,   "🌳 Árvore",   "#3D6050"),
    (3500,   "🌲 Floresta", "#2F4F3E"),
    (7000,   "🏔️ Montanha", "#7A6AAE"),
    (12000,  "⭐ Guardião", "#E6A15A"),
]


def _calcular_nivel(xp: int) -> dict:
    """
    Dado o XP total, retorna um dicionário com as informações de nível.

    Percorre a tabela de níveis de trás para frente para encontrar
    o nível atual (o maior cujo xp_mínimo é <= xp do usuário).
    """
    nivel_atual_idx = 0
    for i, (xp_min, _, _) in enumerate(NIVEIS):
        if xp >= xp_min:
            nivel_atual_idx = i

    xp_min_atual, nome_atual, cor_atual = NIVEIS[nivel_atual_idx]

    # Próximo nível (ou "Máximo" se já for o último).
    if nivel_atual_idx < len(NIVEIS) - 1:
        xp_min_prox, nome_prox, _ = NIVEIS[nivel_atual_idx + 1]
        xp_necessario = xp_min_prox - xp_min_atual
        xp_no_nivel   = xp - xp_min_atual
    else:
        nome_prox     = "Máximo atingido"
        xp_necessario = 1          # Evita divisão por zero.
        xp_no_nivel   = xp - xp_min_atual

    return {
        "nivel":        nome_atual,
        "cor_nivel":    cor_atual,
        "proximo_nivel": nome_prox,
        "xp_no_nivel":  xp_no_nivel,
        "xp_necessario": xp_necessario,
    }


def obter_status_usuario() -> dict:
    """
    Retorna todos os dados de gamificação do usuário para exibição na UI.

    Retorno esperado pelas views:
        xp, streak, nivel, cor_nivel,
        proximo_nivel, xp_no_nivel, xp_necessario
    """
    conn = get_conn()
    row  = conn.execute("SELECT xp, streak FROM usuario WHERE id = 1").fetchone()

    xp     = row["xp"]
    streak = row["streak"]

    info_nivel = _calcular_nivel(xp)

    return {
        "xp":     xp,
        "streak": streak,
        **info_nivel,   # Desempacota os campos de nível no mesmo dict.
    }


def adicionar_xp(quantidade: int) -> int:
    """
    Adiciona XP ao usuário e retorna o novo total.
    Chamado pelos outros controllers ao completar ações.
    """
    conn = get_conn()
    conn.execute("UPDATE usuario SET xp = xp + ? WHERE id = 1", (quantidade,))
    conn.commit()
    novo_xp = conn.execute("SELECT xp FROM usuario WHERE id = 1").fetchone()["xp"]
    return novo_xp


def verificar_e_atualizar_streak() -> None:
    """
    Verifica se o usuário abriu o app hoje e atualiza o streak.

    Regras:
      - Se último login foi ontem → streak + 1
      - Se último login foi hoje  → não altera (já contou)
      - Se último login foi antes de ontem → reseta para 1
      - Se nunca logou → inicia streak em 1

    Chamado no __init__ do TaigaApp (main_window.py).
    """
    conn  = get_conn()
    row   = conn.execute("SELECT streak, ultimo_login FROM usuario WHERE id = 1").fetchone()

    hoje   = date.today().isoformat()          # Ex: "2025-01-15"
    ultimo = row["ultimo_login"] or ""
    streak = row["streak"]

    if ultimo == hoje:
        # Já contou hoje, não faz nada.
        return

    if ultimo == _dia_anterior(hoje):
        # Logou ontem: incrementa streak.
        streak += 1
    else:
        # Perdeu a sequência ou primeiro login.
        streak = 1

    conn.execute(
        "UPDATE usuario SET streak = ?, ultimo_login = ? WHERE id = 1",
        (streak, hoje)
    )
    conn.commit()


def _dia_anterior(data_iso: str) -> str:
    """Retorna a data do dia anterior no formato ISO (YYYY-MM-DD)."""
    from datetime import datetime, timedelta
    d = datetime.strptime(data_iso, "%Y-%m-%d")
    return (d - timedelta(days=1)).strftime("%Y-%m-%d")
