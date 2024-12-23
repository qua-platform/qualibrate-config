from collections import defaultdict
from collections.abc import Mapping, Sequence
from queue import Queue
from typing import Any, Optional, cast

import jsonpatch
import jsonpointer

from qualibrate_config.qulibrate_types import RawConfigType
from qualibrate_config.references.models import (
    PathWithSolvingReferences,
    Reference,
)

TEMPLATE_START = "${#"


def find_references_in_str(
    to_search: str, config_path: str
) -> Sequence[Reference]:
    to_resolve: list[Reference] = []
    template_start_index = to_search.find(TEMPLATE_START)
    while template_start_index != -1:
        template_end_index = to_search.find("}", template_start_index)
        if template_end_index == -1:
            return to_resolve
        to_resolve.append(
            Reference(
                config_path=config_path,
                reference_path=to_search[
                    template_start_index + 3 : template_end_index
                ].strip(),
                index_start=template_start_index,
                index_end=template_end_index,
            )
        )
        template_start_index = to_search.find(
            TEMPLATE_START, template_end_index + 1
        )
    return to_resolve


def find_references_from_base(
    document: Mapping[str, Any],
    path: str,
) -> set[Reference]:
    value = jsonpointer.resolve_pointer(document, path)
    references_in_base = find_references_in_str(value, path)
    if len(references_in_base) == 0:
        return set()
    queue: Queue[Reference] = Queue()
    for ref in references_in_base:
        queue.put(ref)
    references_to_resolve: set[Reference] = set()
    config_paths: set[str] = set()
    while not queue.empty():
        ref = queue.get()
        references_to_resolve.add(ref)
        if ref.reference_path in config_paths:
            return references_to_resolve
        config_paths.add(ref.config_path)
        try:
            value = jsonpointer.resolve_pointer(document, ref.reference_path)
        except jsonpointer.JsonPointerException as ex:
            raise ValueError(f"Reference {ref} can't be resolved") from ex
        if not isinstance(value, str):
            continue
        references_in_base = find_references_in_str(value, ref.reference_path)
        if len(references_in_base) > 0:
            for ref in references_in_base:
                queue.put(ref)
    return references_to_resolve


def find_all_references(
    document: Mapping[str, Any], current_path: Optional[list[str]] = None
) -> Sequence[Reference]:
    if current_path is None:
        current_path = []
    to_resolve: list[Reference] = []
    for key, value in document.items():
        if isinstance(value, Mapping):
            to_resolve.extend(find_all_references(value, current_path + [key]))
        elif isinstance(value, str):
            config_path = "/" + "/".join(current_path + [key])
            to_resolve.extend(find_references_in_str(value, config_path))
    return to_resolve


def check_cycles_in_references(
    references: Mapping[str, Sequence[str]],
) -> tuple[bool, Optional[Sequence[str]]]:
    """Return True if the references has a cycle.

    >>> check_cycles_in_references({"a": ("b",), "b": ("c",), "c": ("a",)})
    (True, ['a', 'b', 'c', 'a'])
    >>> check_cycles_in_references({"a": ("b",), "b": ("c",), "c": ("d",)})
    (False, None)

    """
    path: list[str] = []
    visited: set[str] = set()
    cycled_item: str = ""

    def visit(vertex: str) -> bool:
        nonlocal cycled_item
        if vertex in visited:
            return False
        visited.add(vertex)
        path.append(vertex)
        for neighbour in references.get(vertex, ()):
            if neighbour in path or visit(neighbour):
                cycled_item = vertex
                return True
        path.pop()  # == path.remove(vertex):
        return False

    if any(visit(v) for v in references):
        return True, [*path, cycled_item]
    return False, None


