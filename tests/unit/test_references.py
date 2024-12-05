from collections import defaultdict
from unittest.mock import call

import pytest

from qualibrate_config.references import models as ref_models
from qualibrate_config.references import resolvers as ref_resolvers
from qualibrate_config.references.models import Reference


@pytest.fixture
def config_with_refs():
    return {
        "qual": {"project": "my_project"},
        "data_handler": {
            "root": "/data/${#/data_handler/project}/subpath",
            "project": "${#/qual/project}",
        },
        "sub": {
            "item": {
                "path": "path_${#/data_handler/root}_project_${#/qual/project}"
            }
        },
    }


@pytest.fixture
def path_with_refs():
    return {
        "/data_handler/root": ref_models.PathWithSolvingReferences(
            config_path="/data_handler/root",
            value=None,
            solved=False,
            references=[
                ref_models.Reference(
                    config_path="/data_handler/root",
                    reference_path="/data_handler/project",
                    index_start=6,
                    index_end=30,
                    value=None,
                    solved=False,
                )
            ],
        ),
        "/data_handler/project": ref_models.PathWithSolvingReferences(
            config_path="/data_handler/project",
            value=None,
            solved=False,
            references=[
                ref_models.Reference(
                    config_path="/data_handler/project",
                    reference_path="/qual/project",
                    index_start=0,
                    index_end=16,
                    value=None,
                    solved=False,
                )
            ],
        ),
        "/sub/item/path": ref_models.PathWithSolvingReferences(
            config_path="/sub/item/path",
            value=None,
            solved=False,
            references=[
                ref_models.Reference(
                    config_path="/sub/item/path",
                    reference_path="/data_handler/root",
                    index_start=5,
                    index_end=26,
                    value=None,
                    solved=False,
                ),
                ref_models.Reference(
                    config_path="/sub/item/path",
                    reference_path="/qual/project",
                    index_start=36,
                    index_end=52,
                    value=None,
                    solved=False,
                ),
            ],
        ),
    }


def test_find_references_no_references(mocker):
    mock_find_refs = mocker.patch(
        "qualibrate_config.references.resolvers.find_references_in_str",
        return_value=list(),
    )
    config = {"base": "${#/ref}"}
    result = ref_resolvers.find_references_from_base(config, "/base")
    assert result == set()
    mock_find_refs.assert_called_once_with(config["base"], "/base")


def test_find_references_valid(mocker):
    doc = {
        "base": "${#/nested/ref1}",
        "nested": {"ref1": "${#/nested/ref2}", "ref2": "value"},
    }
    ref_base = Reference(
        config_path="/base",
        reference_path="/nested/ref1",
        index_start=0,
        index_end=15,
    )
    ref_nested = Reference(
        config_path="/nested/ref1",
        reference_path="/nested/ref2",
        index_start=0,
        index_end=15,
    )
    find_references_in_str = [[ref_base], [ref_nested], []]
    mocked_find_ref_in_str = mocker.patch(
        "qualibrate_config.references.resolvers.find_references_in_str",
        side_effect=find_references_in_str,
    )
    result = ref_resolvers.find_references_from_base(doc, "/base")
    assert result == {ref_base, ref_nested}
    mocked_find_ref_in_str.assert_has_calls(
        [
            call("${#/nested/ref1}", "/base"),
            call("${#/nested/ref2}", "/nested/ref1"),
        ]
    )


def test_find_references_cyclic(mocker):
    doc = {"base": "${#/cyclic}", "cyclic": "${#/cyclic}"}
    ref_base = Reference(
        config_path="/base",
        reference_path="/cyclic",
        index_start=0,
        index_end=15,
    )
    ref_cyclic = Reference(
        config_path="/cyclic",
        reference_path="/cyclic",
        index_start=0,
        index_end=15,
    )
    find_references_in_str = [[ref_base], [ref_cyclic], [ref_cyclic]]
    mocked_find_ref_in_str = mocker.patch(
        "qualibrate_config.references.resolvers.find_references_in_str",
        side_effect=find_references_in_str,
    )
    result = ref_resolvers.find_references_from_base(doc, "/base")
    assert result == {ref_base, ref_cyclic}
    mocked_find_ref_in_str.assert_has_calls(
        [
            call("${#/cyclic}", "/base"),
            call("${#/cyclic}", "/cyclic"),
            call("${#/cyclic}", "/cyclic"),
        ]
    )
    assert mocked_find_ref_in_str.call_count == 3


def test_find_references_unresolvable(mocker):
    broken_ref = Reference(
        config_path="/base",
        reference_path="/missing",
        index_start=0,
        index_end=15,
    )
    mocker.patch(
        "qualibrate_config.references.resolvers.find_references_in_str",
        return_value=[broken_ref],
    )
    with pytest.raises(
        ValueError, match=f"Reference {broken_ref} can't be resolved"
    ):
        ref_resolvers.find_references_from_base(
            {"base": "${#/missing}"}, "/base"
        )


