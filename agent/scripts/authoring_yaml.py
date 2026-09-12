"""Preserve the indented sequence style accepted by the Studio topic editor."""

import yaml


class IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def represent_string(dumper, value):
    return dumper.represent_scalar(
        "tag:yaml.org,2002:str", value, style="|" if "\n" in value else None,
    )


IndentedSafeDumper.add_representer(str, represent_string)


def dump_authoring_yaml(value):
    return yaml.dump(
        value, Dumper=IndentedSafeDumper, sort_keys=False,
        allow_unicode=True, width=2**31 - 1,
    )
