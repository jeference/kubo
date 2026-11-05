from __future__ import annotations

import numpy as np
import trimesh

from catalog.models import CostParameters, ProductSize
from creations import costing


def _glb(mesh) -> bytes:
    return mesh.export(file_type="glb")


def _sphere_with_hole(hole_ratio: float):
    """Esfera de raio 1 com uma calota aberta."""
    mesh = trimesh.creation.icosphere(subdivisions=5, radius=1.0)
    centers = mesh.triangles_center
    keep = centers[:, 2] < 1 - hole_ratio
    mesh.update_faces(keep)
    return mesh


def test_closed_sphere_volume_is_close_and_not_underestimated():
    measure = costing.measure_mesh(_glb(trimesh.creation.icosphere(subdivisions=5, radius=1.0)))
    # Maior dimensão = 1: esfera de diâmetro 1 tem volume pi/6.
    expected = np.pi / 6
    assert measure.method == "voxel_flood"
    assert 0.9 * expected <= measure.unit_volume <= 1.15 * expected


def test_sphere_with_small_hole_does_not_collapse():
    """Preenchimento simples perderia 96% aqui. Volume baixo é venda com prejuízo."""
    measure = costing.measure_mesh(_glb(_sphere_with_hole(0.002)))
    assert measure.unit_volume >= 0.85 * (np.pi / 6)


def test_area_of_sphere_is_reasonable():
    measure = costing.measure_mesh(_glb(trimesh.creation.icosphere(subdivisions=5, radius=1.0)))
    expected = np.pi  # Área de esfera de diâmetro 1.
    assert 0.7 * expected <= measure.unit_area <= 1.5 * expected


def test_invalid_glb_falls_back_to_worst_case():
    measure = costing.measure_mesh(b"nao e um glb")
    assert measure.method == "bounding_box"
    assert measure.unit_volume == 1.0


def test_flat_mesh_falls_back_or_stays_positive():
    plane = trimesh.creation.box(extents=(1, 1, 0.001))
    measure = costing.measure_mesh(_glb(plane))
    assert measure.unit_volume > 0
    assert measure.unit_area > 0


def test_estimates_scale_and_block_below_margin():
    params = CostParameters.objects.get(version=1)
    small = ProductSize.objects.get(code="4cm")
    big = ProductSize.objects.get(code="15cm")
    measure = costing.MeshMeasure(unit_volume=0.5, unit_area=3.0, method="voxel_flood")
    a = costing.estimate_for_size(measure=measure, size=small, params=params)
    b = costing.estimate_for_size(measure=measure, size=big, params=params)
    assert b["grams"] > a["grams"]
    assert b["cost_cents"] > a["cost_cents"]

    small.price_cents = 100
    blocked = costing.estimate_for_size(measure=measure, size=small, params=params)
    assert blocked["is_blocked"] is True
    assert blocked["margin_fraction"] < 0


def test_worst_case_is_more_expensive_than_measured():
    params = CostParameters.objects.get(version=1)
    size = ProductSize.objects.get(code="10cm")
    sphere = costing.MeshMeasure(unit_volume=np.pi / 6, unit_area=np.pi, method="voxel_flood")
    box = costing.MeshMeasure(unit_volume=1.0, unit_area=6.0, method="bounding_box")
    assert (
        costing.estimate_for_size(measure=box, size=size, params=params)["cost_cents"]
        > costing.estimate_for_size(measure=sphere, size=size, params=params)["cost_cents"]
    )
