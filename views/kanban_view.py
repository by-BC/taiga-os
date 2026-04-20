# =============================================================================
# TAIGA OS — views/kanban_view.py
# View do Quadro Kanban — visualização de tarefas em colunas de status.
#
# Colunas: A Fazer | Fazendo | Concluído
# Cada tarefa tem botões para mover entre colunas e deletar.
# =============================================================================

import customtkinter as ctk
from controllers.tasks import obter_tarefas, atualizar_status_tarefa, deletar_tarefa
from views.theme import COLORS, RADIUS, PADDING, make_font
from views.components import (
    SectionTitle, SubLabel, PrimaryButton, GhostButton,
    Card, CategoryBadge, StyledEntry, StyledComboBox
)

COLUNAS = ["A Fazer", "Fazendo", "Concluído"]

# Cores dos cabeçalhos de cada coluna.
COR_COLUNA = {
    "A Fazer":   COLORS["text_muted"],
    "Fazendo":   COLORS["green_light"],
    "Concluído": COLORS["green_deep"],
}


class KanbanView(ctk.CTkScrollableFrame):
    """View do Kanban Board."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            **kwargs
        )
        self._build()

    def _build(self):
        px = PADDING["lg"]

        # Cabeçalho.
        ctk.CTkLabel(
            self, text="📋 Kanban",
            font=make_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=px, pady=(PADDING["lg"], 2))

        SubLabel(
            self,
            text="Mova tarefas entre colunas. Concluir vale +20 XP.",
            muted=True
        ).pack(anchor="w", padx=px, pady=(0, PADDING["md"]))

        # Board Kanban (3 colunas lado a lado).
        self.board = ctk.CTkFrame(self, fg_color="transparent")
        self.board.pack(fill="both", expand=True, padx=px)

        # Configura as 3 colunas com peso igual.
        for i in range(3):
            self.board.columnconfigure(i, weight=1)

        self._render_board()

    def _render_board(self):
        """Limpa e re-renderiza o board completo."""
        for w in self.board.winfo_children():
            w.destroy()

        # Busca todas as tarefas (não filtra por status — mostra todas).
        todas = obter_tarefas()

        for col_idx, status in enumerate(COLUNAS):
            tarefas_col = [t for t in todas if t[4] == status]
            self._criar_coluna(col_idx, status, tarefas_col)

    def _criar_coluna(self, col_idx: int, status: str, tarefas: list):
        """Cria uma coluna do Kanban com suas tarefas."""
        coluna = ctk.CTkFrame(
            self.board,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"]
        )
        coluna.grid(
            row=0, column=col_idx,
            padx=(0, 8) if col_idx < 2 else 0,
            sticky="nsew",
            pady=4
        )

        # Cabeçalho da coluna.
        header = ctk.CTkFrame(coluna, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["sm"], pady=(PADDING["sm"], 4))

        # Ponto colorido + nome da coluna + contador.
        ctk.CTkFrame(
            header,
            width=8, height=8,
            fg_color=COR_COLUNA[status],
            corner_radius=4
        ).pack(side="left", padx=(4, 6))

        ctk.CTkLabel(
            header,
            text=status,
            font=make_font("subhead"),
            text_color=COR_COLUNA[status]
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=str(len(tarefas)),
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        ).pack(side="right", padx=4)

        # Divisor.
        ctk.CTkFrame(coluna, height=1, fg_color=COLORS["border"]).pack(fill="x")

        # Lista de tarefas da coluna.
        tasks_scroll = ctk.CTkScrollableFrame(
            coluna,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_hover"],
            height=400
        )
        tasks_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        if not tarefas:
            ctk.CTkLabel(
                tasks_scroll,
                text="Sem tarefas aqui",
                font=make_font("small"),
                text_color=COLORS["text_muted"]
            ).pack(pady=PADDING["lg"])
        else:
            for t in tarefas:
                self._criar_task_card(tasks_scroll, t, status)

    def _criar_task_card(self, parent, tarefa: tuple, status_atual: str):
        """Cria o card de uma tarefa dentro de uma coluna."""
        tid, titulo, categoria, data_limite, status, cor_hex, descricao = tarefa

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card2"],
            corner_radius=RADIUS["md"]
        )
        card.pack(fill="x", pady=4, padx=2)

        # Borda colorida à esquerda (indicador de categoria).
        ctk.CTkFrame(
            card, width=3, height=60,
            fg_color=cor_hex,
            corner_radius=1
        ).place(x=0, y=0, relheight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=(10, 8), pady=8)

        # Título.
        ctk.CTkLabel(
            inner, text=titulo,
            font=make_font("body"),
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=160  # Quebra linha se o título for longo.
        ).pack(anchor="w")

        # Prazo.
        if data_limite:
            ctk.CTkLabel(
                inner, text=f"📅 {data_limite}",
                font=make_font("small"),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w", pady=(2, 0))

        CategoryBadge(inner, categoria=categoria).pack(anchor="w", pady=(4, 2))

        # --- Botões de ação ---
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(4, 0))

        # Botão "→" para mover para a próxima coluna.
        col_idx = COLUNAS.index(status_atual)
        if col_idx < len(COLUNAS) - 1:
            proximo = COLUNAS[col_idx + 1]
            ctk.CTkButton(
                btn_frame,
                text=f"→ {proximo}",
                font=make_font("small"),
                fg_color=COLORS["green_deep"],
                hover_color=COLORS["green_mid"],
                text_color=COLORS["beige"],
                height=26,
                corner_radius=RADIUS["sm"],
                command=lambda t=tid, s=proximo: self._mover_tarefa(t, s)
            ).pack(side="left", padx=(0, 4))

        # Botão de deletar.
        ctk.CTkButton(
            btn_frame,
            text="🗑",
            font=make_font("small"),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_muted"],
            width=30, height=26,
            corner_radius=RADIUS["sm"],
            command=lambda t=tid: self._deletar_tarefa(t)
        ).pack(side="right")

    def _mover_tarefa(self, tarefa_id: int, novo_status: str):
        """Move a tarefa para outro status e re-renderiza o board."""
        atualizar_status_tarefa(tarefa_id, novo_status)
        self._render_board()

    def _deletar_tarefa(self, tarefa_id: int):
        """Deleta a tarefa e re-renderiza."""
        deletar_tarefa(tarefa_id)
        self._render_board()
