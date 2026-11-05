"""Renderiza a logo 3D do Kubo: o traço de um cubo amarelo neon com um K nas faces laterais.

O cubo gira como um peão, em torno do eixo vertical, para o K ficar sempre em pé como uma
letra. A câmera fica um pouco acima, então a face de cima aparece, e ela não leva K porque
ele giraria deitado. As faces são transparentes, mas escondem o que está atrás delas.
Como 90 graus nesse eixo levam o cubo nele mesmo, esse trecho já fecha o loop sem emenda.

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

    rgba = rgba.reshape(full, full, 4)
    premultiplied = rgba[..., :3] * rgba[..., 3:]
    blocks = (SIZE, SUPERSAMPLE, SIZE, SUPERSAMPLE)
    alpha = rgba[..., 3].reshape(blocks).mean((1, 3))
    color = premultiplied.reshape(*blocks, 3).mean((1, 3))
    color = color / np.maximum(alpha[..., None], 1e-6)
    pixels = np.clip(np.dstack([color, alpha]), 0, 1) * 255 + 0.5
    return Image.fromarray(pixels.astype(np.uint8), "RGBA")


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
    for name in ("kubo-cube.webp", "kubo-cube-still.webp"):
        print(name, (OUTPUT_DIR / name).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
