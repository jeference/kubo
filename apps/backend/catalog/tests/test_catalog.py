from __future__ import annotations

from catalog import prompts
from catalog.models import CostParameters, ProductSize


def test_styles_are_public(anon):
    response = anon.get("/api/catalog/styles/")
    assert response.status_code == 200
    assert [style["id"] for style in response.data] == ["free", "pixar", "mini-pop", "chibi"]


def test_sizes_list_only_active(anon):
    ProductSize.objects.filter(code="4cm").update(is_active=False)
    codes = [size["code"] for size in anon.get("/api/catalog/sizes/").data]
    assert "4cm" not in codes
    assert codes[0] == "6cm"


def test_price_table(anon):
    sizes = anon.get("/api/catalog/sizes/").data
    assert [(size["code"], size["price_cents"]) for size in sizes] == [
        ("4cm", 5990),
        ("6cm", 9990),
        ("8cm", 14490),
        ("10cm", 18990),
        ("12cm", 22990),
    ]
    assert [size["code"] for size in sizes if size["is_default"]] == ["6cm"]


def test_seed_has_cost_parameters():
    assert CostParameters.objects.filter(version=1).exists()


def test_prompts_render_every_style():
    for style in prompts.STYLE_IDS:
        assert "dragão" in prompts.text_prompt(style=style, text="Um dragão.")
        assert prompts.photo_prompt(style=style)
        assert "sem chapéu" in prompts.photo_prompt(style=style, request="sem chapéu")
    assert "capa vermelha" in prompts.edit_prompt(instruction="capa vermelha.")
