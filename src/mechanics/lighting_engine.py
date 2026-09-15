"""
Fichier : lighting_engine.py
Auteur : base technique (game jam)

Description :
Moteur de lumière. L'obscurité est la mécanique la plus structurante du jeu :
tout est dessiné normalement, puis le moteur applique deux passes par-dessus.

  1. Une passe de LUEUR : un dégradé radial dessiné en fusion additive pour
     chaque source, ce qui donne sa couleur chaude à une torche et sa teinte
     froide à un cadavre.
  2. Une passe d'OBSCURITÉ : un unique quad noir couvrant la zone de jeu, avec
     un shader qui y perce un trou dégradé autour de chaque source.

Le shader reçoit la liste des lumières visibles, donc faire vaciller une torche
revient simplement à faire varier son rayon d'une frame à l'autre.

Sources de lumière du jeu :
  - le halo du joueur (petit, il le suit) ;
  - les torches plantées (grandes, permanentes, elles vacillent) ;
  - les cadavres (faibles, ils pulsent : ce sont les balises du joueur) ;
  - la sortie de l'étage.

IMPORTANT : `draw()` doit être appelé alors que la caméra ÉCRAN est active
(après le rendu du monde, avant le HUD), car les lumières sont fournies en
coordonnées écran.
"""
from __future__ import annotations

from dataclasses import dataclass

import arcade
from arcade.gl import geometry

from src import constants as C

# Doit correspondre exactement à la taille du tableau déclaré dans le shader.
MAX_LIGHTS = 48

VERTEX_SHADER = """
#version 330
in vec2 in_vert;
out vec2 v_ndc;
void main() {
    v_ndc = in_vert;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330
in vec2 v_ndc;
out vec4 fragColor;

uniform vec2 u_window;              // taille logique de la fenetre, en pixels
uniform int u_count;                // nombre de lumieres actives
uniform vec3 u_lights[%(max)d];     // x, y (pixels ecran), rayon
uniform float u_darkness;           // opacite du voile, 0..1

void main() {
    // Position du pixel courant en coordonnees fenetre : passer par le repere
    // normalise rend le calcul independant des ecrans retina.
    vec2 position = (v_ndc * 0.5 + 0.5) * u_window;

    float light = 0.0;
    for (int i = 0; i < u_count; i++) {
        float radius = max(u_lights[i].z, 1.0);
        float distance_ratio = distance(position, u_lights[i].xy) / radius;
        // Extinction douce : plein feu au centre, noir complet au bord.
        float contribution = pow(clamp(1.0 - distance_ratio, 0.0, 1.0), 1.15);
        light = max(light, contribution);
    }

    fragColor = vec4(0.0, 0.0, 0.0, u_darkness * (1.0 - light));
}
""" % {"max": MAX_LIGHTS}


@dataclass
class _Light:
    x: float
    y: float
    radius: float
    color: tuple[int, int, int]
    glow: float          # intensité de la passe additive, 0 = aucune couleur


class LightingEngine:
    """Applique lueurs et voile d'obscurité sur la zone de jeu."""

    def __init__(self, window: arcade.Window):
        self.window = window
        self.ctx = window.ctx
        self.program = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )
        self.darkness = C.DARKNESS_ALPHA / 255.0
        # Le voile ne couvre que la zone de jeu : le bandeau du HUD reste lisible.
        self._quad = self._build_viewport_quad()
        self._lights: list[_Light] = []

        # Les sprites de lueur sont recyclés d'une frame à l'autre : créer des
        # sprites à chaque frame coûterait cher pour rien.
        self._glow_texture = arcade.load_texture(str(C.SPRITES_DIR / "light_gradient.png"))
        self._glow_list = arcade.SpriteList()
        self._glow_pool: list[arcade.Sprite] = []

    def _build_viewport_quad(self):
        """
        Quad couvrant le viewport de jeu, exprimé en coordonnées normalisées.

        Passer par le repère normalisé (et non par `ctx.viewport`) évite tout
        problème d'écran retina, où le framebuffer fait le double de pixels.
        """
        ndc_width = 2.0 * C.VIEWPORT_WIDTH / C.WINDOW_WIDTH
        ndc_height = 2.0 * C.VIEWPORT_HEIGHT / C.WINDOW_HEIGHT
        center_y = C.HUD_HEIGHT + C.VIEWPORT_HEIGHT / 2.0
        ndc_center_y = 2.0 * center_y / C.WINDOW_HEIGHT - 1.0
        return geometry.quad_2d(size=(ndc_width, ndc_height), pos=(0.0, ndc_center_y))

    # ------------------------------------------------------------------ #
    # Collecte des lumières (coordonnées ÉCRAN, pas monde)
    # ------------------------------------------------------------------ #
    def begin_frame(self) -> None:
        self._lights.clear()

    def add_light(self, screen_x: float, screen_y: float, radius: float,
                  color: tuple[int, int, int] = (255, 244, 224),
                  glow: float = 0.55) -> None:
        """
        Ajoute une lumière pour la frame courante.

        Les lumières hors écran sont ignorées : inutile de gaspiller un des
        emplacements du shader pour une torche située dans une autre zone.
        """
        if len(self._lights) >= MAX_LIGHTS:
            return
        if (
            screen_x < -radius
            or screen_x > C.WINDOW_WIDTH + radius
            or screen_y < C.HUD_HEIGHT - radius
            or screen_y > C.WINDOW_HEIGHT + radius
        ):
            return
        self._lights.append(_Light(screen_x, screen_y, radius, color, glow))

    # ------------------------------------------------------------------ #
    # Rendu
    # ------------------------------------------------------------------ #
    def _draw_glows(self) -> None:
        """Passe additive : donne sa couleur à chaque source de lumière."""
        while len(self._glow_pool) < len(self._lights):
            sprite = arcade.Sprite(self._glow_texture)
            self._glow_pool.append(sprite)
            self._glow_list.append(sprite)

        for index, sprite in enumerate(self._glow_pool):
            if index >= len(self._lights):
                sprite.visible = False
                continue
            light = self._lights[index]
            sprite.visible = light.glow > 0.0
            sprite.position = (light.x, light.y)
            # La texture fait 512 px de large pour un rayon de 256 px.
            sprite.scale = light.radius / 256.0
            sprite.color = light.color
            sprite.alpha = int(max(0.0, min(1.0, light.glow)) * 255)

        self.ctx.enable(self.ctx.BLEND)
        self.ctx.blend_func = self.ctx.BLEND_ADDITIVE
        self._glow_list.draw()
        self.ctx.blend_func = self.ctx.BLEND_DEFAULT

    def _draw_darkness(self) -> None:
        """Passe d'obscurité : voile noir percé autour de chaque lumière."""
        positions: list[float] = []
        for light in self._lights:
            positions.extend((light.x, light.y, light.radius))
        # Le shader déclare un tableau de taille fixe : on complète le reste.
        positions.extend([0.0, 0.0, 1.0] * (MAX_LIGHTS - len(self._lights)))

        self.program["u_window"] = (float(C.WINDOW_WIDTH), float(C.WINDOW_HEIGHT))
        self.program["u_count"] = len(self._lights)
        self.program["u_lights"] = positions
        self.program["u_darkness"] = self.darkness

        self.ctx.enable(self.ctx.BLEND)
        self.ctx.blend_func = self.ctx.BLEND_DEFAULT
        self._quad.render(self.program)

    def draw(self) -> None:
        """À appeler APRÈS le monde et AVANT le HUD, caméra écran active."""
        self._draw_glows()
        self._draw_darkness()
