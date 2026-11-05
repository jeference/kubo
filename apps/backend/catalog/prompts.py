"""Estilos e prompts do 2D, ajustados no protótipo contra as referências.

Mudar um prompt exige novo deploy e reteste contra `docs/concorrencia/jujubit/estilos/`.
Suba `PROMPT_VERSION` a cada mudança: cada `ProviderTask` guarda a versão e o texto enviado.
"""

PROMPT_VERSION = "2026-11-03"

MAX_PRINT_COLORS = 4
# Colors we have PLA filament for: name sent to the image model -> hex. Starting values
# are the common PLA colors; replace them with the real stock.
FILAMENT_COLORS = {
    "white": "#FFFFFF",
    "black": "#000000",
    "gray": "#8E9089",
    "red": "#C12E1F",
    "orange": "#FF6A13",
    "yellow": "#F4EE2A",
    "green": "#00AE42",
    "blue": "#0A2989",
    "purple": "#5E43B7",
    "pink": "#F5547C",
    "brown": "#9D432C",
    "beige": "#F7E6DE",
    # Voolt3D PLA "Bege Caucasiano". The maker publishes no hex: sampled from its product photo.
    "light skin": "#EBC8B0",
}
# Opens every prompt that produces a 2D image; at the end of the prompt, GPT Image 2 kept the
# off-list colors of requests and references. Tested 2026-11-02, one image per case: off-list
# colors were replaced in 3 of 4 cases, but only 1 of 6 images stayed within the limit, so
# this lowers the color count without guaranteeing it. No braces: templates go through .format().
_COLOR_RULE = (
    "This figurine is 3D printed, and only these filament colors exist: "
    + ", ".join(f"{name} ({hex_code})" for name, hex_code in FILAMENT_COLORS.items())
    + f". No other color can be printed. Use at most {MAX_PRINT_COLORS} of them on the whole "
    "figurine, counting the base and small details such as eyes, mouth and buttons. Do not "
    "reproduce colors from the request or the reference that are not on the list, such as "
    "turquoise, teal, gold, tan or light blue: repaint them in the closest listed color, "
    "even if that changes how it looks. Each part is one uniform matte color but stays a "
    "sculpted 3D form with volume, never a flat drawing. The white background does not count "
    "as a color. Do not draw the list, color swatches or any text.\n\n"
)

_STANDARDIZE_RULES = (
    "same shape, pose, proportions, clothing, materials and distinctive details, and do not "
    "add anything that is not in the reference. Show it upright in its natural orientation, "
    "and complete any part of an object that is cut off "
    "by the photo or hidden by the camera angle; a character shown only as a head stays only "
    "a head. Captions, signatures and handwriting around the subject are not part of it, and "
    "neither is whatever is underneath it, such as a pedestal, a pier, a table or the ground. "
    "Fur and hair are sculpted as solid shapes. A standing person or character gets a small "
    "plain round base; anything else rests directly on the background. Three-quarter view. "
    "Show the whole figurine alone, centered and large, with a small margin on every side, "
    "isolated on a plain white background."
)

# Closes every prompt for a new image. _COLOR_RULE alone left most images over the limit,
# because the model doesn't know which parts should share a color. Tested 2026-11-03 on 19 text
# and photo cases, one image per case, counted by eye: images within the limit went from 7 to
# 15 of 18 in Mini Pop and from 2 to 14 of 18 in Chibi. It still doesn't guarantee the limit,
# and prints and some original colors are lost. A second pass repainting the image with 4 named
# colors cut more colors but damaged faces and doubled the cost.
_COLOR_PLAN = (
    "\n\nColor plan, more important than color accuracy: the finished figure uses exactly "
    f"{MAX_PRINT_COLORS} colors from the list, no more, and each part is one flat color with no "
    "prints, patterns, stripes or logos. These rules change only the colors, never what the "
    "subject is: every shape, object and feature above stays. Choose by subject. A person or "
    "character: skin is light skin, or brown for dark skin; hair, beard, eyebrows, eyes and shoes "
    "all share one dark color (black or brown); the top is one color; the trousers or skirt are "
    "one color. An animal or toy: its main color, a second color for its next largest part, "
    "black for eyes and nose, and one color for any accessory. An object, vehicle or building: "
    "its 2 or 3 main colors, with every small detail repainted in one of them. Do not add any "
    "person, animal or object that is not in the request or the reference."
)

# Pixar, Mini Pop and Chibi: tuned on GPT Image 2 against Jujubit's styles of the same name, on
# 21 text and photo cases (2026-11-02, docs/concorrencia/jujubit/estilos/). Margin wording:
# "filling the frame" made the figure touch the image border. "child" got a car refused by
# OpenAI's safety system in Chibi, so it says "humanoid character".
_STYLE_FRAME = (
    "centered and large, with a clear white margin on every side so that nothing touches the "
    "edge of the image,"
)
_STYLE_BACKDROP = (
    "isolated on a plain white background with a soft contact shadow and no base or pedestal."
    + _COLOR_PLAN
)
_STYLE_IGNORE = "Ignore the background and whatever is underneath the subject."

