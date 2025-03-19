import json
import sys
from pathlib import Path
import sqlite3

vscode_storage_file = (
    "~/Library/Application Support/Code/User/globalStorage/state.vscdb"
)


def get_vscode_recent_folders(search_query):
    with sqlite3.connect(Path(vscode_storage_file).expanduser()) as conn:
        cursor = conn.cursor()
        res = cursor.execute(
            "select value from itemTable where key='history.recentlyOpenedPathsList'"
        )
        json_data = res.fetchone()[0]

    data = json.loads(json_data)

    recent_folders = []

    for folder in data["entries"]:
        folder_path = folder.get("folderUri")
        if not folder_path:
            continue
        if not folder_path.startswith("file://"):
            continue
        folder_path = folder_path.removeprefix("file://")
        folder_path = Path(folder_path).resolve()
        if not folder_path.exists():
            continue
        recent_folders.append(folder_path)

    searched_folders = []
    for f in recent_folders:
        if f.name.startswith(search_query):
            searched_folders.append(f)
    return searched_folders or recent_folders


def get_formatted_results(search_results):
    formatted_results = []
    for item in search_results:
        result = {
            "title": item.name,
            "subtitle": str(item),
            "arg": str(item),
            "autocomplete": item.name,
            "icon": {"path": "./folder.png"},
        }
        formatted_results.append(result)

    return formatted_results


def get_alfred_items(search_results):
    if len(search_results) == 0:
        result = {
            "title": "No project found.",
            "subtitle": "Enter in a new search term",
        }
        return [result]
    else:
        return get_formatted_results(search_results)


if __name__ == "__main__":
    try:
        search_query = sys.argv[1]
    except Exception:
        search_query = ""
    results = get_vscode_recent_folders(search_query)
    alfred_json = json.dumps({"items": get_alfred_items(results)}, indent=2)

    sys.stdout.write(alfred_json)
