# =============================================================================
# TAIGA OS — views/academic_view.py
# View do Academic Hub — gestão de cursos e projetos.
#
# Funcionalidades:
#   - Listar cursos com barras de progresso
#   - Atualizar aulas concluídas
#   - Adicionar novos cursos
#   - Ver previsão de conclusão
#   - Links para GitHub / Documentação
# =============================================================================

import customtkinter as ctk
import webbrowser  # Módulo nativo do Python para abrir URLs no navegador.
from controllers.courses import (
    obter_cursos, adicionar_curso, atualizar_progresso,
    calcular_previsao_conclusao, deletar_curso
)
from views.theme import COLORS, RADIUS, PADDING, make_font
from views.components import (
    SectionTitle, SubLabel, PrimaryButton, GhostButton, AccentButton,
    Card, CategoryBadge, StyledEntry, StyledComboBox
)


class AcademicView(ctk.CTkScrollableFrame):
    """View do Academic & Work Hub."""

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
            self, text="📚 Academic Hub",
            font=make_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=px, pady=(PADDING["lg"], 2))

        SubLabel(
            self,
            text="Acompanhe cursos e projetos. Concluir um curso vale 500 XP.",
            muted=True
        ).pack(anchor="w", padx=px, pady=(0, PADDING["md"]))

        # Formulário de adição de curso.
        self._build_add_form(px)

        # Lista de cursos.
        self.courses_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.courses_frame.pack(fill="x", padx=px)
        self._render_courses()

    def _build_add_form(self, px):
        """Formulário para adicionar um novo curso."""
        SectionTitle(self, text="➕ Novo Curso / Projeto", anchor="w").pack(
            fill="x", padx=px, pady=(0, PADDING["sm"])
        )

        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])
        inner.columnconfigure(0, weight=2)
        inner.columnconfigure(1, weight=1)

        # Linha 1: Nome e Instituição.
        self.entry_nome = StyledEntry(inner, placeholder_text="Nome do curso ou projeto", height=34)
        self.entry_nome.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=4)

        self.entry_inst = StyledEntry(inner, placeholder_text="Instituição", height=34)
        self.entry_inst.grid(row=0, column=1, sticky="ew", pady=4)

        # Linha 2: Total de aulas e categoria.
        self.entry_total = StyledEntry(inner, placeholder_text="Total de aulas", width=120, height=34)
        self.entry_total.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)

        self.combo_cat = StyledComboBox(
            inner,
            values=["Estudos", "Trabalho", "Saúde", "Lifestyle", "Financeiro"],
            width=150
        )
        self.combo_cat.set("Estudos")
        self.combo_cat.grid(row=1, column=1, sticky="w", pady=4)

        # Linha 3: Links.
        self.entry_github = StyledEntry(inner, placeholder_text="Link GitHub (opcional)", height=34)
        self.entry_github.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=4)

        self.entry_doc = StyledEntry(inner, placeholder_text="Link de documentação (opcional)", height=34)
        self.entry_doc.grid(row=2, column=1, sticky="ew", pady=4)

        PrimaryButton(
            inner, text="Adicionar Curso", height=36,
            command=self._adicionar_curso
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))

        self.form_status = ctk.CTkLabel(
            inner, text="", font=make_font("small"), text_color=COLORS["green_pale"]
        )
        self.form_status.grid(row=3, column=1, sticky="w", padx=8)

    def _render_courses(self):
        """Limpa e re-renderiza todos os cursos."""
        for w in self.courses_frame.winfo_children():
            w.destroy()

        SectionTitle(self.courses_frame, text="📋 Seus Cursos", anchor="w").pack(
            fill="x", pady=(0, PADDING["sm"])
        )

        cursos = obter_cursos()

        if not cursos:
            ctk.CTkLabel(
                self.courses_frame,
                text="Nenhum curso cadastrado ainda.",
                font=make_font("body"),
                text_color=COLORS["text_muted"]
            ).pack(pady=PADDING["md"])
            return

        for curso in cursos:
            self._criar_course_card(curso)

    def _criar_course_card(self, curso: dict):
        """Cria o card visual de um curso com controles interativos."""
        card = Card(self.courses_frame, level=1)
        card.pack(fill="x", pady=6)

        # --- Cabeçalho do card ---
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["md"], pady=(PADDING["md"], 4))
        header.columnconfigure(1, weight=1)

        # Indicador de cor da categoria.
        ctk.CTkFrame(
            header,
            width=4, height=32,
            fg_color=curso["cor"],
            corner_radius=2
        ).grid(row=0, column=0, padx=(0, 10), rowspan=2)

        # Nome e instituição.
        ctk.CTkLabel(
            header, text=curso["nome"],
            font=make_font("subhead"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            header, text=curso["instituicao"] or "—",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=1, column=1, sticky="w")

        CategoryBadge(header, categoria=curso["categoria"]).grid(row=0, column=2, padx=8)

        # --- Barra de progresso ---
        prog_frame = ctk.CTkFrame(card, fg_color="transparent")
        prog_frame.pack(fill="x", padx=PADDING["md"], pady=4)

        label_top = ctk.CTkFrame(prog_frame, fg_color="transparent")
        label_top.pack(fill="x")

        ctk.CTkLabel(
            label_top,
            text=f"{curso['concluidas']} de {curso['total']} aulas",
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        ).pack(side="left")

        ctk.CTkLabel(
            label_top,
            text=f"{curso['progresso']}%",
            font=make_font("label"),
            text_color=curso["cor"]
        ).pack(side="right")

        ctk.CTkProgressBar(
            prog_frame,
            progress_color=curso["cor"],
            fg_color=COLORS["bg_card2"],
            height=6,
            corner_radius=3
        ).pack(fill="x", pady=(4, 0)).set(min(curso["progresso"] / 100, 1.0))

        # --- Controles ---
        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=PADDING["md"], pady=(8, PADDING["md"]))

        # Input para atualizar aulas.
        entry_aulas = StyledEntry(controls, placeholder_text="Aulas feitas", width=100, height=30)
        entry_aulas.insert(0, str(curso["concluidas"]))
        entry_aulas.pack(side="left", padx=(0, 8))

        PrimaryButton(
            controls, text="Atualizar", width=90, height=30,
            command=lambda c=curso["id"], e=entry_aulas: self._atualizar_progresso(c, e)
        ).pack(side="left", padx=(0, 8))

        # Previsão de conclusão.
        previsao = calcular_previsao_conclusao(curso["id"])
        ctk.CTkLabel(
            controls,
            text=f"📅 Previsão: {previsao}",
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=8)

        # Links externos (abre no navegador padrão).
        if curso["github"]:
            GhostButton(
                controls, text="GitHub", width=70, height=30,
                command=lambda url=curso["github"]: webbrowser.open(url)
            ).pack(side="right", padx=(4, 0))

        if curso["doc"]:
            GhostButton(
                controls, text="Docs", width=70, height=30,
                command=lambda url=curso["doc"]: webbrowser.open(url)
            ).pack(side="right", padx=(4, 0))

    def _atualizar_progresso(self, curso_id: int, entry: StyledEntry):
        """Callback do botão Atualizar de um curso."""
        try:
            aulas = int(entry.get())
            mensagem = atualizar_progresso(curso_id, aulas)
            # Re-renderiza para refletir o novo progresso na barra.
            self._render_courses()
        except ValueError:
            pass  # Ignora se o valor não for um número.

    def _adicionar_curso(self):
        """Callback do formulário de novo curso."""
        nome = self.entry_nome.get().strip()
        if not nome:
            self.form_status.configure(text="⚠️  Nome é obrigatório.", text_color=COLORS["orange"])
            return

        try:
            total = int(self.entry_total.get() or 0)
        except ValueError:
            self.form_status.configure(text="⚠️  Total de aulas deve ser um número.", text_color=COLORS["orange"])
            return

        mensagem = adicionar_curso(
            nome=nome,
            instituicao=self.entry_inst.get().strip(),
            total_aulas=total,
            categoria=self.combo_cat.get(),
            github=self.entry_github.get().strip(),
            doc=self.entry_doc.get().strip(),
        )

        self.form_status.configure(text=f"✅ {mensagem}", text_color=COLORS["green_pale"])

        # Limpa os campos.
        for entry in [self.entry_nome, self.entry_inst, self.entry_total,
                      self.entry_github, self.entry_doc]:
            entry.delete(0, "end")

        # Atualiza a lista.
        self._render_courses()