def _resolve_references(
    path: str,
    path_with_references: dict[str, PathWithSolvingReferences],
    original_config: Mapping[str, Any],
    solved_references: dict[str, Any],
) -> None:
    if path_with_references[path].solved:
        # path already solved
        return
    config_item = path_with_references[path]
    references: list[Reference] = config_item.references
    not_solved_refs = filter(lambda ref: not ref.solved, references)
    for ref in not_solved_refs:
        if ref.reference_path in solved_references:
            ref.value = solved_references[ref.reference_path]
            ref.solved = True
        elif ref.reference_path in path_with_references:
            _resolve_references(
                ref.reference_path,
                path_with_references,
                original_config,
                solved_references,
            )
            if ref.reference_path not in solved_references:
                raise ValueError(
                    f"Subreference '{ref.reference_path}' "
                    f"for '{ref.config_path}' not solved."
                )
            ref.value = solved_references[ref.reference_path]
            ref.solved = True
        else:
            value = jsonpointer.resolve_pointer(
                original_config, ref.reference_path, None
            )
            if value is None:
                raise ValueError(
                    f"Can't resolve reference item '{ref.reference_path}' "
                    f"for config path '{ref.config_path}'"
                )
            ref.value = value
            ref.solved = True
            solved_references[ref.reference_path] = value
    verify_all_solved = all(map(lambda ref: ref.solved, references))
    if not verify_all_solved:
        not_solved_refs = filter(lambda ref: not ref.solved, references)
        references_errors = (
            (
                f"- config path: '{ref.config_path}', "
                f"reference: '{ref.reference_path}';"
            )
            for ref in not_solved_refs
        )
        raise ValueError(
            "\n".join(
                [
                    "Some issues with solving references. Issued references:",
                    *references_errors,
                ]
            )
        )
    config_value = jsonpointer.resolve_pointer(
        original_config, config_item.config_path, None
    )
    if config_value is None or not isinstance(config_value, str):
        raise ValueError(
            f"Can't resolve config item '{config_item.config_path}'"
        )
    for ref in sorted(
        references, key=lambda ref: ref.index_start, reverse=True
    ):
        config_value = (
            f"{config_value[:ref.index_start]}"
            f"{ref.value}{config_value[ref.index_end + 1:]}"
        )
    config_item.value = config_value
    config_item.solved = True
    solved_references[config_item.config_path] = config_value


def no_cycle_or_error(references: Sequence[Reference]) -> None:
    """Raise error if there is a cycle in reference. Do nothing otherwise.

    Raises:
        ValueError: If cycle found
    """
    references_seq = defaultdict(list)
    for reference in references:
        references_seq[reference.config_path].append(reference.reference_path)
    has_cycles, cycle = check_cycles_in_references(references_seq)
    if has_cycles:
        raise ValueError(f"Config contains cycle: {cycle}")


def _resolve_common(
    document: Mapping[str, Any], references: Sequence[Reference]
) -> dict[str, PathWithSolvingReferences]:
    no_cycle_or_error(references)
    solved_references: dict[str, Any] = {}
    path_with_references: dict[str, PathWithSolvingReferences] = {}
    for reference in references:
        path_with_refs = path_with_references.setdefault(
            reference.config_path,
            PathWithSolvingReferences(config_path=reference.config_path),
        )
        path_with_refs.references.append(reference)
    for path in path_with_references:
        _resolve_references(
            path,
            path_with_references,
            document,
            solved_references,
        )
    return path_with_references


def resolve_single_item(
    config: Mapping[str, Any],
    base: str,
) -> Any:
    custom_config = dict(**config)
    key_to_resolve = "_qualibrate_ref_to_resolve"
    jsonpointer_to_resolve = f"/{key_to_resolve}"
    custom_config[key_to_resolve] = base
    references = find_references_from_base(
        custom_config, jsonpointer_to_resolve
    )
    path_with_references = _resolve_common(custom_config, list(references))
    needed = path_with_references.get(jsonpointer_to_resolve)
    return needed.value if needed else None


def resolve_references(config: RawConfigType) -> RawConfigType:
    references = find_all_references(config)
    path_with_references = _resolve_common(config, references)
    patches = [
        {"op": "replace", "path": path.config_path, "value": path.value}
        for path in path_with_references.values()
    ]
    return cast(RawConfigType, jsonpatch.apply_patch(config, patches))


if __name__ == "__main__":
    _config = {
        "qualibrate": {"project": "my_project"},
        # "qualibrate": {
        #     "subref": "${#/data_handler/root_data_folder}",
        #     "project": "${#/qualibrate/subref}",
        # },
        "data_handler": {
            "root_data_folder": "/data/${#/data_handler/project}/subpath",
            "project": "${#/qualibrate/project}",
            # "project": "${#/qualibrate/project_}",
        },
    }
    res_all = resolve_references(_config)
    # print(_config)
    res = resolve_single_item(
        _config, "/data/${#/data_handler/project}/subpath"
    )
    print(res)
