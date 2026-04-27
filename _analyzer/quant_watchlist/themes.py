"""Color themes for the dashboard. Sourced from primer/primitives."""

THEMES = {
    "dimmed": {  # GitHub Dark Dimmed
        "bg":          "#1c2128",
        "panel":       "#22272e",
        "panel_alt":   "#2d333b",
        "text":        "#adbac7",
        "text_strong": "#cdd9e5",
        "muted":       "#768390",
        "border":      "#444c56",
        "accent":      "#6cb6ff",
        "accent2":     "#dcbdfb",
        "up":          "#57ab5a",
        "down":        "#e5534b",
        "warn":        "#daaa3f",
        "neutral":     "#768390",
        "grid":        "#373e47",
        "code_bg":     "#2d333b",
        "header_grad": "linear-gradient(135deg, #316dca 0%, #8256d0 100%)",
    },
    "light": {
        "bg":          "#f6f8fa",
        "panel":       "#ffffff",
        "panel_alt":   "#f6f8fa",
        "text":        "#1f2328",
        "text_strong": "#1f2328",
        "muted":       "#656d76",
        "border":      "#d0d7de",
        "accent":      "#0969da",
        "accent2":     "#8250df",
        "up":          "#1a7f37",
        "down":        "#cf222e",
        "warn":        "#9a6700",
        "neutral":     "#656d76",
        "grid":        "#d0d7de",
        "code_bg":     "#f6f8fa",
        "header_grad": "linear-gradient(135deg, #0969da 0%, #8250df 100%)",
    },
}

# Active theme — set by the entry point
COLORS = THEMES["dimmed"]


def set_theme(name: str):
    global COLORS
    COLORS = THEMES.get(name, THEMES["dimmed"])
    return COLORS


def palette_cycle():
    return [COLORS["accent"], COLORS["accent2"], COLORS["up"], COLORS["down"],
            COLORS["warn"], "#f69d50", "#ec6cb9", "#56d4dd", "#b083f0", "#f47067"]
