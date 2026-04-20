# =============================================================================
# TAIGA OS — views/main_window.py
# A janela principal do sistema — o "esqueleto" da aplicação.
#
# Estrutura:
#   ┌─────────────┬────────────────────────────────────────┐
#   │             │                                        │
#   │   Sidebar   │          Área de Conteúdo              │
#   │  (220px)    │         (conteúdo dinâmico)            │
#   │             │                                        │
#   └─────────────┴────────────────────────────────────────┘
#
# A sidebar é fixa. O conteúdo à direita muda conforme a navegação.
# Cada "página" é um Frame que é mostrado/escondido com pack/pack_forget.
# =============================================================================

import customtkinter as ctk
from datetime import datetime
from controllers.gamification import obter_status_usuario, verificar_e_atualizar_streak
from views.theme import COLORS, RADIUS, PADDING, make_font

# Importa todas as Views (páginas) do sistema.
from views.dashboard_view import DashboardView
from views.daily_view     import DailyLogView
from views.academic_view  import AcademicView
from views.kanban_view    import KanbanView
from views.pomodoro_view  import PomodoroView


class TaigaApp(ctk.CTk):
    """
    Classe principal da aplicação. Herda de `ctk.CTk` (a janela raiz).

    Responsabilidades:
      - Configurar a janela (tamanho, título, tema).
      - Construir a sidebar de navegação.
      - Gerenciar qual View está visível no momento.
      - Atualizar o painel de XP/streak na sidebar.
    """

    def __init__(self):
        super().__init__()

        # Configura o tema global do CustomTkinter.
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Configurações da janela.
        self.title("Taiga OS")
        self.geometry("1200x800")
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["bg_primary"])

        # Verifica e atualiza o streak ao abrir.
        verificar_e_atualizar_streak()

        # Dicionário que mapeia nome da página → instância do Frame.
        # Começamos com None e criamos sob demanda (lazy loading).
        self._views: dict = {}
        self._view_ativa: str = ""

        # Constrói os dois painéis principais.
        self._build_layout()
        self._build_sidebar()
        self._build_main_area()

        # Navega para o Dashboard na inicialização.
        self._navegar("Dashboard")

    def _build_layout(self):
        """Define o grid principal da janela: coluna sidebar + coluna conteúdo."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar: largura fixa.
        self.grid_columnconfigure(1, weight=1)  # Conteúdo: expande.

    def _build_sidebar(self):
        """Constrói a barra lateral com logo, navegação e painel de XP."""
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=COLORS["bg_deep"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # Mantém a largura fixa.

        # Impede que os widgets internos "encolham" a sidebar.
        self.sidebar.grid_rowconfigure(10, weight=1)  # Linha de espaçamento flexível.
        self.sidebar.grid_columnconfigure(0, weight=1)

        # --- Logo ---
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=PADDING["md"], pady=(PADDING["lg"], PADDING["md"]))

        # Ícone da árvore (texto emoji como substituto).
        ctk.CTkLabel(
            logo_frame,
            text="🌲",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, 8))

        logo_text = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_text.pack(side="left")

        ctk.CTkLabel(
            logo_text,
            text="Taiga",
            font=ctk.CTkFont(family="Plus Jakarta Sans", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_text,
            text="OS",
            font=ctk.CTkFont(family="Plus Jakarta Sans", size=18, weight="bold"),
            text_color=COLORS["orange"]
        ).place(relx=0, rely=0)  # Reposiciona ao lado de "Taiga" manualmente.

        # Reinicia o logo_text com abordagem mais simples.
        for w in logo_text.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            logo_text,
            text="Taiga OS",
            font=ctk.CTkFont(family="Plus Jakarta Sans", size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_text,
            text="Personal OS",
            font=ctk.CTkFont(family="Inter", size=10),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")

        # Divisor.
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=COLORS["border"]
        ).grid(row=1, column=0, sticky="ew", padx=PADDING["md"], pady=0)

        # --- Itens de Navegação ---
        # Lista de (nome, emoji) para cada página.
        nav_items = [
            ("Dashboard",   "📊"),
            ("Daily Log",   "📝"),
            ("Academic Hub","📚"),
            ("Kanban",      "📋"),
            ("Pomodoro",    "🍅"),
        ]

        # Dicionário de botões de nav para controlar o estado "ativo".
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        for row_idx, (nome, emoji) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {emoji}  {nome}",
                anchor="w",
                font=make_font("body"),
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_muted"],
                corner_radius=RADIUS["md"],
                height=40,
                command=lambda n=nome: self._navegar(n)
            )
            btn.grid(row=row_idx, column=0, sticky="ew",
                     padx=PADDING["sm"], pady=2)
            self._nav_buttons[nome] = btn

        # --- Painel de XP (parte inferior da sidebar) ---
        # A linha 10 tem weight=1, então este frame fica empurrado para baixo.
        self._build_xp_panel()

    def _build_xp_panel(self):
        """Painel de XP, nível e streak na parte inferior da sidebar."""
        # Divisor antes do painel.
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=COLORS["border"]
        ).grid(row=11, column=0, sticky="ew", padx=PADDING["md"], pady=4)

        xp_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        xp_frame.grid(row=12, column=0, sticky="ew",
                      padx=PADDING["md"], pady=(0, PADDING["md"]))

        status = obter_status_usuario()

        # Streak.
        ctk.CTkLabel(
            xp_frame,
            text=f"🔥  {status['streak']} dias de streak",
            font=make_font("body"),
            text_color=COLORS["orange"],
            anchor="w"
        ).pack(fill="x", pady=2)

        # Nível.
        ctk.CTkLabel(
            xp_frame,
            text=f"⭐  {status['nivel']}",
            font=make_font("body"),
            text_color=status["cor_nivel"],
            anchor="w"
        ).pack(fill="x", pady=2)

        # XP total.
        ctk.CTkLabel(
            xp_frame,
            text=f"⚡  {status['xp']:,} XP",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", pady=2)

        # Barra de progresso mini do nível.
        prog = status["xp_no_nivel"] / max(status["xp_necessario"], 1)
        bar = ctk.CTkProgressBar(
            xp_frame,
            progress_color=status["cor_nivel"],
            fg_color=COLORS["bg_card2"],
            height=4,
            corner_radius=2
        )
        bar.pack(fill="x", pady=(4, 2))
        bar.set(min(prog, 1.0))

        ctk.CTkLabel(
            xp_frame,
            text=f"→ {status['proximo_nivel']}",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x")

        # Salva referência para poder atualizar depois.
        self._xp_frame = xp_frame

    def _build_main_area(self):
        """Container da área de conteúdo principal (à direita da sidebar)."""
        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_primary"]
        )
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def _navegar(self, nome_pagina: str):
        """
        Troca a View ativa no painel principal.

        Estratégia: lazy loading + pack/pack_forget.
          1. Se a View ainda não foi criada, instancia ela.
          2. Esconde a View atual com `.pack_forget()`.
          3. Mostra a nova View com `.pack()`.

        Isso é mais eficiente que destruir e recriar os frames toda vez.
        """
        # Se já está na página, não faz nada.
        if nome_pagina == self._view_ativa:
            return

        # --- Atualiza o visual dos botões de navegação ---
        for nome, btn in self._nav_buttons.items():
            if nome == nome_pagina:
                btn.configure(
                    fg_color=COLORS["bg_card"],
                    text_color=COLORS["text_primary"],
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_muted"]
                )

        # --- Esconde a view atual ---
        if self._view_ativa and self._view_ativa in self._views:
            self._views[self._view_ativa].pack_forget()

        # --- Cria a view se ainda não existe ---
        if nome_pagina not in self._views:
            self._views[nome_pagina] = self._criar_view(nome_pagina)

        # --- Exibe a nova view ---
        self._views[nome_pagina].pack(fill="both", expand=True)
        self._view_ativa = nome_pagina

        # Atualiza o painel de XP ao navegar (pode ter mudado).
        self._atualizar_xp_panel()

    def _criar_view(self, nome: str) -> ctk.CTkFrame:
        """
        Factory method: instancia a View correta pelo nome.
        Todas as views recebem `self.main_container` como master.
        """
        views_map = {
            "Dashboard":    DashboardView,
            "Daily Log":    DailyLogView,
            "Academic Hub": AcademicView,
            "Kanban":       KanbanView,
            "Pomodoro":     PomodoroView,
        }
        ViewClass = views_map.get(nome)
        if not ViewClass:
            raise ValueError(f"View '{nome}' não encontrada.")
        return ViewClass(self.main_container)

    def _atualizar_xp_panel(self):
        """
        Re-renderiza o painel de XP da sidebar.
        Destrói os widgets antigos e reconstrói com dados frescos do banco.
        """
        for widget in self._xp_frame.winfo_children():
            widget.destroy()

        status = obter_status_usuario()

        ctk.CTkLabel(
            self._xp_frame,
            text=f"🔥  {status['streak']} dias de streak",
            font=make_font("body"),
            text_color=COLORS["orange"],
            anchor="w"
        ).pack(fill="x", pady=2)

        ctk.CTkLabel(
            self._xp_frame,
            text=f"⭐  {status['nivel']}",
            font=make_font("body"),
            text_color=status["cor_nivel"],
            anchor="w"
        ).pack(fill="x", pady=2)

        ctk.CTkLabel(
            self._xp_frame,
            text=f"⚡  {status['xp']:,} XP",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x", pady=2)

        prog = status["xp_no_nivel"] / max(status["xp_necessario"], 1)
        bar = ctk.CTkProgressBar(
            self._xp_frame,
            progress_color=status["cor_nivel"],
            fg_color=COLORS["bg_card2"],
            height=4,
            corner_radius=2
        )
        bar.pack(fill="x", pady=(4, 2))
        bar.set(min(prog, 1.0))

        ctk.CTkLabel(
            self._xp_frame,
            text=f"→ {status['proximo_nivel']}",
            font=make_font("small"),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).pack(fill="x")
