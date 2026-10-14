"""AI AGENT GUIDE
Purpose: Read, write, validate, and compare Green Search XML file snapshots.
Boundary: This module must not import or depend on any GUI toolkit, webview, DOM,
user interface state, or presentation code. Keep XML rules independent of the
application interface so other tools can reuse this module directly.
Extension contract: Preserve SnapshotEngine.export_results(files, search_root,
query, extension, target) and compare_snapshots(older_path, newer_path). Return
plain Python dictionaries containing status, errors, and file result records.
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime


class SnapshotEngine:
    """Standalone XML export and path-based comparison engine."""

    def export_results(self, files, search_root, query, extension, target):
        context = {"root": search_root, "query": query, "extension": extension}
        try:
            unique = {item.get("path", "").casefold(): item for item in files if item.get("path")}
            root = ET.Element("search", {
                "created": datetime.now().astimezone().isoformat(timespec="seconds"),
                "root": context["root"], "name_query": context["query"], "extension": context["extension"]})
            file_list = ET.SubElement(root, "files")
            for item in unique.values():
                ET.SubElement(file_list, "file", {key: str(item.get(key, "")) for key in
                    ("name", "folder", "path", "size", "modified")})
            ET.indent(root, space="  ")
            ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
            return {"ok": True, "path": target, "count": len(unique)}
        except (OSError, TypeError, KeyError) as exc:
            return {"ok": False, "error": f"No se pudo exportar el XML: {exc}"}

    def compare_snapshots(self, older_path, newer_path):
        try:
            older = self._snapshot_files(ET.parse(older_path).getroot())
            newer = self._snapshot_files(ET.parse(newer_path).getroot())
            if older is None or newer is None:
                return {"ok": False, "error": "El XML debe contener rutas de archivos (atributo path o elemento file/path)."}
            old_paths = {item["path"].casefold() for item in older}
            added = []
            for item in newer:
                path = item["path"]
                if path.casefold() not in old_paths:
                    added.append({"name": item.get("name") or os.path.basename(path),
                        "folder": item.get("folder") or os.path.dirname(path), "path": path,
                        "size": item.get("size", "N/A"), "modified": item.get("modified", "N/A")})
            return {"ok": True, "items": added}
        except (ET.ParseError, OSError) as exc:
            return {"ok": False, "error": f"No se pudieron comparar los XML: {exc}"}

    @staticmethod
    def _snapshot_files(root):
        items = []
        for node in root.iter():
            path = node.get("path")
            if path is None and node.tag.casefold() in {"file", "path"}:
                path = node.text.strip() if node.text else None
            if not path:
                continue
            item = dict(node.attrib)
            item["path"] = path
            for child in node:
                if child.text and child.tag.casefold() in {"name", "folder", "size", "modified"}:
                    item.setdefault(child.tag.casefold(), child.text.strip())
            items.append(item)
        return items or None