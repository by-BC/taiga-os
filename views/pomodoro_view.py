# =============================================================================
# TAIGA OS — views/pomodoro_view.py
# View do Timer Pomodoro integrado.
#
# Técnica Pomodoro:
#   - 25 minutos de foco total
#   - 5 minutos de pausa curta
#   - Ao final do ciclo de foco, sugere registrar as horas no Daily Log
#
# Implementação do timer com `after()`:
#   O CustomTkinter (assim como Tkinter) é single-threaded.
#   Não podemos usar `time.sleep()` dentro da UI pois travaria a janela.
#   O método `.after(ms, callback)` agenda uma chamada após X milissegundos,
#   sem bloquear a interface. É assim que animações e timers funcionam em Tkinter.
# =============================================================================

import customtkinter as ctk
from views.theme import COLORS, RADIUS, PADDING, make_font
from views.components import SectionTitle, SubLabel, PrimaryButton, GhostButton, Card

# Durações em segundos.
DURACAO_FOCO   = 25 * 60  # 1500 segundos
DURACAO_PAUSA  = 5  * 60  # 300 segundos


class PomodoroView(ctk.CTkScrollableFrame):
    """View do Timer Pomodoro."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            **kwargs
        )
        # Estado interno do timer.
        self._segundos_restantes = DURACAO_FOCO
        self._rodando = False          # Se o timer está ativo.
        self._modo = "foco"            # "foco" ou "pausa"
        self._ciclos_completos = 0     # Contador de pomodoros concluídos.
        self._after_id = None          # ID do `.after()` para cancelar se necessário.

        self._build()

    def _build(self):
        px = PADDING["lg"]

        # Cabeçalho.
        ctk.CTkLabel(
            self, text="🍅 Pomodoro",
            font=make_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=px, pady=(PADDING["lg"], 2))

        SubLabel(
            self,
            text="25 min de foco + 5 min de pausa. Ao concluir, registre no Daily Log.",
            muted=True
        ).pack(anchor="w", padx=px, pady=(0, PADDING["md"]))

        # Card principal do timer.
        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))

        # Label de modo (Foco / Pausa).
        self.modo_label = ctk.CTkLabel(
            card,
            text="🎯 MODO FOCO",
            font=make_font("subhead"),
            text_color=COLORS["green_light"]
        )
        self.modo_label.pack(pady=(PADDING["lg"], PADDING["sm"]))

        # Display do tempo — número grande central.
        self.timer_label = ctk.CTkLabel(
            card,
            text=self._formatar_tempo(DURACAO_FOCO),
            font=ctk.CTkFont(family="Inter", size=64, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.timer_label.pack(pady=PADDING["sm"])

        # Barra de progresso do ciclo.
        self.progress_bar = ctk.CTkProgressBar(
            card,
            progress_color=COLORS["green_light"],
            fg_color=COLORS["bg_card2"],
            height=8,
            corner_radius=4,
            width=300
        )
        self.progress_bar.pack(pady=PADDING["sm"])
        self.progress_bar.set(1.0)  # Inicia cheio (de cima para baixo).

        # Contador de ciclos.
        self.ciclos_label = ctk.CTkLabel(
            card,
            text="Ciclos concluídos: 0",
            font=make_font("small"),
            text_color=COLORS["text_muted"]
        )
        self.ciclos_label.pack(pady=(PADDING["sm"], 0))

        # Botões de controle.
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=PADDING["md"])

        self.btn_iniciar = PrimaryButton(
            btn_row, text="▶  Iniciar", width=120, height=40,
            command=self._toggle_timer
        )
        self.btn_iniciar.pack(side="left", padx=8)

        GhostButton(
            btn_row, text="↺  Resetar", width=100, height=40,
            command=self._resetar
        ).pack(side="left", padx=8)

        # Notificação / sugestão de registro (hidden inicialmente).
        self.notif_card = Card(self, level=1)
        self.notif_card.pack(fill="x", padx=px, pady=(0, PADDING["md"]))
        self.notif_card.pack_forget()  # Esconde até que o ciclo termine.

        ctk.CTkLabel(
            self.notif_card,
            text="🎉 Ciclo de foco concluído!",
            font=make_font("subhead"),
            text_color=COLORS["green_pale"]
        ).pack(padx=PADDING["md"], pady=(PADDING["md"], 4), anchor="w")

        self.notif_label = ctk.CTkLabel(
            self.notif_card,
            text="",
            font=make_font("body"),
            text_color=COLORS["text_secondary"]
        )
        self.notif_label.pack(padx=PADDING["md"], anchor="w")

        GhostButton(
            self.notif_card,
            text="✕  Fechar aviso",
            width=140, height=30,
            command=lambda: self.notif_card.pack_forget()
        ).pack(padx=PADDING["md"], pady=PADDING["md"], anchor="w")

        # Informações sobre a técnica.
        self._build_info(px)

    def _build_info(self, px):
        """Card informativo sobre a técnica Pomodoro."""
        card = Card(self, level=1)
        card.pack(fill="x", padx=px, pady=(0, PADDING["xl"]))

        ctk.CTkLabel(
            card, text="Como funciona a Técnica Pomodoro",
            font=make_font("subhead"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=PADDING["md"], pady=(PADDING["md"], 4))

        steps = [
            "1. Escolha uma tarefa para focar",
            "2. Inicie o timer de 25 minutos",
            "3. Trabalhe sem interrupções até o alarme",
            "4. Faça uma pausa de 5 minutos",
            "5. A cada 4 ciclos, faça uma pausa maior (15-30 min)",
        ]

        for step in steps:
            ctk.CTkLabel(
                card, text=step,
                font=make_font("body"),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=PADDING["md"], pady=2)

        ctk.CTkLabel(
            card,
            text="💡 Ao finalizar um ciclo de foco, registre as horas no Daily Log para ganhar XP.",
            font=make_font("small"),
            text_color=COLORS["orange"]
        ).pack(anchor="w", padx=PADDING["md"], pady=(PADDING["sm"], PADDING["md"]))

    # ------------------------------------------------------------------
    # LÓGICA DO TIMER
    # ------------------------------------------------------------------

    def _toggle_timer(self):
        """Alterna entre iniciar e pausar o timer."""
        if self._rodando:
            self._pausar()
        else:
            self._iniciar()

    def _iniciar(self):
        """Inicia a contagem regressiva."""
        self._rodando = True
        self.btn_iniciar.configure(text="⏸  Pausar")
        self._tick()  # Inicia o primeiro tick.

    def _pausar(self):
        """Pausa o timer cancelando o próximo tick agendado."""
        self._rodando = False
        self.btn_iniciar.configure(text="▶  Continuar")

        # Cancela o after() pendente para evitar que o timer continue em background.
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _resetar(self):
        """Volta ao estado inicial."""
        self._pausar()
        self._modo = "foco"
        self._segundos_restantes = DURACAO_FOCO
        self.btn_iniciar.configure(text="▶  Iniciar")
        self._atualizar_display()
        self.progress_bar.set(1.0)
        self.modo_label.configure(text="🎯 MODO FOCO", text_color=COLORS["green_light"])

    def _tick(self):
        """
        Função chamada a cada 1 segundo pelo `.after()`.

        `.after(1000, self._tick)` agenda uma nova chamada após 1000ms (1s).
        Isso cria um loop de timer sem bloquear a UI.
        """
        if not self._rodando:
            return

        if self._segundos_restantes > 0:
            self._segundos_restantes -= 1
            self._atualizar_display()
            self._atualizar_progresso_bar()

            # Agenda o próximo tick em 1 segundo.
            self._after_id = self.after(1000, self._tick)
        else:
            # Timer chegou a zero: troca de modo.
            self._ao_terminar_ciclo()

    def _ao_terminar_ciclo(self):
        """Trata o fim de um ciclo (foco ou pausa)."""
        self._rodando = False
        self._after_id = None

        if self._modo == "foco":
            # Fim do ciclo de foco.
            self._ciclos_completos += 1
            self.ciclos_label.configure(text=f"Ciclos concluídos: {self._ciclos_completos}")

            # Exibe notificação sugerindo registrar as horas.
            minutos_focados = 25
            self.notif_label.configure(
                text=f"Você ficou {minutos_focados} minutos focado.\n"
                     f"Vá ao Daily Log e registre +{minutos_focados // 60 or 1} hora(s) de estudo para ganhar XP!"
            )
            self.notif_card.pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["md"]))

            # Troca para modo pausa.
            self._modo = "pausa"
            self._segundos_restantes = DURACAO_PAUSA
            self.modo_label.configure(text="☕ MODO PAUSA", text_color=COLORS["orange"])
            self.btn_iniciar.configure(text="▶  Iniciar Pausa")

        else:
            # Fim da pausa: volta para foco.
            self._modo = "foco"
            self._segundos_restantes = DURACAO_FOCO
            self.modo_label.configure(text="🎯 MODO FOCO", text_color=COLORS["green_light"])
            self.btn_iniciar.configure(text="▶  Iniciar Foco")

        self._atualizar_display()
        self.progress_bar.set(1.0)

    def _atualizar_display(self):
        """Atualiza o label do timer."""
        self.timer_label.configure(text=self._formatar_tempo(self._segundos_restantes))

    def _atualizar_progresso_bar(self):
        """Atualiza a barra de progresso do ciclo atual."""
        duracao_total = DURACAO_FOCO if self._modo == "foco" else DURACAO_PAUSA
        progresso = self._segundos_restantes / duracao_total
        cor = COLORS["green_light"] if self._modo == "foco" else COLORS["orange"]
        self.progress_bar.configure(progress_color=cor)
        self.progress_bar.set(max(progresso, 0))

    @staticmethod
    def _formatar_tempo(segundos: int) -> str:
        """Converte segundos em string 'MM:SS'."""
        minutos = segundos // 60
        segs    = segundos % 60
        return f"{minutos:02d}:{segs:02d}"
