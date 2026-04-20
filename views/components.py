# =============================================================================
# TAIGA OS — views/components.py
# Componentes reutilizáveis da interface.
#
# Em vez de repetir o mesmo código de botão/card em cada View,
# criamos classes aqui e importamos onde precisamos.
# Isso segue o princípio DRY (Don't Repeat Yourself).
# =============================================================================

import customtkinter as ctk
from views.theme import COLORS, RADIUS, make_font


class SectionTitle(ctk.CTkLabel):
    """
    Título de seção padronizado.
    Uso: SectionTitle(parent, text="🎯 Foco de Hoje")
    """
    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master,
            text=text,
            font=make_font("heading"),
            text_color=COLORS["text_primary"],
            **kwargs
        )


class SubLabel(ctk.CTkLabel):
    """Label de texto secundário/muted."""
    def __init__(self, master, text: str, muted: bool = False, **kwargs):
        color = COLORS["text_muted"] if muted else COLORS["text_secondary"]
        super().__init__(
            master,
            text=text,
            font=make_font("small"),
            text_color=color,
            **kwargs
        )


class PrimaryButton(ctk.CTkButton):
    """
    Botão de ação principal — verde escuro.
    Uso: PrimaryButton(parent, text="Salvar", command=minha_funcao)
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["green_deep"],
            hover_color=COLORS["green_mid"],
            text_color=COLORS["beige"],
            font=make_font("body"),
            corner_radius=RADIUS["md"],
            **kwargs
        )


class GhostButton(ctk.CTkButton):
    """Botão secundário sem preenchimento."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            border_width=1,
            border_color=COLORS["border_accent"],
            font=make_font("body"),
            corner_radius=RADIUS["md"],
            **kwargs
        )


class AccentButton(ctk.CTkButton):
    """Botão de destaque — laranja suave."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["orange"] + "28",   # Laranja com transparência (HEX + alfa).
            hover_color=COLORS["orange"] + "44",
            text_color=COLORS["orange"],
            border_width=1,
            border_color=COLORS["orange"] + "55",
            font=make_font("body"),
            corner_radius=RADIUS["md"],
            **kwargs
        )


class Card(ctk.CTkFrame):
    """
    Card/container padrão do sistema.
    Todos os painéis internos devem usar este componente para consistência.
    """
    def __init__(self, master, level: int = 1, **kwargs):
        """
        level=1 → bg_card (nível primário de card)
        level=2 → bg_card2 (card dentro de card)
        """
        bg = COLORS["bg_card"] if level == 1 else COLORS["bg_card2"]
        super().__init__(
            master,
            fg_color=bg,
            corner_radius=RADIUS["lg"],
            **kwargs
        )


class CategoryBadge(ctk.CTkLabel):
    """
    Badge colorida para mostrar a categoria de uma tarefa.
    Uso: CategoryBadge(parent, categoria="Estudos")
    """
    CORES = {
        "Trabalho":   "#E6A15A",
        "Estudos":    "#4E6B50",
        "Saúde":      "#2F4F3E",
        "Lifestyle":  "#8B5E3C",
        "Financeiro": "#7A6AAE",
    }

    def __init__(self, master, categoria: str, **kwargs):
        cor = self.CORES.get(categoria, COLORS["text_muted"])
        super().__init__(
            master,
            text=categoria,
            font=make_font("label"),
            text_color=cor,
            **kwargs
        )


class ProgressBar(ctk.CTkFrame):
    """
    Barra de progresso customizada com label de porcentagem.

    Uso:
        bar = ProgressBar(parent, label="Python Avançado", value=0.72)
        bar.pack(fill="x", padx=10, pady=5)
    """
    def __init__(self, master, label: str, value: float, color: str = None, **kwargs):
        """
        label: texto à esquerda da barra
        value: float entre 0.0 e 1.0
        color: cor da barra (opcional, usa verde padrão se None)
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        bar_color = color or COLORS["green_light"]

        # Linha superior: nome + porcentagem.
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            top, text=label,
            font=make_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"{value * 100:.0f}%",
            font=make_font("label"),
            text_color=bar_color
        ).pack(side="right")

        # Barra de progresso.
        pb = ctk.CTkProgressBar(
            self,
            progress_color=bar_color,
            fg_color=COLORS["bg_card2"],
            height=6,
            corner_radius=3
        )
        pb.pack(fill="x")
        pb.set(min(value, 1.0))


class StyledEntry(ctk.CTkEntry):
    """Entry (campo de texto) com estilo do Design System."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card2"],
            border_color=COLORS["border_accent"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            font=make_font("body"),
            corner_radius=RADIUS["md"],
            **kwargs
        )


class StyledComboBox(ctk.CTkComboBox):
    """ComboBox (dropdown) com estilo do Design System."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card2"],
            border_color=COLORS["border_accent"],
            button_color=COLORS["green_deep"],
            button_hover_color=COLORS["green_mid"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["bg_hover"],
            font=make_font("body"),
            corner_radius=RADIUS["md"],
            **kwargs
        )
