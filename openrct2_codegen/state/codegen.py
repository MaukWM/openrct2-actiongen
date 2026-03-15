"""Render Jinja2 templates from a StateIR."""

from pathlib import Path

from openrct2_codegen.render import make_env
from openrct2_codegen.state.ir import StateIR

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _pascal(name: str) -> str:
    """Convert camelCase or lowercase to PascalCase: 'park' → 'Park', 'cash' → 'Cash'."""
    return name[0].upper() + name[1:]


def _literal_value(ts_type: str) -> str | None:
    """Extract string content from a TS literal type: '"ride"' → 'ride', else None."""
    ts_type = ts_type.strip()
    if ts_type.startswith('"') and ts_type.endswith('"'):
        return ts_type[1:-1]
    return None


def _enrich_unions(interfaces, interface_unions):
    """For each union type, compute the discriminator field and per-variant discriminator value."""
    enriched = {}
    for union_name, variant_names in interface_unions.items():
        # Find the discriminator field: first property with a literal ts_type in any variant
        discriminator_field = None
        for variant_name in variant_names:
            iface = interfaces.get(variant_name)
            if not iface:
                continue
            for prop in iface.properties:
                if _literal_value(prop.ts_type) is not None:
                    discriminator_field = prop.name
                    break
            if discriminator_field:
                break

        variants_enriched = []
        for variant_name in variant_names:
            iface = interfaces.get(variant_name)
            disc_value = None
            if discriminator_field and iface:
                for prop in iface.properties:
                    if prop.name == discriminator_field:
                        disc_value = _literal_value(prop.ts_type)
                        break
            variants_enriched.append({
                "name": variant_name,
                "discriminator_value": disc_value,
                "properties": [p.model_dump() for p in iface.properties] if iface else [],
            })

        enriched[union_name] = {
            "discriminator": discriminator_field,
            "variants": variants_enriched,
        }
    return enriched


def render_template(template_name: str, ir: StateIR) -> str:
    """Render a state codegen template with the given IR."""
    j2_file = _TEMPLATES_DIR / f"{template_name}.j2"
    if not j2_file.is_file():
        raise ValueError(f"Unknown template: {template_name!r} (no file at {j2_file})")

    namespace_iface_names = {ns.ts_interface for ns in ir.namespaces}
    union_variant_names = {v for variants in ir.interface_unions.values() for v in variants}

    # Union variant interfaces come first so serializers are defined before the union serializer
    union_variants = [
        ir.interfaces[n].model_dump()
        for n in ir.interfaces
        if n not in namespace_iface_names and n in union_variant_names
    ]
    # All other leaf interfaces (Research, WeatherState, ScenarioObjective, Award, ParkMessage, …)
    other_leaves = [
        ir.interfaces[n].model_dump()
        for n in ir.interfaces
        if n not in namespace_iface_names and n not in union_variant_names
    ]

    enriched_unions = _enrich_unions(ir.interfaces, ir.interface_unions)

    namespaces = []
    for ns in ir.namespaces:
        iface = ir.interfaces[ns.ts_interface]
        namespaces.append({
            "name": ns.name,
            "ts_interface": ns.ts_interface,
            "properties": [p.model_dump() for p in iface.properties],
        })

    env = make_env(_TEMPLATES_DIR, {"pascal": _pascal})
    template = env.get_template(j2_file.name)

    return template.render(
        generator_version=ir.generator_version,
        openrct2_version=ir.openrct2_version,
        api_version=ir.api_version,
        generated_at=ir.generated_at,
        namespaces=namespaces,
        interfaces={k: v.model_dump() for k, v in ir.interfaces.items()},
        enums=ir.enums,
        unions=enriched_unions,
        union_variants=union_variants,
        other_leaves=other_leaves,
    )
