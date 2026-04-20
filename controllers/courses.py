# =============================================================================
# TAIGA OS — controllers/courses.py
# Gestão de cursos e projetos do Academic Hub.
#
# XP:
#   Concluir um curso inteiro → +500 XP
# =============================================================================

from datetime import date, timedelta
from database import get_conn
from controllers.gamification import adicionar_xp

CORES_CATEGORIA = {
    "Trabalho":   "#E6A15A",
    "Estudos":    "#4E6B50",
    "Saúde":      "#2F4F3E",
    "Lifestyle":  "#8B5E3C",
    "Financeiro": "#7A6AAE",
}

XP_CONCLUIR_CURSO = 500


def _row_para_dict(row) -> dict:
    """
    Converte sqlite3.Row em dicionário enriquecido com campos calculados.
    Este é o formato que o AcademicView espera.
    """
    total      = row["total_aulas"] or 1   # Evita divisão por zero.
    concluidas = row["aulas_concluidas"]
    progresso  = round((concluidas / total) * 100, 1)
    cor        = CORES_CATEGORIA.get(row["categoria"], "#7A7773")

    return {
        "id":          row["id"],
        "nome":        row["nome"],
        "instituicao": row["instituicao"] or "",
        "total":       row["total_aulas"],
        "concluidas":  concluidas,
        "progresso":   progresso,
        "categoria":   row["categoria"],
        "cor":         cor,
        "github":      row["github"] or "",
        "doc":         row["doc"] or "",
        "concluido":   bool(row["concluido"]),
    }


def obter_cursos() -> list[dict]:
    """
    Retorna todos os cursos ordenados: incompletos primeiro, depois concluídos.
    """
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM cursos ORDER BY concluido ASC, id DESC"
    ).fetchall()
    return [_row_para_dict(r) for r in rows]


def adicionar_curso(
    nome: str,
    instituicao: str = "",
    total_aulas: int = 0,
    categoria: str = "Estudos",
    github: str = "",
    doc: str = "",
) -> str:
    """Insere um novo curso e retorna mensagem de confirmação."""
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO cursos (nome, instituicao, total_aulas, categoria, github, doc)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nome.strip(), instituicao.strip(), total_aulas, categoria, github.strip(), doc.strip()),
    )
    conn.commit()
    return f'Curso "{nome}" adicionado com sucesso!'


def atualizar_progresso(curso_id: int, aulas_concluidas: int) -> str:
    """
    Atualiza o número de aulas concluídas de um curso.

    Se o curso for completado (aulas == total), marca como concluído
    e distribui XP de conclusão.

    Retorna mensagem de feedback.
    """
    conn = get_conn()
    row  = conn.execute("SELECT * FROM cursos WHERE id = ?", (curso_id,)).fetchone()

    if not row:
        return "Curso não encontrado."

    total      = row["total_aulas"]
    ja_concluiu = bool(row["concluido"])

    # Garante que aulas_concluidas não ultrapasse o total.
    aulas_concluidas = max(0, min(aulas_concluidas, total))

    foi_concluido = (aulas_concluidas >= total and total > 0)

    conn.execute(
        """
        UPDATE cursos
        SET aulas_concluidas = ?,
            concluido = ?
        WHERE id = ?
        """,
        (aulas_concluidas, int(foi_concluido), curso_id),
    )
    conn.commit()

    # Concede XP apenas se acabou de concluir (não repete).
    if foi_concluido and not ja_concluiu:
        novo_xp = adicionar_xp(XP_CONCLUIR_CURSO)
        return f"🎉 Curso concluído! +{XP_CONCLUIR_CURSO} XP. Total: {novo_xp:,} XP"

    progresso = round((aulas_concluidas / max(total, 1)) * 100, 1)
    return f"Progresso atualizado: {aulas_concluidas}/{total} aulas ({progresso}%)"


def calcular_previsao_conclusao(curso_id: int) -> str:
    """
    Estima a data de conclusão com base na velocidade atual do usuário.

    Algoritmo:
      1. Calcula aulas restantes.
      2. Usa o histórico do daily_log para estimar horas/semana de estudo.
      3. Assume ~1 aula por hora de estudo.
      4. Projeta a data de conclusão.

    Retorna uma string legível como "~15 dias" ou "Concluído" ou "N/D".
    """
    conn = get_conn()
    row  = conn.execute("SELECT * FROM cursos WHERE id = ?", (curso_id,)).fetchone()

    if not row:
        return "N/D"

    if row["concluido"]:
        return "✅ Concluído"

    total      = row["total_aulas"]
    concluidas = row["aulas_concluidas"]
    restantes  = total - concluidas

    if restantes <= 0:
        return "✅ Concluído"

    if total == 0:
        return "N/D"

    # Busca média de horas de estudo dos últimos 14 dias.
    quinze_dias_atras = (date.today() - timedelta(days=14)).isoformat()
    logs = conn.execute(
        "SELECT horas_estudo FROM daily_log WHERE data >= ?",
        (quinze_dias_atras,)
    ).fetchall()

    if not logs:
        return "N/D"

    media_horas_dia = sum(r["horas_estudo"] for r in logs) / len(logs)

    if media_horas_dia <= 0:
        return "N/D"

    # Estimativa: 1 aula ≈ 1 hora de estudo.
    dias_estimados = round(restantes / media_horas_dia)

    data_previsao = date.today() + timedelta(days=dias_estimados)
    return data_previsao.strftime("%d/%m/%Y")


def deletar_curso(curso_id: int) -> None:
    """Remove permanentemente um curso."""
    conn = get_conn()
    conn.execute("DELETE FROM cursos WHERE id = ?", (curso_id,))
    conn.commit()
