# =============================================================================
# TAIGA OS — views/daily_view.py
# View do Diário de Hábitos (Daily Log).
#
# Permite ao usuário registrar diariamente:
#   - Humor
#   - Litros de água ingeridos
#   - Horas de sono
#   - Horas de estudo/trabalho
#   - Checklist de rotina (Treino, Leitura, Meditação...)
# =============================================================================

import customtkinter as ctk
from controllers.daily_log import registrar_habitos, obter_log_hoje
from views.theme import COLORS, RADIUS, PADDING, make_font
from views.components import (
    SectionTitle, SubLabel, PrimaryButton, Card, StyledEntry, StyledComboBox
)


# Ícones de humor para a interface.
HUMORES = ["😊 Feliz", "😐 Normal", "💪 Produtivo", "😰 Ansioso", "😴 Cansado"]

# Checklist de rotina diária.
ROTINA_ITEMS = [
    "🏃 Treino de corrida",
    "📖 Leitura",
    "💧 Hidratação (meta atingida)",
    "🧘 Meditação / foco",
    "😴 Dormi bem",
]


class DailyLogView(ctk.CTkScrollableFrame):
    """
    View do Diário de Hábitos.

    Ao ser instanciada, verifica se já existe um log para hoje
    e pré-preenche os campos se houver.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            **kwargs
        )
        # Dicionário de variáveis do checklist (nome → BooleanVar).
        self.checklist_vars = {}
        self._build()
        self._carregar_log_existente()

    def _build(self):
        """Constrói a interface do formulário."""
        px = PADDING["lg"]

        # Cabeçalho.
        ctk.CTkLabel(
            self, text="📝 Daily Log",
            font=make_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=px, pady=(PADDING["lg"], 2))

        SubLabel(
            self,
            text="Registre seus hábitos do dia. Cada entrada vale XP.",
            muted=True
        ).pack(anchor="w", padx=px, pady=(0, PADDING["md"]))

        # Seção: Bem-estar
        self._build_bem_estar(px)

        # Seção: Horas
        self._build_horas(px)

        # Seção: Checklist de rotina
        self._build_checklist(px)

        # Botão de salvar e label de status.
        PrimaryButton(
            self, text="💾  Salvar o dia", height=40,
            command=self._salvar
        ).pack(padx=px, pady=PADDING["md"], anchor="w")

        self.status_label = ctk.CTkLabel(
            self, text="",
            font=make_font("body"),
            text_color=COLORS["green_pale"]
        )
        self.status_label.pack(anchor="w", padx=px, pady=(0, PADDING["xl"]))

    def _build_bem_estar(self, px):
        """Seção de humor e métricas físicas."""
        SectionTitle(self, text="🌡️ Bem-estar", anchor="w").pack(
            fill="x", padx=px, pady=(PADDING["sm"], PADDING["sm"])
        )

        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])
        grid.columnconfigure(1, weight=1)

        # Humor
        ctk.CTkLabel(grid, text="Como está seu humor?",
                     font=make_font("body"), text_color=COLORS["text_secondary"]
                     ).grid(row=0, column=0, sticky="w", pady=8, padx=(0, 16))

        self.combo_humor = StyledComboBox(grid, values=HUMORES, width=200)
        self.combo_humor.set(HUMORES[1])  # Normal como padrão.
        self.combo_humor.grid(row=0, column=1, sticky="w", pady=8)

        # Água
        ctk.CTkLabel(grid, text="Água ingerida (litros):",
                     font=make_font("body"), text_color=COLORS["text_secondary"]
                     ).grid(row=1, column=0, sticky="w", pady=8, padx=(0, 16))

        self.entry_agua = StyledEntry(grid, placeholder_text="Ex: 2.5", width=120)
        self.entry_agua.grid(row=1, column=1, sticky="w", pady=8)

        # Sono
        ctk.CTkLabel(grid, text="Horas de sono:",
                     font=make_font("body"), text_color=COLORS["text_secondary"]
                     ).grid(row=2, column=0, sticky="w", pady=8, padx=(0, 16))

        self.entry_sono = StyledEntry(grid, placeholder_text="Ex: 7.5", width=120)
        self.entry_sono.grid(row=2, column=1, sticky="w", pady=8)

    def _build_horas(self, px):
        """Seção de registro de horas de estudo/trabalho."""
        SectionTitle(self, text="⏱️ Horas Registradas", anchor="w").pack(
            fill="x", padx=px, pady=(PADDING["sm"], PADDING["sm"])
        )

        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])
        grid.columnconfigure(1, weight=1)

        ctk.CTkLabel(grid, text="Horas de estudo/trabalho:",
                     font=make_font("body"), text_color=COLORS["text_secondary"]
                     ).grid(row=0, column=0, sticky="w", pady=8, padx=(0, 16))

        self.entry_estudo = StyledEntry(grid, placeholder_text="Ex: 3", width=120)
        self.entry_estudo.grid(row=0, column=1, sticky="w", pady=8)

        ctk.CTkLabel(
            grid,
            text="💡 Cada hora registrada vale 100 XP",
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

    def _build_checklist(self, px):
        """Checklist de atividades da rotina diária."""
        SectionTitle(self, text="✅ Rotina do Dia", anchor="w").pack(
            fill="x", padx=px, pady=(PADDING["sm"], PADDING["sm"])
        )

        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])

        for item in ROTINA_ITEMS:
            # Cada item tem sua própria BooleanVar para rastrear o estado.
            var = ctk.BooleanVar(value=False)
            self.checklist_vars[item] = var

            ctk.CTkCheckBox(
                inner,
                text=item,
                variable=var,
                font=make_font("body"),
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["green_deep"],
                hover_color=COLORS["green_mid"],
                border_color=COLORS["border_accent"],
                checkmark_color=COLORS["beige"]
            ).pack(anchor="w", pady=4)

        # Indica que completar a rotina inteira dá bônus de XP.
        ctk.CTkLabel(
            card,
            text="💡 Rotina completa = +50 XP bônus",
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=PADDING["md"], pady=(0, PADDING["md"]))

    def _salvar(self):
        """
        Coleta todos os valores do formulário e chama o controller.
        Usa try/except para tratar erros de conversão de tipo.
        """
        try:
            humor = self.combo_humor.get()
            agua  = float(self.entry_agua.get() or 0)
            sono  = float(self.entry_sono.get() or 0)
            horas = float(self.entry_estudo.get() or 0)

            # Verifica se todos os itens do checklist foram marcados.
            todos_marcados = all(var.get() for var in self.checklist_vars.values())

            # Chama o controller que salva no banco e distribui XP.
            mensagem = registrar_habitos(humor, agua, sono, horas, todos_marcados)

            self.status_label.configure(text=mensagem, text_color=COLORS["green_pale"])

        except ValueError:
            self.status_label.configure(
                text="⚠️  Atenção: use apenas números nos campos de horas/água/sono.",
                text_color=COLORS["orange"]
            )

    def _carregar_log_existente(self):
        """
        Se o usuário já preencheu o log hoje, pré-carrega os valores.
        Chamado no __init__ após construir a interface.
        """
        log = obter_log_hoje()
        if not log:
            return

        # Tenta encontrar o humor com emoji correspondente.
        for h in HUMORES:
            if log["humor"] and log["humor"] in h:
                self.combo_humor.set(h)
                break

        if log["agua_litros"]:
            self.entry_agua.delete(0, "end")
            self.entry_agua.insert(0, str(log["agua_litros"]))

        if log["sono_horas"]:
            self.entry_sono.delete(0, "end")
            self.entry_sono.insert(0, str(log["sono_horas"]))

        if log["horas_estudo"]:
            self.entry_estudo.delete(0, "end")
            self.entry_estudo.insert(0, str(log["horas_estudo"]))

        self.status_label.configure(
            text="📋 Log de hoje já registrado. Você pode atualizar.",
            text_color=COLORS["text_muted"]
        )
