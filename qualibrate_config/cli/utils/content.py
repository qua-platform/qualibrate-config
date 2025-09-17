import functools
import warnings

from qualibrate_config.cli.utils import deprecated_alias
from qualibrate_config.core import content as _core_content

__all__ = _core_content.__all__

deprecated_m = "qualibrate_config.cli.utils.content"
new_m = "qualibrate_config.core.content"

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
get_config_file_content = l_deprecated(
    name="get_config_file_content",
)(_core_content.get_config_file_content)
simple_write = l_deprecated(name="simple_write")(_core_content.simple_write)
write_config = l_deprecated(name="write_config")(_core_content.write_config)
