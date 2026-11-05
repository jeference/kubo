"""Renderiza a logo 3D do Kubo: o traço de um cubo amarelo neon com um K nas faces laterais.

O cubo gira como um peão, em torno do eixo vertical, para o K ficar sempre em pé como uma
letra. A câmera fica um pouco acima, então a face de cima aparece, e ela não leva K porque
ele giraria deitado. As faces são transparentes, mas escondem o que está atrás delas.
Como 90 graus nesse eixo levam o cubo nele mesmo, esse trecho já fecha o loop sem emenda.

O "ubo" ao lado do cubo é desenhado com tubos da mesma grossura das arestas, sob a mesma
luz, e tem uma pequena profundidade em âmbar, para parecer feito do mesmo material. Ele usa
a mesma escala do cubo: as duas imagens têm a altura de um quadro, então basta alinhar uma
ao lado da outra pelo centro.

Rode com o Python da .venv do backend, que já tem numpy e Pillow:

    apps/backend/.venv/Scripts/python.exe apps/web/consumer/scripts/render_logo.py
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "brand"

SIZE = 72  # O cubo acompanha o tamanho da fonte do header, que não passa de 36 px em telas 2x.
SUPERSAMPLE = 5
FRAMES = 45
STILL_FRAME = 12  # Para quem pede menos movimento: um pouco virado, com o K legível.
SECONDS_PER_LOOP = 4.5  # Uma volta inteira leva o quádruplo disso.

EDGE_RADIUS = 0.15
VIEW_HALF = 1.72
VIEW_CENTER_Y = -0.17  # Vista de cima, a perspectiva desce o contorno; isto o recentra.
CAMERA_ELEVATION = math.radians(18)
BOUND_RADIUS = 2.0
CAMERA_DISTANCE = 9.0

VIEW = np.array([0.0, 0.0, 1.0])
LIGHT = np.array([-0.45, 0.8, 0.62])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF_VECTOR = (LIGHT + VIEW) / np.linalg.norm(LIGHT + VIEW)

# Sombrear amarelo com preto vira verde-oliva, por isso a rampa desce para o âmbar.
YELLOW_RAMP = np.array(
    [
        [0.80, 0.53, 0.00],
        [0.93, 0.76, 0.00],
        [0.98, 1.00, 0.00],
        [0.98, 1.00, 0.00],
    ]
)
RAMP_STOPS = np.array([0.0, 0.42, 0.72, 1.0])

# Linhas das letras, em unidades do cubo e a partir do centro do quadro. O "b" tem a altura
# e a base do K quando a face está de frente, para o K e o "ubo" lerem como uma palavra só.
WORD_BOTTOM = -0.72
WORD_X_HEIGHT = 0.01
WORD_ASCENDER = 0.41
WORD_BOWL = (WORD_X_HEIGHT - WORD_BOTTOM) / 2
WORD_MIDDLE = WORD_BOTTOM + WORD_BOWL
WORD_U_LEFT = 0.32
WORD_U_RIGHT = WORD_U_LEFT + 2 * WORD_BOWL
WORD_B_STEM = WORD_U_RIGHT + 2 * EDGE_RADIUS + 0.20
WORD_O_CENTER = WORD_B_STEM + 3 * WORD_BOWL + 2 * EDGE_RADIUS + 0.17
WORD_DEPTH_X, WORD_DEPTH_Y = 0.08, -0.09
WORD_DEPTH_LAYERS = 12
WORD_DEPTH_COLOR = YELLOW_RAMP[0]  # O mesmo âmbar das faces mais escuras do cubo.
WORD_WIDTH = WORD_O_CENTER + WORD_BOWL + EDGE_RADIUS + WORD_DEPTH_X + 0.02
WORD_SCALE = 2  # Mais pixels que o cubo: a imagem é parada e pesa pouco.

K_RADIUS = 0.14
K_SEGMENTS = np.array(
    [
        [[-0.38, -0.54], [-0.38, 0.54]],  # Haste
        [[-0.33, -0.04], [0.38, 0.54]],  # Braço
        [[-0.06, 0.12], [0.41, -0.54]],  # Perna
    ]
)

# Eixo u do K em cada face lateral, para fora pela regra da mão direita com v = +Y (para cima).
FACE_U = {
    (2, 1): (0, 1.0),  # +Z
    (0, 1): (2, -1.0),  # +X
    (2, -1): (0, -1.0),  # -Z
    (0, -1): (2, 1.0),  # -X
}


def rotation(axis, angle):
    x, y, z = axis / np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    t = 1 - c
    return np.array(
        [
            [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
        ]
    )


def edges(p):
    """Distância até as 12 arestas do cubo, como tubos de pontas arredondadas."""
    a = np.abs(p) - 1.0
    beyond = np.maximum(a, 0)
    tube = np.minimum.reduce(
        [
            np.sqrt(beyond[:, 0] ** 2 + a[:, 1] ** 2 + a[:, 2] ** 2),
            np.sqrt(a[:, 0] ** 2 + beyond[:, 1] ** 2 + a[:, 2] ** 2),
            np.sqrt(a[:, 0] ** 2 + a[:, 1] ** 2 + beyond[:, 2] ** 2),
        ]
    )
    return tube - EDGE_RADIUS


def k_distance(p):
    """Distância até o K, medida no plano da face lateral mais próxima de cada ponto."""
    dominant = np.argmax(np.abs(p), axis=1)
    rows = np.arange(len(p))
    sign = np.sign(p[rows, dominant])
    u = np.zeros(len(p))
    for (axis, direction), (u_axis, u_sign) in FACE_U.items():
        mask = (dominant == axis) & (sign == direction)
        u[mask] = p[mask, u_axis] * u_sign
    v = p[:, 1]
    distances = []
    for (ax, ay), (bx, by) in K_SEGMENTS:
        dx, dy = bx - ax, by - ay
        t = np.clip(((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        distances.append(np.hypot(u - ax - t * dx, v - ay - t * dy))
    distance = np.min(distances, axis=0) - K_RADIUS
    distance[dominant == 1] = np.inf  # As faces de cima e de baixo não levam K.
    return distance


def scene(p):
    faces = np.max(np.abs(p), axis=1) - 1.0
    return np.minimum(edges(p), faces)


def normals(p):
    e = 0.004
    n = np.zeros_like(p)
    for axis in range(3):
        step = np.zeros(3)
        step[axis] = e
        n[:, axis] = scene(p + step) - scene(p - step)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)


def trace(origin, direction):
    """Marcha os raios até a superfície e devolve o t de cada um, ou NaN se não acertou."""
    b = np.sum(origin * direction, axis=1)
    c = np.sum(origin * origin, axis=1) - BOUND_RADIUS**2
    disc = b * b - c
    t = np.full(len(origin), np.nan)
    active = np.where(disc > 0)[0]
    current = -b[active] - np.sqrt(disc[active])
    far = -b[active] + np.sqrt(disc[active])
    # Raios rentes a uma aresta avançam muito pouco a cada passo, por isso o limite é alto.
    for _ in range(600):
        if not len(active):
            break
        d = scene(origin[active] + direction[active] * current[:, None])
        hit = d < 0.0015
        t[active[hit]] = current[hit]
        current = current + d
        keep = ~hit & (current < far)
        active, current, far = active[keep], current[keep], far[keep]
    return t


def shade(n):
    half_lambert = 0.5 + 0.5 * (n @ LIGHT)
    color = np.stack(
        [np.interp(half_lambert, RAMP_STOPS, YELLOW_RAMP[:, c]) for c in range(3)],
        axis=1,
    )
    specular = np.clip(n @ HALF_VECTOR, 0, 1) ** 42
    return np.clip(color + (1 - color) * specular[:, None] * 0.55, 0, 1)


def render_frame(angle):
    full = SIZE * SUPERSAMPLE
    grid = (np.arange(full) + 0.5) / full * 2 - 1
    sx, sy = np.meshgrid(grid * VIEW_HALF, -grid * VIEW_HALF + VIEW_CENTER_Y)
    target = np.stack([sx.ravel(), sy.ravel(), np.zeros(full * full)], axis=1)

    spin = rotation(np.array([0.0, 1.0, 0.0]), angle)
    world = rotation(np.array([1.0, 0.0, 0.0]), CAMERA_ELEVATION) @ spin

    eye = np.array([0.0, 0.0, CAMERA_DISTANCE])
    direction = target - eye
    direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    # A matriz leva objeto em câmera; multiplicar à direita aplica a inversa, pois ela é ortogonal.
    origin = np.tile(eye, (full * full, 1)) @ world
    direction = direction @ world

    t = trace(origin, direction)
    hit = np.where(~np.isnan(t))[0]
    p = origin[hit] + direction[hit] * t[hit, None]
    # Fora do K, quem acerta a face fica transparente: ela só esconde o que está atrás.
    painted = (edges(p) < 0.004) | (k_distance(p) < 0)

    rgba = np.zeros((full * full, 4))
    rgba[hit[painted], :3] = shade(normals(p[painted]) @ world.T)
    rgba[hit[painted], 3] = 1

    return downsample(rgba.reshape(full, full, 4))


def downsample(rgba):
    height, width = rgba.shape[0] // SUPERSAMPLE, rgba.shape[1] // SUPERSAMPLE
    premultiplied = rgba[..., :3] * rgba[..., 3:]
    blocks = (height, SUPERSAMPLE, width, SUPERSAMPLE)
    alpha = rgba[..., 3].reshape(blocks).mean((1, 3))
    color = premultiplied.reshape(*blocks, 3).mean((1, 3))
    color = color / np.maximum(alpha[..., None], 1e-6)
    pixels = np.clip(np.dstack([color, alpha]), 0, 1) * 255 + 0.5
    return Image.fromarray(pixels.astype(np.uint8), "RGBA")


def offset_to_segment(x, y, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return x - ax - t * dx, y - ay - t * dy


def offset_to_circle(x, y, cx):
    vx, vy = x - cx, y - WORD_MIDDLE
    length = np.maximum(np.hypot(vx, vy), 1e-9)
    return vx - vx / length * WORD_BOWL, vy - vy / length * WORD_BOWL


def word_centerline_offset(x, y):
    """Vetor do ponto mais próximo do traço das letras até cada ponto da imagem."""
    u_center = (WORD_U_LEFT + WORD_U_RIGHT) / 2
    bowl_x, bowl_y = offset_to_circle(x, y, u_center)
    bowl_x, bowl_y = np.where(y < WORD_MIDDLE, bowl_x, np.inf), np.where(y < WORD_MIDDLE, bowl_y, np.inf)
    parts = [
        # u
        offset_to_segment(x, y, WORD_U_LEFT, WORD_X_HEIGHT, WORD_U_LEFT, WORD_MIDDLE),
        (bowl_x, bowl_y),
        offset_to_segment(x, y, WORD_U_RIGHT, WORD_X_HEIGHT, WORD_U_RIGHT, WORD_BOTTOM),
        # b
        offset_to_segment(x, y, WORD_B_STEM, WORD_ASCENDER, WORD_B_STEM, WORD_BOTTOM),
        offset_to_circle(x, y, WORD_B_STEM + WORD_BOWL),
        # o
        offset_to_circle(x, y, WORD_O_CENTER),
    ]
    best_x, best_y = parts[0]
    for part_x, part_y in parts[1:]:
        closer = np.hypot(part_x, part_y) < np.hypot(best_x, best_y)
        best_x, best_y = np.where(closer, part_x, best_x), np.where(closer, part_y, best_y)
    return best_x, best_y


def render_word():
    pixels_per_unit = SIZE * WORD_SCALE * SUPERSAMPLE / (2 * VIEW_HALF)
    width = round(WORD_WIDTH * pixels_per_unit / SUPERSAMPLE) * SUPERSAMPLE
    height = SIZE * WORD_SCALE * SUPERSAMPLE
    x = (np.arange(width) + 0.5) / pixels_per_unit
    y = VIEW_HALF - (np.arange(height) + 0.5) / pixels_per_unit
    x, y = np.meshgrid(x, y)
    x, y = x.ravel(), y.ravel()
    rgba = np.zeros((height * width, 4))

    # A profundidade vem primeiro, de trás para a frente; a frente fica por cima de tudo.
    for layer in range(WORD_DEPTH_LAYERS, -1, -1):
        depth = layer / WORD_DEPTH_LAYERS
        offset_x, offset_y = word_centerline_offset(x - WORD_DEPTH_X * depth, y - WORD_DEPTH_Y * depth)
        distance = np.hypot(offset_x, offset_y)
        inside = distance < EDGE_RADIUS
        # A normal de um tubo visto de frente sai do centro do traço, como nas arestas do cubo.
        n = np.stack(
            [
                offset_x[inside] / EDGE_RADIUS,
                offset_y[inside] / EDGE_RADIUS,
                np.sqrt(1 - (distance[inside] / EDGE_RADIUS) ** 2),
            ],
            axis=1,
        )
        color = shade(n)
        if layer:
            color = color * 0.25 + WORD_DEPTH_COLOR * 0.75
        rgba[inside, :3] = color
        rgba[inside, 3] = 1
    return downsample(rgba.reshape(height, width, 4))


def main():
    frames = [render_frame(math.radians(90) * index / FRAMES) for index in range(FRAMES)]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT_DIR / "kubo-cube.webp",
        save_all=True,
        append_images=frames[1:],
        duration=round(SECONDS_PER_LOOP * 1000 / FRAMES),
        loop=0,
        quality=50,
        alpha_quality=40,
        method=6,
    )
    frames[STILL_FRAME].save(
        OUTPUT_DIR / "kubo-cube-still.webp", quality=92, alpha_quality=95, method=6
    )
    word = render_word()
    word.save(OUTPUT_DIR / "kubo-ubo.webp", quality=92, alpha_quality=95, method=6)
    print("kubo-ubo.webp", word.size)
    for name in ("kubo-cube.webp", "kubo-cube-still.webp", "kubo-ubo.webp"):
        print(name, (OUTPUT_DIR / name).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
