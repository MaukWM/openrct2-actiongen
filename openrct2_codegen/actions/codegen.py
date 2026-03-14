"""Render Jinja2 templates from an ActionsIR."""

import re
from pathlib import Path

from openrct2_codegen.actions.ir import ActionsIR
from openrct2_codegen.render import make_env

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _cpp_class_to_method(cpp_class: str) -> str:
    """Convert a C++ action class name to a Python method name.

    RideCreateAction -> ride_create
    BalloonPressAction -> balloon_press
    """
    name = cpp_class.removesuffix("Action")
    return re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name).lower()


def _camel_to_snake(name: str) -> str:
    """Convert a camelCase parameter name to snake_case.

    primaryColour -> primary_colour
    rideType -> ride_type
    """
    return re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name).lower()


def _ir_type_to_py(ir_type: str) -> str:
    """Map an IR type string to a Python type annotation string.

    number -> int
    boolean -> bool
    string -> str
    """
    return {"number": "int", "boolean": "bool", "string": "str"}[ir_type]


_FILTERS = {
    "cpp_class_to_method": _cpp_class_to_method,
    "camel_to_snake": _camel_to_snake,
    "ir_type_to_py": _ir_type_to_py,
}


def render_template(template_name: str, ir: ActionsIR) -> str:
    """Render an actions codegen template with the given IR."""
    j2_file = _TEMPLATES_DIR / f"{template_name}.j2"
    if not j2_file.is_file():
        raise ValueError(f"Unknown template: {template_name!r} (no file at {j2_file})")

    env = make_env(_TEMPLATES_DIR, _FILTERS)
    template = env.get_template(j2_file.name)

    return template.render(
        generator_version=ir.generator_version,
        openrct2_version=ir.openrct2_version,
        api_version=ir.api_version,
        generated_at=ir.generated_at,
        actions=[a.model_dump() for a in ir.actions],
    )
