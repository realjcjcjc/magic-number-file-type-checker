# Normalize and validate input paths
# Expand directories into file paths
# Handle recursion flag for directories
# Collect "problems" without crashing

import os

from filetype_checker.error import (
    FtcheckError,
    NotARegularFileError,
    PathNotFoundError,
    PermissionDeniedError,
)


def expand_path(path: str, recursive: bool) -> tuple[list[str], list[FtcheckError]]:
    file_paths = []
    problems = []

    def _on_walk_error(e: OSError) -> None:
        code = "EACCES" if isinstance(e, PermissionError) else "EIO"
        problems.append(
            FtcheckError(
                code=code,
                message=f"Error accessing path: {path}",
                details={"path": path, "os_error": str(e)},
            )
        )

    try:
        os.lstat(path)
    except FileNotFoundError:
        problems.append(PathNotFoundError(path))
        return file_paths, problems
    except PermissionError:
        problems.append(PermissionDeniedError(path))
        return file_paths, problems
    except OSError as e:
        problems.append(
            FtcheckError(
                code="EIO",
                message=f"Error accessing path: {path}",
                details={"path": path, "os_error": str(e)},
            )
        )
        return file_paths, problems
    if os.path.isfile(path):
        file_paths.append(path)
        return file_paths, problems
    elif os.path.isdir(path):
        try:
            if recursive:
                for root, _, files in os.walk(path, onerror=_on_walk_error):
                    for name in files:
                        file_paths.append(os.path.join(root, name))
            else:
                with os.scandir(path) as entries:
                    for entry in entries:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                file_paths.append(entry.path)
                        except PermissionError:
                            problems.append(
                                PermissionDeniedError(
                                    entry.path,
                                    message=f"Permission denied: {entry.path}",
                                )
                            )
                        except OSError as e:
                            problems.append(
                                FtcheckError(
                                    code="EIO",
                                    message=f"Error accessing path: {entry.path}",
                                    details={"path": entry.path, "os_error": str(e)},
                                )
                            )
        except PermissionError:
            problems.append(PermissionDeniedError(path, message=f"Permission denied: {path}"))
        except OSError as e:
            problems.append(
                FtcheckError(
                    code="EIO",
                    message=f"Error accessing path: {path}",
                    details={"path": path, "os_error": str(e)},
                )
            )
    else:
        problems.append(NotARegularFileError(path))

    return file_paths, problems


def expand_paths(paths: list[str], recursive: bool) -> tuple[list[str], list[FtcheckError]]:
    all_file_paths = []
    all_problems = []

    for path in paths:
        file_paths, problems = expand_path(path, recursive)
        all_file_paths.extend(file_paths)
        all_problems.extend(problems)

    all_file_paths = sorted(set(all_file_paths))
    return all_file_paths, all_problems
