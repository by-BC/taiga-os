# =============================================================================
# TAIGA OS — views/dashboard_view.py
# View do Dashboard — primeira tela que o usuário vê.
#
# Exibe:
#   - Saudação com data e hora
#   - Cards de métricas (XP, streak, horas de estudo)
#   - Barra de progresso de nível
#   - Lista de tarefas pendentes do dia
#   - Resumo semanal de hábitos
# =============================================================================

import customtkinter as ctk
from datetime import datetime
from controllers.gamification import obter_status_usuario
from controllers.tasks import obter_tarefas_pendentes, concluir_tarefa, adicionar_tarefa
from controllers.daily_log import obter_media_semanal, obter_log_hoje
from views.theme import COLORS, RADIUS, PADDING, make_font
from views.components import (
    SectionTitle, SubLabel, PrimaryButton, GhostButton,
    Card, CategoryBadge, StyledEntry, StyledComboBox
)


class DashboardView(ctk.CTkScrollableFrame):
    """
    Frame principal do Dashboard. Herda de CTkScrollableFrame
    para que o conteúdo possa ser rolado se não couber na tela.

    Esta classe é instanciada pela main_window quando o usuário
    clica em "Dashboard" na sidebar.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_hover"],
            **kwargs
        )
        # Armazena referência ao frame de tarefas para poder re-renderizar.
        self.tasks_frame = None
        self._build()

    def _build(self):
        """Constrói todos os widgets do Dashboard."""
        pad = {"padx": PADDING["lg"], "pady": (0, PADDING["md"])}

        # --- SAUDAÇÃO ---
        self._build_header(**pad)

        # --- CARDS DE MÉTRICAS ---
        self._build_metrics(**pad)

        # --- BARRA DE NÍVEL ---
        self._build_level_bar(**pad)

        # --- TAREFAS DE HOJE ---
        self._build_tasks_section(**pad)

        # --- RESUMO SEMANAL ---
        self._build_weekly_summary(**pad)

    def _build_header(self, **pad):
        """Saudação dinâmica baseada no horário."""
        agora = datetime.now()
        hora = agora.hour

        if hora < 12:
            saudacao = "Bom dia"
        elif hora < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"

        data_fmt = agora.strftime("%A, %d de %B de %Y").capitalize()

        ctk.CTkLabel(
            self,
            text=f"{saudacao} 🌲",
            font=make_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=(PADDING["lg"], 2), **{"padx": PADDING["lg"]})

        ctk.CTkLabel(
            self,
            text=data_fmt,
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["md"]))

    def _build_metrics(self, **pad):
        """Grid de cards com as métricas principais."""
        status = obter_status_usuario()
        media = obter_media_semanal()

        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", **pad)

        # Configura 4 colunas de igual peso.
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)

        # Dados de cada card: (emoji, valor, rótulo, cor_valor)
        cards_data = [
            ("⚡", f"{status['xp']:,}",       "XP Total",        COLORS["orange"]),
            ("🔥", f"{status['streak']} dias", "Streak",          COLORS["orange"]),
            ("📚", f"{media['total_estudo']}h", "Horas (semana)", COLORS["green_pale"]),
            ("💧", f"{media['agua']}L",         "Água (média)",   COLORS["green_light"]),
        ]

        for col, (emoji, valor, rotulo, cor) in enumerate(cards_data):
            card = Card(metrics_frame, level=1)
            card.grid(row=0, column=col, padx=(0, 8) if col < 3 else 0, sticky="nsew")

            ctk.CTkLabel(card, text=emoji, font=make_font("heading"), anchor="w"
                         ).pack(anchor="w", padx=PADDING["md"], pady=(PADDING["md"], 2))
            ctk.CTkLabel(card, text=valor, font=make_font("heading"),
                         text_color=cor, anchor="w"
                         ).pack(anchor="w", padx=PADDING["md"])
            ctk.CTkLabel(card, text=rotulo, font=make_font("small"),
                         text_color=COLORS["text_muted"], anchor="w"
                         ).pack(anchor="w", padx=PADDING["md"], pady=(2, PADDING["md"]))

    def _build_level_bar(self, **pad):
        """Barra de progresso de nível com informações de XP."""
        status = obter_status_usuario()

        card = Card(self, level=1)
        card.pack(fill="x", **pad)

        # Linha de cabeçalho: nível atual + próximo nível.
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["md"], pady=(PADDING["md"], 4))

        ctk.CTkLabel(
            header,
            text=f"⭐ {status['nivel']}",
            font=make_font("subhead"),
            text_color=status["cor_nivel"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"→ {status['proximo_nivel']}",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=8)

        ctk.CTkLabel(
            header,
            text=f"{status['xp_no_nivel']:,} / {status['xp_necessario']:,} XP",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
        ).pack(side="right")

        # Barra de progresso.
        progresso = status["xp_no_nivel"] / max(status["xp_necessario"], 1)
        level_bar = ctk.CTkProgressBar(
            card,
            progress_color=status["cor_nivel"],
            fg_color=COLORS["bg_card2"],
            height=8,
            corner_radius=4,
        )
        level_bar.pack(fill="x", padx=PADDING["md"], pady=(0, PADDING["md"]))
        level_bar.set(min(progresso, 1.0))

    def _build_tasks_section(self, **pad):
        """Seção de tarefas do dia com campo para adicionar novas."""
        SectionTitle(self, text="🎯 Foco de Hoje", anchor="w").pack(
            fill="x", padx=PADDING["lg"], pady=(PADDING["sm"], PADDING["sm"])
        )

        # --- Formulário de nova tarefa ---
        form = Card(self, level=1)
        form.pack(fill="x", **pad)

        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])
        form_inner.columnconfigure(0, weight=1)

        self.entry_nova_tarefa = StyledEntry(
            form_inner, placeholder_text="Nova tarefa...", height=36
        )
        self.entry_nova_tarefa.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.combo_categoria = StyledComboBox(
            form_inner,
            values=["Trabalho", "Estudos", "Saúde", "Lifestyle", "Financeiro"],
            width=130
        )
        self.combo_categoria.set("Estudos")
        self.combo_categoria.grid(row=0, column=1, padx=(0, 8))

        PrimaryButton(
            form_inner, text="Adicionar", width=90,
            command=self._adicionar_tarefa
        ).grid(row=0, column=2)

        # --- Lista de tarefas ---
        # Guarda a referência para poder re-renderizar ao concluir uma tarefa.
        self.tasks_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tasks_frame.pack(fill="x", padx=PADDING["lg"])
        self._renderizar_tarefas()

    def _renderizar_tarefas(self):
        """Limpa e re-desenha a lista de tarefas pendentes."""
        # Destrói todos os widgets filhos do frame antes de redesenhar.
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        tarefas = obter_tarefas_pendentes()

        if not tarefas:
            ctk.CTkLabel(
                self.tasks_frame,
                text="Nenhuma tarefa pendente. Bom trabalho! 🌲",
                font=make_font("body"),
                text_color=COLORS["text_muted"]
            ).pack(pady=PADDING["md"])
            return

        for tarefa in tarefas:
            # Desempacota a tupla retornada pelo controller.
            tid, titulo, categoria, data_limite, status, cor_hex, descricao = tarefa
            self._criar_task_card(tid, titulo, categoria, data_limite, status, cor_hex)

    def _criar_task_card(self, tid, titulo, categoria, data_limite, status, cor):
        """Cria um card visual para uma tarefa individual."""
        card = Card(self.tasks_frame, level=2)
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=PADDING["md"], pady=PADDING["sm"])
        inner.columnconfigure(1, weight=1)

        # Checkbox para marcar como concluída.
        ctk.CTkCheckBox(
            inner,
            text="",
            width=20,
            fg_color=COLORS["green_deep"],
            hover_color=COLORS["green_mid"],
            border_color=COLORS["border_accent"],
            checkmark_color=COLORS["beige"],
            # Lambda captura `tid` e `card` no closure para evitar bug de loop.
            command=lambda t=tid, c=card: self._concluir_tarefa(t, c)
        ).grid(row=0, column=0, padx=(0, 8))

        # Título da tarefa.
        ctk.CTkLabel(
            inner,
            text=titulo,
            font=make_font("body"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=0, column=1, sticky="ew")

        # Prazo (se existir).
        if data_limite:
            ctk.CTkLabel(
                inner,
                text=data_limite,
                font=make_font("small"),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=2, padx=8)

        # Badge de categoria.
        CategoryBadge(inner, categoria=categoria).grid(row=0, column=3, padx=(0, 4))

    def _concluir_tarefa(self, tarefa_id: int, card_widget):
        """
        Callback do checkbox: marca a tarefa como concluída e remove o card.
        Usa `.after(300, ...)` para dar um leve delay visual antes de destruir.
        """
        concluir_tarefa(tarefa_id)
        card_widget.after(300, card_widget.destroy)

    def _adicionar_tarefa(self):
        """Callback do botão Adicionar: lê os campos e chama o controller."""
        titulo = self.entry_nova_tarefa.get().strip()
        if not titulo:
            return  # Não adiciona se o campo estiver vazio.

        categoria = self.combo_categoria.get()
        adicionar_tarefa(titulo, categoria)

        # Limpa o campo de entrada.
        self.entry_nova_tarefa.delete(0, "end")

        # Re-renderiza a lista para mostrar a nova tarefa.
        self._renderizar_tarefas()

    def _build_weekly_summary(self, **pad):
        """Cards com resumo dos hábitos da semana."""
        SectionTitle(self, text="📊 Semana em Números", anchor="w").pack(
            fill="x", padx=PADDING["lg"], pady=(PADDING["md"], PADDING["sm"])
        )

        media = obter_media_semanal()
        log_hoje = obter_log_hoje()

        card = Card(self, level=1)
        card.pack(fill="x", **pad)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])

        for i in range(3):
            grid.columnconfigure(i, weight=1)

        metricas = [
            ("💧 Água",  f"{media['agua']} L/dia",  "média"),
            ("😴 Sono",  f"{media['sono']} h/noite", "média"),
            ("📚 Estudo",f"{media['total_estudo']} h","total na semana"),
        ]

        for col, (titulo, valor, sub) in enumerate(metricas):
            ctk.CTkLabel(grid, text=titulo, font=make_font("small"),
                         text_color=COLORS["text_muted"], anchor="w"
                         ).grid(row=0, column=col, sticky="w", padx=(0, 16))
            ctk.CTkLabel(grid, text=valor, font=make_font("subhead"),
                         text_color=COLORS["green_pale"], anchor="w"
                         ).grid(row=1, column=col, sticky="w", padx=(0, 16))
            ctk.CTkLabel(grid, text=sub, font=make_font("small"),
                         text_color=COLORS["text_muted"], anchor="w"
                         ).grid(row=2, column=col, sticky="w", padx=(0, 16), pady=(0, PADDING["sm"]))

        # Aviso se o log de hoje não foi preenchido.
        if not log_hoje:
            ctk.CTkLabel(
                card,
                text="⚠️  Log de hoje não preenchido. Registre seus hábitos!",
                font=make_font("small"),
                text_color=COLORS["orange"]
            ).pack(anchor="w", padx=PADDING["md"], pady=(0, PADDING["md"]))
