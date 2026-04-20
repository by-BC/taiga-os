# =============================================================================
# TAIGA OS — views/theme.py
# Centraliza TODOS os tokens visuais do Design System.
#
# Por que centralizar?
#   Se você quiser mudar uma cor, fonte ou raio de borda, altera aqui
#   e todo o sistema reflete a mudança automaticamente.
#   Evita "magic numbers" espalhados pelo código.
# =============================================================================


# ------------------------------------------------------------------
# CORES — baseadas no brand book do Taiga OS
# ------------------------------------------------------------------
COLORS = {
    # Fundos
    "bg_deep":      "#161814",   # Fundo mais escuro (janela raiz)
    "bg_primary":   "#1E201C",   # Fundo principal
    "bg_card":      "#252820",   # Cards e containers internos
    "bg_card2":     "#2E3129",   # Cards de segundo nível
    "bg_hover":     "#353830",   # Estado hover de botões/itens

    # Verde — cor primária (15% do uso)
    "green_deep":   "#2F4F3E",   # Verde escuro (botões primários, active)
    "green_mid":    "#3D6050",   # Verde médio (hover de botões)
    "green_light":  "#4E6B50",   # Verde claro (barras, badges)
    "green_pale":   "#7A9E7A",   # Verde pálido (texto de sucesso)

    # Laranja — acento (5% do uso)
    "orange":       "#E6A15A",   # Laranja principal (alertas, XP, Trabalho)
    "orange_pale":  "#F2C48A",   # Laranja claro (hover de acento)

    # Neutros — textos e superfícies (80% do uso)
    "beige":        "#F4EFEA",   # Texto principal / fundo claro
    "brown":        "#8B5E3C",   # Detalhes, categoria Lifestyle
    "text_primary": "#F4EFEA",   # Texto principal
    "text_secondary":"#B8B4AE",  # Texto secundário
    "text_muted":   "#7A7773",   # Texto desabilitado/placeholder

    # Categorias — cada uma com sua cor
    "cat_trabalho": "#E6A15A",
    "cat_estudos":  "#4E6B50",
    "cat_saude":    "#2F4F3E",
    "cat_lifestyle":"#8B5E3C",
    "cat_financeiro":"#7A6AAE",

    # Bordas
    "border":       "#2A2D28",
    "border_accent":"#3D5040",
}

# Atalho para as cores de categoria (útil nos controllers e views).
CATEGORIA_CORES = {
    "Trabalho":   COLORS["cat_trabalho"],
    "Estudos":    COLORS["cat_estudos"],
    "Saúde":      COLORS["cat_saude"],
    "Lifestyle":  COLORS["cat_lifestyle"],
    "Financeiro": COLORS["cat_financeiro"],
}


# ------------------------------------------------------------------
# FONTES
# ------------------------------------------------------------------
FONTS = {
    # CustomTkinter usa CTkFont. Estes dicionários são passados como kwargs.
    "title":    {"family": "Plus Jakarta Sans", "size": 22, "weight": "bold"},
    "heading":  {"family": "Inter",             "size": 17, "weight": "bold"},
    "subhead":  {"family": "Inter",             "size": 14, "weight": "bold"},
    "body":     {"family": "Inter",             "size": 13, "weight": "normal"},
    "small":    {"family": "Inter",             "size": 11, "weight": "normal"},
    "label":    {"family": "Inter",             "size": 11, "weight": "bold"},
    "mono":     {"family": "Consolas",          "size": 12, "weight": "normal"},
}


# ------------------------------------------------------------------
# BORDAS E ESPAÇAMENTO
# ------------------------------------------------------------------
RADIUS = {
    "sm":  4,
    "md":  8,
    "lg":  12,
    "xl":  16,
}

PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}


# ------------------------------------------------------------------
# FUNÇÃO UTILITÁRIA: cria CTkFont a partir do dicionário de tokens
# ------------------------------------------------------------------
def make_font(token_key: str):
    """
    Importa e retorna um CTkFont com base em um token de fonte.

    Uso: label = ctk.CTkLabel(..., font=make_font("heading"))
    """
    import customtkinter as ctk
    spec = FONTS[token_key]
    return ctk.CTkFont(
        family=spec["family"],
        size=spec["size"],
        weight=spec["weight"]
    )
