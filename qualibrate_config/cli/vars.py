CONFIG_PATH_HELP = (
    "Path to the configuration file. If the path points to a file, it will "
    "be read and the old configuration will be reused, except for the "
    "variables specified by the user. If the file does not exist, a new one"
    " will be created. If the path points to a directory, a check will be "
    "made to see if files with the default name exist."
)
CALIBRATION_LIBRARY_FOLDER_HELP = (
    "Path to the folder contains calibration nodes and graphs."
)
STORAGE_LOCATION_HELP = (
    "Path to the local user storage. Used for storing nodes output data."
)
QUAM_STATE_PATH_HELP = "Path to the quam state."
SINGLE_BACKEND_DEPRECATION_MSG = (
    "'{option}' is deprecated and no longer has any effect. As of "
    "QUAlibrate 1.5.0, QUAlibrate runs as a single built-in backend and no "
    "longer spawns or connects to a separate app/runner service."
)
