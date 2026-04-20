# =============================================================================
# TAIGA OS — controllers/daily_log.py
# Registro diário de hábitos + cálculo de médias semanais.
#
# Sistema de XP do Daily Log:
#   Cada hora de estudo/trabalho  → +100 XP
#   Rotina completa (todos itens) → +50 XP de bônus
#   Hidratação ≥ 2L               → +10 XP
#   Sono ≥ 7h                     → +10 XP
# =============================================================================

from datetime import date, timedelta
from database import get_conn
from controllers.gamification import adicionar_xp


def registrar_habitos(
    humor: str,
    agua_litros: float,
    sono_horas: float,
    horas_estudo: float,
    rotina_completa: bool,
) -> str:
    """
    Salva (ou atualiza) o log do dia atual e distribui XP.

    Usa INSERT OR REPLACE para que o usuário possa atualizar o log
    do mesmo dia sem criar duplicatas (a coluna `data` é UNIQUE).

    Retorna uma string de feedback para exibir na UI.
    """
    conn = get_conn()
    hoje = date.today().isoformat()

    conn.execute(
        """
        INSERT INTO daily_log
            (data, humor, agua_litros, sono_horas, horas_estudo, rotina_completa)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(data) DO UPDATE SET
            humor           = excluded.humor,
            agua_litros     = excluded.agua_litros,
            sono_horas      = excluded.sono_horas,
            horas_estudo    = excluded.horas_estudo,
            rotina_completa = excluded.rotina_completa
        """,
        (hoje, humor, agua_litros, sono_horas, horas_estudo, int(rotina_completa)),
    )
    conn.commit()

    # --- Calcula e distribui XP ---
    xp_ganho = 0

    # Horas de estudo/trabalho.
    xp_horas = int(horas_estudo) * 100
    xp_ganho += xp_horas

    # Bônus por rotina completa.
    if rotina_completa:
        xp_ganho += 50

    # Bônus de hidratação.
    if agua_litros >= 2.0:
        xp_ganho += 10

    # Bônus de sono.
    if sono_horas >= 7.0:
        xp_ganho += 10

    if xp_ganho > 0:
        novo_xp = adicionar_xp(xp_ganho)
        return f"✅ Log salvo! +{xp_ganho} XP ganhos. Total: {novo_xp:,} XP"
    else:
        return "✅ Log salvo! Registre horas de estudo para ganhar XP."


def obter_log_hoje() -> dict | None:
    """
    Retorna o log de hoje como dicionário, ou None se ainda não foi registrado.

    Usado no DailyLogView para pré-preencher os campos caso o usuário
    já tenha registrado o dia.
    """
    conn = get_conn()
    hoje = date.today().isoformat()
    row  = conn.execute(
        "SELECT * FROM daily_log WHERE data = ?", (hoje,)
    ).fetchone()

    if not row:
        return None

    return {
        "humor":         row["humor"],
        "agua_litros":   row["agua_litros"],
        "sono_horas":    row["sono_horas"],
        "horas_estudo":  row["horas_estudo"],
        "rotina_completa": bool(row["rotina_completa"]),
    }


def obter_media_semanal() -> dict:
    """
    Calcula as médias dos últimos 7 dias para exibição no Dashboard.

    Retorna:
        agua        → média diária de litros de água (arredondado 1 casa)
        sono        → média diária de horas de sono (arredondado 1 casa)
        total_estudo → soma total de horas de estudo na semana (arredondado 1 casa)
    """
    conn = get_conn()
    sete_dias_atras = (date.today() - timedelta(days=7)).isoformat()

    rows = conn.execute(
        """
        SELECT agua_litros, sono_horas, horas_estudo
        FROM daily_log
        WHERE data >= ?
        """,
        (sete_dias_atras,)
    ).fetchall()

    if not rows:
        return {"agua": 0.0, "sono": 0.0, "total_estudo": 0.0}

    n = len(rows)
    total_agua   = sum(r["agua_litros"]  for r in rows)
    total_sono   = sum(r["sono_horas"]   for r in rows)
    total_estudo = sum(r["horas_estudo"] for r in rows)

    return {
        "agua":         round(total_agua / n, 1),
        "sono":         round(total_sono / n, 1),
        "total_estudo": round(total_estudo, 1),   # Soma total, não média.
    }
