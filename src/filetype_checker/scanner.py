# Normalize and validate input paths
# Expand directories into file paths
# Handle recursion flag for directories
# Collect "problems" without crashing

import os


def expand_path(path: str, recursive: bool) -> tuple[list[str], list[dict]]:
    file_paths = []
    problems = []

    if not os.path.exists(path):
        problems.append({
            "code": "ENOENT",
            "message": f"File not found: {path}",
            "details": {"path": path},
        })
        return file_paths, problems
    elif os.path.isfile(path):
        file_paths.append(path)
        return file_paths, problems
    elif os.path.isdir(path):
        try: 
            if recursive:
                for root, _, files in os.walk(path):
                    for name in files:
                        file_paths.append(os.path.join(root, name))
            else:
                with os.scandir(path) as entries:
                    for entry in entries:
                        if entry.is_file():
                            file_paths.append(entry.path)
        except PermissionError as e:
            problems.append({
                "code": "EACCES",
                "message": f"Permission denied: {path}",
                "details": {"path": path, "error": str(e)},
            })
        except OSError as e:
            problems.append({
                "code": "EIO",
                "message": f"Error accessing path: {path}",
                "details": {"path": path, "error": str(e)},
            })
    else:
        problems.append({
            "code": "ENOTFILE",
            "message": f"Not a regular file or directory: {path}",
            "details": {"path": path},
        })


    file_paths.sort()
    return file_paths, problems

def expand_paths(paths: list[str], recursive: bool) -> tuple[list[str], list[dict]]:
    all_file_paths = []
    all_problems = []

    for path in paths:
        file_paths, problems = expand_path(path, recursive)
        all_file_paths.extend(file_paths)
        all_problems.extend(problems)

    all_file_paths = sorted(set(all_file_paths))
    return all_file_paths, all_problems