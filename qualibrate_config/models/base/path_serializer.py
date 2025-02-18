from os import sep as os_sep
from pathlib import Path

from qualibrate_config.references.resolvers import TEMPLATE_START

__all__ = ["PathSerializer"]


class PathSerializer:
    @staticmethod
    def serialize_path(path: Path) -> str:
        str_path = str(path)
        if os_sep == "/":
            return str_path
        t_start_idx = str_path.find(TEMPLATE_START)
        while t_start_idx != -1:
            t_end_idx = str_path.find("}", t_start_idx)
            if t_end_idx == -1:
                return str_path
            new_ref = str_path[t_start_idx:t_end_idx].replace(os_sep, "/")
            str_path = str_path.replace(
                str_path[t_start_idx:t_end_idx], new_ref
            )
            t_start_idx = str_path.find(TEMPLATE_START, t_end_idx + 1)
        return str_path
