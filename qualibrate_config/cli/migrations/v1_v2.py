from typing import Any, Optional

from qualibrate_config.cli.migrations.base import MigrateBase


class Migrate(MigrateBase):
    from_version: int = 1
    to_version: int = 2

    @staticmethod
    def backward(data: dict[str, Any]) -> dict[str, Any]:
        qualibrate = data.pop("qualibrate")
        qualibrate.pop("version")
        qualibrate["config_version"] = 1

        app = qualibrate.pop("app", None)
        runner = qualibrate.pop("runner", None)
        composite = qualibrate.pop("composite", None)
        calibration_lib = qualibrate.pop("calibration_library", None)
        new_data = {
            "qualibrate": qualibrate,
        }
        if app:
            if runner:
                app["runner"] = runner
            new_data["qualibrate_app"] = app
        if composite:
            if runner:
                composite["runner"].update(runner)
            new_data["qualibrate_composite"] = composite
        if calibration_lib:
            new_data["qualibrate_runner"] = {
                "calibration_library_resolver": calibration_lib["resolver"],
                "calibration_library_folder": calibration_lib["folder"],
            }
        return new_data

    @staticmethod
    def forward(data: dict[str, Any]) -> dict[str, Any]:
        new_qualibrate = data.pop("qualibrate")
        new_qualibrate.pop("config_version")
        q_app: Optional[dict[str, Any]] = data.pop("qualibrate_app", None)
        q_composite: Optional[dict[str, Any]] = data.pop(
            "qualibrate_composite", None
        )
        q_runner: Optional[dict[str, Any]] = data.pop("qualibrate_runner", None)
        data.pop("active_machine", None)

        if q_app:
            new_qualibrate["app"] = {
                "static_site_files": q_app["static_site_files"]
            }
        if remote_runner := (
            (q_composite and q_composite.get("runner"))
            or (q_app and q_app.get("runner"))
        ):
            new_runner = {}
            if "address" in remote_runner:
                new_runner["address"] = remote_runner["address"]
            if "timeout" in remote_runner:
                new_runner["timeout"] = remote_runner["timeout"]
            if new_runner:
                new_qualibrate["runner"] = new_runner
        if q_composite:
            new_qualibrate["composite"] = {
                "app": {"spawn": q_composite["app"]["spawn"]},
                "runner": {"spawn": q_composite["runner"]["spawn"]},
            }
        if q_runner:
            new_qualibrate["calibration_library"] = {
                "resolver": q_runner["calibration_library_resolver"],
                "folder": q_runner["calibration_library_folder"],
            }
        new_qualibrate["version"] = Migrate.to_version
        new_data = {"qualibrate": new_qualibrate, **data}
        return new_data
