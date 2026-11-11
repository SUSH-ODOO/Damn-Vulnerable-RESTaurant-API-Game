import re
import shlex
import subprocess

# "df" options that take no argument and are safe to expose.
ALLOWED_DF_OPTIONS = {
    "-a",
    "--all",
    "-h",
    "--human-readable",
    "-H",
    "--si",
    "-i",
    "--inodes",
    "-k",
    "-l",
    "--local",
    "-P",
    "--portability",
    "-T",
    "--print-type",
    "--total",
    "--sync",
    "--no-sync",
}

# Path-like operands (file or mount point); must not start with "-".
SAFE_PATH_PATTERN = re.compile(r"^[A-Za-z0-9_./][A-Za-z0-9_.\-/]*$")


def _build_df_arguments(parameters: str) -> list:
    try:
        tokens = shlex.split(parameters)
    except ValueError:
        raise ValueError("Invalid disk usage parameters")

    arguments = []
    for token in tokens:
        if token.startswith("-"):
            if token not in ALLOWED_DF_OPTIONS:
                raise ValueError("Unsupported disk usage parameter: " + token)
        elif not SAFE_PATH_PATTERN.match(token):
            raise ValueError("Invalid disk usage parameter: " + token)
        arguments.append(token)
    return arguments


def get_disk_usage(parameters: str):
    # Validated before any process is spawned; ValueError signals bad input.
    command = ["df", "-h"] + _build_df_arguments(parameters)

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
        )
        usage = result.stdout.strip().decode()
    except:
        raise Exception("An unexpected error was observed")

    return usage