def test_find_all_references_mapping_item(mocker):
    find_ref_spy = mocker.spy(ref_resolvers, "find_all_references")
    assert ref_resolvers.find_all_references({"key": {"a": 1}}) == []
    assert find_ref_spy.call_count == 2

    find_ref_spy.assert_has_calls(
        (call({"key": {"a": 1}}), call({"a": 1}, ["key"]))
    )


def test_find_all_references_string_single_ref(mocker):
    find_ref_spy = mocker.spy(ref_resolvers, "find_all_references")
    expected_ref = ref_models.Reference(
        config_path="/key",
        reference_path="/ref",
        index_start=0,
        index_end=7,
        value=None,
        solved=False,
    )
    assert ref_resolvers.find_all_references({"key": "${#/ref}"}) == [
        expected_ref
    ]
    assert find_ref_spy.call_count == 1


def test_find_all_references_string_multi_ref(mocker):
    find_ref_spy = mocker.spy(ref_resolvers, "find_all_references")
    assert ref_resolvers.find_all_references(
        {"key": "${#/ref}_${#/other}"}
    ) == [
        ref_models.Reference(
            config_path="/key",
            reference_path="/ref",
            index_start=0,
            index_end=7,
            value=None,
            solved=False,
        ),
        ref_models.Reference(
            config_path="/key",
            reference_path="/other",
            index_start=9,
            index_end=18,
            value=None,
            solved=False,
        ),
    ]
    assert find_ref_spy.call_count == 1


def test_find_all_references_string_no_ref(mocker):
    find_ref_spy = mocker.spy(ref_resolvers, "find_all_references")
    assert (
        ref_resolvers.find_all_references(
            {"k1": 1, "k2": "$#/aa", "k3": "value"}
        )
        == []
    )
    assert find_ref_spy.call_count == 1


def test_find_all_references_complex(config_with_refs):
    assert ref_resolvers.find_all_references(config_with_refs) == [
        ref_models.Reference(
            config_path="/data_handler/root",
            reference_path="/data_handler/project",
            index_start=6,
            index_end=30,
            value=None,
            solved=False,
        ),
        ref_models.Reference(
            config_path="/data_handler/project",
            reference_path="/qual/project",
            index_start=0,
            index_end=16,
            value=None,
            solved=False,
        ),
        ref_models.Reference(
            config_path="/sub/item/path",
            reference_path="/data_handler/root",
            index_start=5,
            index_end=26,
            value=None,
            solved=False,
        ),
        ref_models.Reference(
            config_path="/sub/item/path",
            reference_path="/qual/project",
            index_start=36,
            index_end=52,
            value=None,
            solved=False,
        ),
    ]


def test_check_cycles_in_references_exists():
    assert ref_resolvers.check_cycles_in_references(
        {"a": ("b", "c"), "b": ("c", "d"), "c": ("a",)}
    ) == (True, ["a", "b", "c", "a"])


def test_check_cycles_in_references_not_exists():
    assert ref_resolvers.check_cycles_in_references(
        {"a": ("b", "d"), "b": ("c", "e"), "c": ("d",)}
    ) == (False, None)


def test__resolve_references_no_subref(config_with_refs, path_with_refs):
    solved_references = {}
    assert (
        ref_resolvers._resolve_references(
            "/data_handler/project",
            path_with_refs,
            config_with_refs,
            solved_references,
        )
        is None
    )
    assert solved_references == {
        "/qual/project": "my_project",
        "/data_handler/project": "my_project",
    }
    config_item = path_with_refs["/data_handler/project"]
    assert config_item.solved
    assert config_item.value == "my_project"
    assert config_item.references == [
        ref_models.Reference(
            config_path="/data_handler/project",
            reference_path="/qual/project",
            index_start=0,
            index_end=16,
            value="my_project",
            solved=True,
        )
    ]


def test__resolve_references_with_subref(config_with_refs, path_with_refs):
    solved_references = {}
    assert (
        ref_resolvers._resolve_references(
            "/sub/item/path",
            path_with_refs,
            config_with_refs,
            solved_references,
        )
        is None
    )
    assert solved_references == {
        "/qual/project": "my_project",
        "/data_handler/project": "my_project",
        "/data_handler/root": "/data/my_project/subpath",
        "/sub/item/path": "path_/data/my_project/subpath_project_my_project",
    }
    assert path_with_refs == {
        "/data_handler/root": ref_models.PathWithSolvingReferences(
            config_path="/data_handler/root",
            value="/data/my_project/subpath",
            solved=True,
            references=[
                ref_models.Reference(
                    config_path="/data_handler/root",
                    reference_path="/data_handler/project",
                    index_start=6,
                    index_end=30,
                    value="my_project",
                    solved=True,
                )
            ],
        ),
        "/data_handler/project": ref_models.PathWithSolvingReferences(
            config_path="/data_handler/project",
            value="my_project",
            solved=True,
            references=[
                ref_models.Reference(
                    config_path="/data_handler/project",
                    reference_path="/qual/project",
                    index_start=0,
                    index_end=16,
                    value="my_project",
                    solved=True,
                )
            ],
        ),
        "/sub/item/path": ref_models.PathWithSolvingReferences(
            config_path="/sub/item/path",
            value="path_/data/my_project/subpath_project_my_project",
            solved=True,
            references=[
                ref_models.Reference(
                    config_path="/sub/item/path",
                    reference_path="/data_handler/root",
                    index_start=5,
                    index_end=26,
                    value="/data/my_project/subpath",
                    solved=True,
                ),
                ref_models.Reference(
                    config_path="/sub/item/path",
                    reference_path="/qual/project",
                    index_start=36,
                    index_end=52,
                    value="my_project",
                    solved=True,
                ),
            ],
        ),
    }