_PIXAR_LOOK = "soft rounded stylized forms, clean smooth materials, a warm friendly look."
_PIXAR_ANIMAL = (
    "An animal stays an animal, with its natural body and a friendly cartoon face with big "
    "expressive eyes."
)
# Jujubit's Pixar breaks on objects (returns the photo, or swaps in a person): not copied.
_PIXAR_OBJECT = (
    "If the subject is an object, vehicle or building, show only that thing as a rounded "
    "stylized model, with no people, no face, no eyes, no arms and no legs."
)

_MINI_POP_LOOK = (
    "an oversized wide rounded-square head about half of the total height, with a flat face, "
    "two large solid glossy black round bead eyes set wide apart at mid-face, a tiny "
    "triangular nose and no visible mouth, on a short neck and a small slim body with "
    "separate arms and legs. Hair and clothes are molded as simple smooth shapes, in matte "
    "vinyl."
)
_MINI_POP_OBJECT = (
    "An object, vehicle or building becomes the character: its shape and colors form the "
    "oversized head and the outfit of a small humanoid body."
)

_CHIBI_LOOK = (
    "a large head about 45 percent of the total height, big glossy anime eyes, a tiny nose and "
    "small mouth, a small rounded body with short limbs, hair sculpted as big smooth locks, and "
    "clothes with a polished PVC toy finish."
)
_CHIBI_HUMANOID = (
    "The figure is always a stylized humanoid anime character: an animal becomes a humanoid "
    "character with that animal's ears, tail and coloring, wearing clothes, and an object, "
    "vehicle or building becomes a character holding a small clearly recognizable model of "
    "it, with hair and outfit in its colors."
)

DEFAULT_STYLE = "free"

