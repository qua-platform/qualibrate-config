import functools
import warnings

from qualibrate_config.cli.utils import deprecated_class_alias
from qualibrate_config.core.migration.migrations import base as _base_content

deprecated_m = "qualibrate_config.cli.migrations.base"
new_m = "qualibrate_config.core.migration.migrations.base"

warnings.warn(
    (
        f"Module '{deprecated_m}' is deprecated and will be removed in a "
        f"future version. Please use '{new_m}' instead."
    ),
    DeprecationWarning,
    stacklevel=2,
)

cl_deprecated = functools.partial(
    deprecated_class_alias, deprecated_module=deprecated_m, new_module=new_m
)
# Apply decorator to each re-exported function
MigrateBase = cl_deprecated(name="MigrateBase")(_base_content.MigrateBase)
