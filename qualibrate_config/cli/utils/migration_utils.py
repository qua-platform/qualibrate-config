import functools
import warnings

from qualibrate_config.cli.utils import deprecated_alias
from qualibrate_config.core.migration import utils as _migration_utils

__all__ = _migration_utils.__all__

deprecated_m = "qualibrate_config.cli.utils.migration_utils"
new_m = "qualibrate_config.core.migration.utils"
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
make_migrations = l_deprecated(
    name="make_migrations",
)(_migration_utils.make_migrations)
