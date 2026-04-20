# =============================================================================
# TAIGA OS — controllers/tasks.py
# CRUD de tarefas + integração com gamificação.
#
# Funções usadas pelas views:
#   obter_tarefas_pendentes()  → Dashboard (só status "A Fazer")
#   obter_tarefas()            → Kanban (todas)
#   adicionar_tarefa()         → Dashboard
#   concluir_tarefa()          → Dashboard (+20 XP)
#   atualizar_status_tarefa()  → Kanban (mover entre colunas)
#   deletar_tarefa()           → Kanban
# =============================================================================

from database import get_conn
from controllers.gamification import adicionar_xp

# Mapeamento categoria → cor hex (espelha o theme.py)
CORES_CATEGORIA = {
    "Trabalho":   "#E6A15A",
    "Estudos":    "#4E6B50",
    "Saúde":      "#2F4F3E",
    "Lifestyle":  "#8B5E3C",
    "Financeiro": "#7A6AAE",
}

XP_CONCLUIR_TAREFA = 20


def _row_para_tupla(row) -> tuple:
    """
    Converte um sqlite3.Row em tupla no formato esperado pelas views:
        (id, titulo, categoria, data_limite, status, cor_hex, descricao)
    """
    cor = CORES_CATEGORIA.get(row["categoria"], "#7A7773")
    return (
        row["id"],
        row["titulo"],
        row["categoria"],
        row["data_limite"],
        row["status"],
        cor,
        row["descricao"],
    )


def obter_tarefas_pendentes() -> list[tuple]:
    """
    Retorna todas as tarefas com status 'A Fazer', ordenadas por id desc.
    Usada no Dashboard para exibir o foco do dia.
    """
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tarefas WHERE status = 'A Fazer' ORDER BY id DESC"
    ).fetchall()
    return [_row_para_tupla(r) for r in rows]


def obter_tarefas() -> list[tuple]:
    """
    Retorna TODAS as tarefas (todos os status).
    Usada no Kanban para distribuir nas colunas.
    """
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tarefas ORDER BY id DESC").fetchall()
    return [_row_para_tupla(r) for r in rows]


def adicionar_tarefa(
    titulo: str,
    categoria: str = "Estudos",
    data_limite: str = None,
    descricao: str = "",
) -> None:
    """
    Insere uma nova tarefa com status padrão 'A Fazer'.
    Chamada pelo Dashboard e pode ser chamada por outros contextos.
    """
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO tarefas (titulo, categoria, data_limite, descricao)
        VALUES (?, ?, ?, ?)
        """,
        (titulo.strip(), categoria, data_limite, descricao),
    )
    conn.commit()


def concluir_tarefa(tarefa_id: int) -> int:
    """
    Marca uma tarefa como 'Concluído' e concede XP ao usuário.
    Retorna o novo total de XP.
    """
    conn = get_conn()
    conn.execute(
        "UPDATE tarefas SET status = 'Concluído' WHERE id = ?",
        (tarefa_id,)
    )
    conn.commit()
    return adicionar_xp(XP_CONCLUIR_TAREFA)


def atualizar_status_tarefa(tarefa_id: int, novo_status: str) -> None:
    """
    Atualiza o status de uma tarefa (usado no Kanban para mover cards).
    Se o novo status for 'Concluído', também concede XP.
    """
    conn = get_conn()
    conn.execute(
        "UPDATE tarefas SET status = ? WHERE id = ?",
        (novo_status, tarefa_id)
    )
    conn.commit()

    if novo_status == "Concluído":
        adicionar_xp(XP_CONCLUIR_TAREFA)


def deletar_tarefa(tarefa_id: int) -> None:
    """Remove permanentemente uma tarefa do banco."""
    conn = get_conn()
    conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()
