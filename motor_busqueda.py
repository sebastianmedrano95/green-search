"""AI AGENT GUIDE
Purpose: Provide the standalone filesystem search engine used by Green Search.
Boundary: This module must not import or depend on any GUI toolkit, webview, DOM,
user interface state, or presentation code. Keep the engine usable from scripts,
CLIs, tests, and alternative interfaces.
Extension contract: Preserve the SearchEngine API (start_search, stop_search,
get_updates, is_searching, search_files). Return plain Python dictionaries for
results and queue progress events; keep filesystem matching and traversal here.
"""
import fnmatch
import os
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


class SearchEngine:
    """Threaded filesystem scanner with a UI-neutral event queue."""

    def __init__(self):
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.files_lock = threading.Lock()
        self.is_searching = False
        self.search_files = []
        self.search_context = None

    def start_search(self, root_dir, name_query, extension):
        root_dir = os.path.abspath(root_dir.strip())
        name_query = name_query.strip().lower()
        extension = extension.strip().lower()
        if not os.path.isdir(root_dir):
            return {"ok": False, "error": "La carpeta indicada no existe o no está disponible."}
        if not name_query and not extension:
            return {"ok": False, "error": "Escribe parte del nombre o una extensión."}
        if extension and not extension.startswith("."):
            extension = "." + extension
        with self.lock:
            if self.is_searching:
                return {"ok": False, "error": "Ya hay una búsqueda en curso."}
            self.is_searching = True
            self.search_context = {"root": root_dir, "query": name_query, "extension": extension}
            self.search_files = []
        self.stop_event.clear()
        while not self.events.empty():
            try:
                self.events.get_nowait()
            except queue.Empty:
                break
        threading.Thread(target=self._search, args=(root_dir, name_query, extension), daemon=True).start()
        return {"ok": True}

    def stop_search(self):
        self.stop_event.set()
        return True

    def get_updates(self):
        items, done = [], None
        while True:
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "file":
                items.append(value)
            else:
                done = value
                with self.lock:
                    self.is_searching = False
        return {"items": items, "done": done}

    @staticmethod
    def _matches(name, query, extension):
        lower = name.lower()
        if extension and not lower.endswith(extension):
            return False
        if not query:
            return True
        if "*" in query or "?" in query:
            return fnmatch.fnmatch(lower, query)
        return all(token in lower for token in query.split())

    @staticmethod
    def _format_size(size):
        units = ("B", "KB", "MB", "GB", "TB")
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f"{size:.1f} {units[index]}" if index else f"{size} B"

    def _publish_file(self, entry, folder):
        try:
            stat = entry.stat()
            size = self._format_size(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        except OSError:
            size, modified = "N/A", "N/A"
        item = {"name": entry.name, "folder": folder,
                "path": os.path.normpath(os.path.join(folder, entry.name)),
                "size": size, "modified": modified}
        with self.files_lock:
            self.search_files.append(item)
        self.events.put(("file", item))

    def _scan_directory(self, folder, query, extension):
        count = 0
        stack = [folder]
        while stack and not self.stop_event.is_set():
            current = stack.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if self.stop_event.is_set():
                            break
                        if entry.name.startswith(("$", ".")):
                            continue
                        try:
                            if entry.is_file(follow_symlinks=False):
                                if self._matches(entry.name, query, extension):
                                    count += 1
                                    self._publish_file(entry, current)
                            elif entry.is_dir(follow_symlinks=False):
                                stack.append(entry.path)
                        except OSError:
                            continue
            except (PermissionError, OSError):
                continue
        return count

    def _search(self, root, query, extension):
        started = time.time()
        count = 0
        directories = []
        try:
            with os.scandir(root) as entries:
                for entry in entries:
                    if self.stop_event.is_set():
                        break
                    try:
                        if entry.is_file(follow_symlinks=False) and self._matches(entry.name, query, extension):
                            count += 1
                            self._publish_file(entry, root)
                        elif entry.is_dir(follow_symlinks=False):
                            directories.append(entry.path)
                    except OSError:
                        continue
            workers = min(32, (os.cpu_count() or 4) + 4)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(self._scan_directory, folder, query, extension) for folder in directories]
                for future in as_completed(futures):
                    count += future.result()
            elapsed = time.time() - started
            if self.stop_event.is_set():
                message = f"Búsqueda detenida. {count} archivo(s) encontrados en {elapsed:.2f} s."
            else:
                message = f"Búsqueda completa. {count} archivo(s) encontrados en {elapsed:.2f} s."
        except Exception as exc:
            message = f"Error durante la búsqueda: {exc}"
        self.events.put(("done", message))