def test_no_cycle_or_error_with_cycle(mocker):
    cycle = ["a", "b", "a"]
    patched_check_cycles = mocker.patch(
        "qualibrate_config.references.resolvers.check_cycles_in_references",
        return_value=(True, cycle),
    )
    with pytest.raises(ValueError) as ex:
        ref_resolvers.no_cycle_or_error(
            [
                Reference(
                    config_path="a",
                    reference_path="/b",
                    index_start=0,
                    index_end=4,
                ),
                Reference(
                    config_path="b",
                    reference_path="/a",
                    index_start=0,
                    index_end=4,
                ),
            ]
        )
    patched_check_cycles.assert_called_once_with(
        defaultdict(list, **{"a": ["/b"], "b": ["/a"]})
    )
    assert ex.type is ValueError
    assert ex.value.args == (f"Config contains cycle: {cycle}",)


def test_no_cycle_or_error_no_cycle(mocker):
    patched_check_cycles = mocker.patch(
        "qualibrate_config.references.resolvers.check_cycles_in_references",
        return_value=(False, None),
    )
    assert (
        ref_resolvers.no_cycle_or_error(
            [
                Reference(
                    config_path="a",
                    reference_path="/b",
                    index_start=0,
                    index_end=4,
                ),
                Reference(
                    config_path="b",
                    reference_path="/c",
                    index_start=0,
                    index_end=4,
                ),
            ]
        )
        is None
    )
    patched_check_cycles.assert_called_once_with(
        defaultdict(list, **{"a": ["/b"], "b": ["/c"]})
    )


def test_resolve_single_item_value_found(mocker):
    doc = {"key": "resolved"}
    references = {
        ref_models.Reference(
            config_path="/data_handler/root",
            reference_path="/data_handler/project",
            index_start=0,
            index_end=15,
        )
    }
    mocked_find_ref = mocker.patch(
        "qualibrate_config.references.resolvers.find_references_from_base",
        return_value=references,
    )
    mocked_resolve_common = mocker.patch(
        "qualibrate_config.references.resolvers._resolve_common",
        return_value={
            "/_qualibrate_ref_to_resolve": ref_models.PathWithSolvingReferences(
                config_path="/_qualibrate_ref_to_resolve",
                value="resolved",
                solved=True,
                references=[],
            )
        },
    )
    to_resolve = "${#/key}"
    assert ref_resolvers.resolve_single_item(doc, to_resolve) == "resolved"
    updated_config = {**doc, "_qualibrate_ref_to_resolve": to_resolve}
    mocked_find_ref.assert_called_once_with(
        updated_config, "/_qualibrate_ref_to_resolve"
    )
    mocked_resolve_common.assert_called_once_with(
        updated_config, list(references)
    )


def test_resolve_single_item_value_not_found(mocker):
    doc = {"key": "resolved"}
    mocked_find_ref = mocker.patch(
        "qualibrate_config.references.resolvers.find_references_from_base",
        return_value=set(),
    )
    mocked_resolve_common = mocker.patch(
        "qualibrate_config.references.resolvers._resolve_common",
        return_value={},
    )
    to_resolve = "${#/key}"
    assert ref_resolvers.resolve_single_item(doc, to_resolve) is None
    updated_config = {**doc, "_qualibrate_ref_to_resolve": to_resolve}
    mocked_find_ref.assert_called_once_with(
        updated_config, "/_qualibrate_ref_to_resolve"
    )
    mocked_resolve_common.assert_called_once_with(updated_config, list())


def test_resolve_references_full_no_subref():
    doc = {"a": "b", "c": {"d": 2}}
    assert ref_resolvers.resolve_references(doc) == doc


def test_resolve_references_full_with_subref(config_with_refs):
    assert ref_resolvers.resolve_references(config_with_refs) == {
        "qual": {"project": "my_project"},
        "data_handler": {
            "root": "/data/my_project/subpath",
            "project": "my_project",
        },
        "sub": {
            "item": {"path": "path_/data/my_project/subpath_project_my_project"}
        },
    }