GENERATION = {
    "IMAGES_PER_PROMPT": 1,
    "IMAGE_SIZE": 1024,
    # Sent with the current image as reference. Tested 2026-11-01: vague requests ("make it
    # prettier") otherwise lose the white background, which the 3D step relies on.
    # Placeholder: {instruction}.
    "EDIT_PROMPT_TEMPLATE": (
        _COLOR_RULE
        + "{instruction}. Keep everything else exactly the same, on a plain white background"
    ),
    # One entry per style the user can pick. PROMPT_TEMPLATE wraps a text description
    # ({prompt}, {prompt_lower}). STANDARDIZE_PROMPT_TEMPLATE turns an uploaded photo into an
    # image of that style; the REQUEST variant is for a photo plus a change ({request}).
    "STYLES": {
        "free": {
            # Matches the 2D references of Jujubit/Tripo. Not retuned for GPT Image 2:
            # tuned on FLUX.2 [klein], the previous image model,
            # against 18 of their images (2026-10-31): a sculpted figurine look (fur and hair
            # as solid shapes, not strands), the whole object centered, and a
            # near-white background (#FDFDFD; theirs is #FCFCFC). FLUX.2 [klein] overreacts to
            # color words: "vivid"/"bright" turn objects rainbow, "natural" goes sepia,
            # "pristine" drains color; "studio lighting" adds a gray vignette.
            "PROMPT_TEMPLATE": (
                _COLOR_RULE
                + "{prompt}, as a detailed 3D figurine, shown whole, centered and filling "
                "the frame, isolated on a plain white background" + _COLOR_PLAN
            ),
            # Tuned for GPT Image 2 against Jujubit's Free Style on 16 photos (2026-11-01).
            # "Whatever is underneath" is what stops it copying pedestals and piers; a broader
            # base rule put a disc under cars and chairs.
            "STANDARDIZE_PROMPT_TEMPLATE": (
                _COLOR_RULE
                + "Create a clean product photograph of a detailed 3D figurine of the main "
                "subject of this reference image. Keep it recognizably the same: "
                + _STANDARDIZE_RULES
                + _COLOR_PLAN
            ),
            "STANDARDIZE_REQUEST_PROMPT_TEMPLATE": (
                _COLOR_RULE
                + "Create a clean product photograph of a detailed 3D figurine of the main "
                "subject of this reference image, with this one change: {request}. Apart from "
                "that change, keep it recognizably the same: " + _STANDARDIZE_RULES + _COLOR_PLAN
            ),
        },
        "pixar": {
            "PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}{{prompt}}, as a 3D model from a modern animated family movie: "
                f"{_PIXAR_LOOK} A person or character has a head only slightly larger than "
                "realistic, large expressive eyes, and is shown full body, standing with the "
                f"arms relaxed at the sides unless described otherwise. {_PIXAR_ANIMAL} "
                f"{_PIXAR_OBJECT} Whole subject alone, {_STYLE_FRAME} with no scene, "
                f"{_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a 3D model "
                f"from a modern animated family movie: {_PIXAR_LOOK} Keep it recognizably the "
                "same: same features, hair, clothing and distinctive details, and do "
                "not add anyone or anything that is not in the reference. If the subject is "
                "one person, or two people side by side, give them a head only slightly larger "
                "than realistic and large expressive eyes, and show them full body, standing "
                "with the arms relaxed at the sides, even if the photo shows only part of "
                f"them. {_PIXAR_ANIMAL} {_PIXAR_OBJECT} {_STYLE_IGNORE} Whole subject alone, "
                f"{_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_REQUEST_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a 3D model "
                "from a modern animated family movie, with this one change: {request}. Style: "
                f"{_PIXAR_LOOK} Apart from that change, keep it recognizably the same: same "
                "features, hair, clothing and distinctive details, and do not add "
                "anyone or anything else. A person has a head only slightly larger than "
                "realistic and large expressive eyes, and is shown full body, standing with "
                f"the arms relaxed at the sides. {_PIXAR_ANIMAL} {_PIXAR_OBJECT} "
                f"{_STYLE_IGNORE} Whole subject alone, {_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
        },
        "mini-pop": {
            "PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}{{prompt}}, as a collectible vinyl bobble-head toy figure: "
                f"{_MINI_POP_LOOK} An animal stands upright in simple clothes. "
                f"{_MINI_POP_OBJECT} Two people stay two people, side by side. Front view, "
                f"standing, shown whole, {_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a collectible "
                f"vinyl bobble-head toy figure: {_MINI_POP_LOOK} Keep it recognizably the same: "
                "same hair, facial hair, clothing and distinctive details. "
                "A person is shown full body, even if the photo shows only part of them. Two "
                "people stay two people, side by side. An animal keeps its animal body on four "
                f"legs, with the same oversized head and bead eyes. {_MINI_POP_OBJECT} "
                f"{_STYLE_IGNORE} Front view, shown whole, {_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_REQUEST_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a collectible "
                "vinyl bobble-head toy figure, with this one change: {request}. Style: "
                f"{_MINI_POP_LOOK} Apart from that change, keep it recognizably the same: same "
                "hair, clothing and distinctive details. An animal keeps "
                f"its animal body, with the same oversized head and bead eyes. "
                f"{_MINI_POP_OBJECT} {_STYLE_IGNORE} Front view, shown whole, {_STYLE_FRAME} "
                f"{_STYLE_BACKDROP}"
            ),
        },
        "chibi": {
            "PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}{{prompt}}, as a Japanese chibi anime collectible figure: "
                f"{_CHIBI_LOOK} The figure is always a stylized humanoid anime character. An "
                "animal becomes a humanoid character with that animal's ears, tail and "
                "coloring, wearing clothes. An object, vehicle or building becomes a character "
                "holding a small clearly recognizable model of it, with hair and outfit in its "
                "colors. Two people stay two people, side by side. Requested words appear large "
                f"on the outfit. Standing, shown whole, {_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a Japanese "
                f"chibi anime collectible figure: {_CHIBI_LOOK} Keep it recognizably the same: "
                "same hair, facial hair, clothing and distinctive details. "
                "A person is shown full body, even if the photo shows only part of them. Two "
                "people stay two people, side by side. Requested words appear large on the "
                f"outfit. {_CHIBI_HUMANOID} {_STYLE_IGNORE} Standing, shown whole, "
                f"{_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
            "STANDARDIZE_REQUEST_PROMPT_TEMPLATE": (
                f"{_COLOR_RULE}Turn the main subject of this reference image into a Japanese "
                "chibi anime collectible figure, with this one change: {request}. Style: "
                f"{_CHIBI_LOOK} Apart from that change, keep it recognizably the same: same "
                f"hair, clothing and distinctive details. {_CHIBI_HUMANOID} "
                f"{_STYLE_IGNORE} Standing, shown whole, {_STYLE_FRAME} {_STYLE_BACKDROP}"
            ),
        },
    },
}


_LABELS = {
    "free": "Livre",
    "pixar": "Pixar",
    "mini-pop": "Mini Pop",
    "chibi": "Chibi",
}
STYLE_IDS = tuple(GENERATION["STYLES"])


def public_styles() -> list[dict]:
    return [
        {"id": style, "label": _LABELS[style], "thumbnail": f"/styles/{style}.webp"}
        for style in STYLE_IDS
    ]


def text_prompt(*, style: str, text: str) -> str:
    subject = text.strip().rstrip(".")
    return GENERATION["STYLES"][style]["PROMPT_TEMPLATE"].format(
        prompt=subject, prompt_lower=subject[:1].lower() + subject[1:]
    )


def photo_prompt(*, style: str, request: str = "") -> str:
    templates = GENERATION["STYLES"][style]
    request = request.strip().rstrip(".")
    if not request:
        return templates["STANDARDIZE_PROMPT_TEMPLATE"]
    return templates["STANDARDIZE_REQUEST_PROMPT_TEMPLATE"].format(request=request)


def edit_prompt(*, instruction: str) -> str:
    return GENERATION["EDIT_PROMPT_TEMPLATE"].format(instruction=instruction.strip().rstrip("."))
