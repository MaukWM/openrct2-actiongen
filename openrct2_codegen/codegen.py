"""Render Jinja2 templates from an ActionsIR."""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from openrct2_codegen.ir import ActionsIR

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


def render_template(template_name: str, ir: ActionsIR) -> str:
    """Render a codegen template with the given IR.

    template_name: stem of the output file (e.g. "actions.ts").
    Loads templates/{template_name}.j2 and renders it with the IR data.
    """
    j2_file = _TEMPLATES_DIR / f"{template_name}.j2"
    if not j2_file.is_file():
        raise ValueError(f"Unknown template: {template_name!r} (no file at {j2_file})")

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["cpp_class_to_method"] = _cpp_class_to_method
    env.filters["camel_to_snake"] = _camel_to_snake
    env.filters["ir_type_to_py"] = _ir_type_to_py
    template = env.get_template(j2_file.name)

    return template.render(
        generator_version=ir.generator_version,
        openrct2_version=ir.openrct2_version,
        api_version=ir.api_version,
        generated_at=ir.generated_at,
        actions=[a.model_dump() for a in ir.actions],
    )
