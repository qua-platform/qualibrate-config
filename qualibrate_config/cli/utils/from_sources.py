import functools
import warnings

from qualibrate_config.cli.utils import deprecated_alias
from qualibrate_config.core import from_sources as _from_source_content

__all__ = _from_source_content.__all__

deprecated_m = "qualibrate_config.cli.utils.from_sources"
new_m = "qualibrate_config.core.from_sources"
warnings.warn(
    (
        f"Module '{deprecated_m}' is deprecated and will be removed in a "
        f"future version. Please use '{new_m}' instead."
    ),
    DeprecationWarning,
    stacklevel=2,
)

l_deprecated = functools.partial(
    deprecated_alias, deprecated_module=deprecated_m, new_module=new_m
)

# Apply decorator to each re-exported function
get_config_by_args_mapping = l_deprecated(
    name="get_config_by_args_mapping",
)(_from_source_content.get_config_by_args_mapping)
get_optional_config = l_deprecated(name="get_optional_config")(
    _from_source_content.get_optional_config
)
not_default = l_deprecated(name="write_config")(
    _from_source_content.not_default
)
qualibrate_config_from_sources = l_deprecated(
    name="qualibrate_config_from_sources"
)(_from_source_content.qualibrate_config_from_sources)
