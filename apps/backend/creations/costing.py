"""Estimativa conservadora de volume, área e custo. Volume baixo significa vender com prejuízo.

Quase todas as malhas geradas são abertas: no Trellis, `mesh.volume` ficou abaixo de 10% do
volume fechado e a área veio cerca do dobro. Preenchimento simples vaza por furos pequenos.
O método abaixo foi testado nos modelos do protótipo, mas não contra fatiador ou impressão.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
import structlog
import trimesh
from scipy import ndimage

from catalog.models import CostParameters, ProductSize
from creations.models import CostEstimate, Model3D

_GRID = 100
_BALL_RADIUS = 3
_AREA_DIVISOR = 0.85
log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class MeshMeasure:
    unit_volume: float
    unit_area: float
    method: str


def _ball(radius: int) -> np.ndarray:
    axis = np.arange(-radius, radius + 1)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return x**2 + y**2 + z**2 <= radius**2


def _load_mesh(glb: bytes) -> trimesh.Trimesh:
    loaded = trimesh.load(io.BytesIO(glb), file_type="glb", force="mesh", process=False)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise ValueError("GLB sem malha.")
    return loaded


def _occupied_grid(mesh: trimesh.Trimesh) -> tuple[np.ndarray, float]:
    """Voxels de superfície, com a maior dimensão ocupando `_GRID` voxels."""
    extents = mesh.extents
    longest = float(extents.max())
    if longest <= 0:
        raise ValueError("Malha sem dimensão.")
    pitch = longest / _GRID
    # Amostragem por área, em vez de só vértices: malhas leves deixariam buracos na grade.
    samples = max(200_000, len(mesh.faces) * 3)
    points, _ = trimesh.sample.sample_surface(mesh, samples, seed=7)
    points = np.vstack([points, mesh.vertices])
    margin = _BALL_RADIUS + 2
    indices = np.floor((points - mesh.bounds[0]) / pitch).astype(int) + margin
    shape = np.ceil(extents / pitch).astype(int) + 2 * margin + 1
    grid = np.zeros(shape, dtype=bool)
    grid[indices[:, 0], indices[:, 1], indices[:, 2]] = True
    return grid, pitch


def _exterior_by_ball(surface: np.ndarray) -> np.ndarray:
    """Exterior alcançado por uma esfera grande demais para passar pelos furos pequenos."""
    free = ~surface
    eroded = ndimage.binary_erosion(free, structure=_ball(_BALL_RADIUS), border_value=1)
    labels, _ = ndimage.label(eroded)
    corner = labels[0, 0, 0]
    if corner == 0:
        return np.zeros_like(surface)
    reachable = labels == corner
    return ndimage.binary_dilation(reachable, structure=_ball(_BALL_RADIUS)) & free


def _inside_by_axes(surface: np.ndarray) -> np.ndarray:
    """Interior: voxel com superfície nas seis direções dos eixos."""
    inside = np.ones_like(surface)
    for axis in range(3):
        forward = np.logical_or.accumulate(surface, axis=axis)
        backward = np.flip(
            np.logical_or.accumulate(np.flip(surface, axis=axis), axis=axis), axis=axis
        )
        inside &= forward & backward
    return inside & ~surface


def measure_mesh(glb: bytes) -> MeshMeasure:
    """Volume e área com a maior dimensão = 1. Falha vira o pior caso, nunca custo zero (RN-14)."""
    try:
        mesh = _load_mesh(glb)
        surface, pitch = _occupied_grid(mesh)
        exterior = _exterior_by_ball(surface)
        by_ball = (~exterior & ~surface).sum()
        by_axes = _inside_by_axes(surface).sum()
        surface_count = int(surface.sum())
        # O máximo protege contra vazamento em um dos métodos. Metade da superfície conta como
        # volume: a casca do voxel fica, em média, metade para dentro.
        filled_voxels = float(max(by_ball, by_axes)) + surface_count / 2
        unit = (pitch / float(mesh.extents.max())) ** 3
        volume = filled_voxels * unit

        border = surface & ndimage.binary_dilation(~surface & exterior)
        area = float(border.sum()) * (pitch / float(mesh.extents.max())) ** 2 / _AREA_DIVISOR
        if volume <= 0 or area <= 0:
            raise ValueError("Medida vazia.")
        return MeshMeasure(unit_volume=volume, unit_area=area, method="voxel_flood")
    except Exception as exc:  # Qualquer falha cai no pior caso, registrado no modelo.
        log.warning("mesh_measure_failed", error=str(exc))
        return _worst_case(glb)


def _worst_case(glb: bytes) -> MeshMeasure:
    """Caixa delimitadora cheia: nunca subestima."""
    try:
        extents = _load_mesh(glb).extents
        unit = extents / extents.max()
        volume = float(unit.prod())
        area = float(2 * (unit[0] * unit[1] + unit[1] * unit[2] + unit[0] * unit[2]))
    except Exception:
        volume, area = 1.0, 6.0  # Cubo: maior dimensão = 1.
    return MeshMeasure(unit_volume=volume, unit_area=area, method="bounding_box")


def estimate_for_size(*, measure: MeshMeasure, size: ProductSize, params: CostParameters) -> dict:
    side_cm = size.longest_side_mm / 10
    volume_cm3 = measure.unit_volume * side_cm**3
    area_cm2 = measure.unit_area * side_cm**2
    wall_cm = float(params.wall_mm) / 10
    shell_cm3 = min(area_cm2 * wall_cm, volume_cm3)
    solid_cm3 = shell_cm3 + float(params.infill_fraction) * (volume_cm3 - shell_cm3)
    part_grams = solid_cm3 * float(params.density_g_cm3)
    grams = part_grams + float(params.purge_grams)
    hours = grams / float(params.grams_per_hour)
    cost = (
        grams * float(params.cost_per_gram_cents)
        + hours * float(params.cost_per_hour_cents)
        + params.packaging_cents
    )
    fee = size.price_cents * float(params.gateway_fee_fraction)
    margin = (size.price_cents - cost - fee) / size.price_cents
    return {
        "grams": grams,
        "hours": hours,
        "cost_cents": int(round(cost)),
        "margin_fraction": margin,
        "is_blocked": margin < float(params.min_margin_fraction),
    }


def apply_estimates(*, model: Model3D, measure: MeshMeasure) -> None:
    """Grava a medida e uma estimativa por tamanho ativo. Chamado pelo worker depois do 3D."""
    params = CostParameters.objects.order_by("-version").first()
    model.unit_volume = measure.unit_volume
    model.unit_area = measure.unit_area
    model.estimate_method = measure.method
    model.save(update_fields=["unit_volume", "unit_area", "estimate_method", "updated_at"])
    for size in ProductSize.objects.filter(is_active=True):
        values = estimate_for_size(measure=measure, size=size, params=params)
        CostEstimate.objects.update_or_create(
            model=model, size=size, defaults={"parameters": params, **values}
        )


def blocked_size_ids(model: Model3D | None) -> set[int]:
    if model is None:
        return set()
    return set(model.cost_estimates.filter(is_blocked=True).values_list("size_id", flat=True))
