import fnmatch
import os
import platform
import queue
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

try:
    import webview
except ImportError as exc:
    raise SystemExit(
        "Falta pywebview. Abre abrir_buscador.bat para instalarlo automaticamente."
    ) from exc


HTML = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Green Search</title>
<style>
:root{color-scheme:dark;--bg:#101613;--side:#151e19;--panel:#1b2620;--panel2:#202d26;--line:#304137;--text:#e3eee6;--muted:#91a398;--green:#b9ef70;--teal:#67d6b1;--orange:#f2a76b;--red:#f27f79}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px "Segoe UI",Arial,sans-serif;height:100vh;overflow:hidden}button,input,select{font:inherit}button{cursor:pointer;color:inherit;border:1px solid var(--line);background:var(--panel2);border-radius:6px;padding:9px 12px}button:hover{border-color:var(--green);background:#27372d}button:disabled{opacity:.45;cursor:default}.app{height:100vh;display:grid;grid-template-columns:218px minmax(0,1fr)}aside{background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:20px 14px;min-height:0}.brand{display:flex;align-items:center;gap:10px;padding:0 7px 22px;border-bottom:1px solid var(--line)}.brand-mark{width:28px;height:28px;border:1px solid var(--green);border-radius:7px;display:grid;place-items:center;color:var(--green);font-size:17px}.brand strong{letter-spacing:1px;font-size:14px}.brand small{display:block;color:var(--muted);font-size:11px;margin-top:3px}.nav-label{font-size:10px;color:var(--muted);letter-spacing:1px;margin:23px 8px 10px}.nav-item{display:flex;align-items:center;gap:10px;padding:10px 9px;border-radius:6px;color:var(--muted)}.nav-item.active{background:#27372d;color:var(--green)}.nav-icon{width:17px;text-align:center}.scope{margin-top:9px;border:1px solid var(--line);padding:10px;border-radius:6px;color:var(--muted);font-size:11px;line-height:1.5;overflow-wrap:anywhere}.scope b{color:var(--text);font-size:12px}.side-bottom{margin-top:auto;color:var(--muted);font-size:11px;padding:12px 8px 0;border-top:1px solid var(--line)}main{min-width:0;display:flex;flex-direction:column;padding:26px 30px 0;gap:17px}.top{display:flex;align-items:flex-start;justify-content:space-between}.eyebrow{color:var(--green);font-size:10px;letter-spacing:1.5px;text-transform:uppercase}.top h1{font-size:23px;margin:5px 0 0;font-weight:600}.top-right{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:12px}.dot{width:7px;height:7px;border-radius:50%;background:var(--teal)}.search-panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px}.path-row{display:flex;gap:8px;align-items:center}.field{background:#111a15;border:1px solid var(--line);border-radius:5px;color:var(--text);height:39px;padding:0 11px;outline:0;min-width:0}.field:focus{border-color:var(--green)}.path-input{flex:1}.subfields{display:grid;grid-template-columns:minmax(170px,1fr) 210px auto;gap:8px;margin-top:10px}.search-btn{background:var(--green);border-color:var(--green);color:#182114;font-weight:700;padding:0 21px;height:39px}.search-btn:hover{background:#c9f895}.search-btn.stop{background:var(--red);border-color:var(--red);color:#211515}.filter-row{display:flex;align-items:center;gap:9px}.filter-label{font-size:12px;color:var(--muted);white-space:nowrap}.filter-row select{width:150px}.filter-row .field:last-of-type{flex:1}.summary{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap}.table-wrap{flex:1;min-height:0;border:1px solid var(--line);border-radius:8px;overflow:auto;background:#141c17}table{border-collapse:collapse;width:100%;table-layout:fixed}thead{position:sticky;top:0;background:#202d26;z-index:1}th{text-align:left;color:#a9b8ad;font-weight:600;font-size:11px;letter-spacing:.3px;padding:12px 13px;border-bottom:1px solid var(--line)}td{padding:10px 13px;border-bottom:1px solid #26332b;font-size:12px;color:#d6e2d9;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}tbody tr{cursor:pointer}tbody tr:hover{background:#202c25}tbody tr.selected{background:#26382b;box-shadow:inset 2px 0 var(--green)}th:nth-child(1){width:30%}th:nth-child(2){width:47%}th:nth-child(3){width:10%;text-align:right}td:nth-child(3){text-align:right;color:var(--muted)}th:nth-child(4){width:13%}.file-name{color:var(--text);font-weight:600}.empty{height:100%;min-height:210px;display:grid;place-items:center;text-align:center;color:var(--muted)}.empty strong{display:block;color:var(--text);font-size:14px;font-weight:500;margin-bottom:6px}.footer{height:55px;flex-shrink:0;border-top:1px solid var(--line);display:flex;align-items:center;gap:8px}.status{color:var(--muted);font-size:12px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.status.ok{color:var(--teal)}.foot-btn{padding:7px 10px;font-size:11px}.foot-btn.primary{color:var(--green);border-color:#527344}.hidden{display:none!important}
@media(max-width:850px){.app{grid-template-columns:62px 1fr}aside{padding:16px 9px}.brand{padding:0 7px 19px}.brand-copy,.nav-label,.nav-text,.scope,.side-bottom{display:none}.nav-item{justify-content:center;padding:11px 5px}main{padding:20px 16px 0}.subfields{grid-template-columns:1fr 120px auto}.top h1{font-size:20px}.summary{display:none}}
.table-wrap{overflow-y:scroll;overflow-x:auto;scrollbar-width:thin;scrollbar-color:#648052 #141c17}.table-wrap::-webkit-scrollbar{width:10px;height:10px}.table-wrap::-webkit-scrollbar-track{background:#141c17}.table-wrap::-webkit-scrollbar-thumb{background:#526b45;border:2px solid #141c17;border-radius:6px}.table-wrap::-webkit-scrollbar-thumb:hover{background:var(--green)}
main{min-height:0;overflow:hidden}.table-wrap{flex:1 1 0;height:0;min-height:0;overflow-y:scroll!important;scrollbar-gutter:stable}
.filter-panel{display:grid;gap:8px;min-width:0}.filter-toolbar{display:flex;align-items:center;gap:8px}.filter-rules{display:grid;gap:7px;max-height:132px;overflow-y:auto}.filter-rule{display:grid;grid-template-columns:150px minmax(100px,1fr) 36px;gap:8px}.filter-rule select,.filter-rule input{width:100%;height:36px}.filter-rule .remove-rule{padding:0;font-size:18px;line-height:1;color:var(--muted)}.add-rule{color:var(--green);font-size:12px;padding:7px 10px}
</style>
</head>
<body>
<div class="app">
<aside>
  <div class="brand"><div class="brand-mark">G</div><div class="brand-copy"><strong>GREEN SEARCH</strong><small>Buscador de archivos</small></div></div>
  <div class="nav-label">WORKSPACE</div>
  <div class="nav-item"><span class="nav-icon">◫</span><span class="nav-text">Inicio</span></div>
  <div class="nav-item active"><span class="nav-icon">⌕</span><span class="nav-text">Buscador</span></div>
  <div class="nav-label">UBICACIÓN ACTUAL</div>
  <div class="scope" id="scope">Selecciona una carpeta para iniciar</div>
  <div class="side-bottom">GREEN SEARCH <span style="color:var(--green)">/</span> ARCHIVOS</div>
</aside>
<main>
  <header class="top"><div><div class="eyebrow">Herramientas / Archivos</div><h1>Buscador de archivos</h1></div><div class="top-right"><span class="dot"></span><span id="stateText">Listo</span></div></header>
  <section class="search-panel">
    <div class="path-row"><input id="path" class="field path-input" placeholder="Ruta de búsqueda" value=""><button id="browse">Elegir carpeta</button></div>
    <div class="subfields"><input id="name" class="field" placeholder="Nombre o patrón, por ejemplo: informe*" autocomplete="off"><input id="extension" class="field" placeholder="Extensión (opcional), ej. pdf"><button id="search" class="search-btn">Buscar archivos</button></div>
  </section>
  <section class="filter-panel"><div class="filter-toolbar"><span class="filter-label">Filtrar resultados</span><span class="summary" id="summary">0 archivos</span><button class="add-rule" id="add-filter">+ Añadir filtro</button><button id="clear">Limpiar</button></div><div class="filter-rules" id="filter-rules"></div></section>
  <section class="table-wrap" id="table-wrap"><div class="empty" id="empty"><div><strong>Sin resultados todavía</strong>Indica una carpeta y un nombre o extensión para buscar.</div></div><table id="table" class="hidden"><thead><tr><th>ARCHIVO</th><th>UBICACIÓN</th><th>TAMAÑO</th><th>MODIFICADO</th></tr></thead><tbody id="rows"></tbody></table></section>
  <footer class="footer"><div class="status" id="status">Listo para buscar.</div><button class="foot-btn" id="copyFolder">Copiar ruta carpeta</button><button class="foot-btn" id="copyFile">Copiar ruta</button><button class="foot-btn primary" id="openFolder">Abrir ubicación</button><button class="foot-btn" id="openFile">Abrir archivo</button></footer>
</main>
</div>
<script>
const $=id=>document.getElementById(id);let results=[],selected=-1,lastCount=0,searching=false;
function setStatus(text,ok=false){$('status').textContent=text;$('status').classList.toggle('ok',ok)}
const filterModes=['Contiene','No contiene','Inicia con','Termina con','Es igual a','No es igual a'];
function addFilterRow(){const row=document.createElement('div');row.className='filter-rule';const mode=document.createElement('select');mode.className='field';for(const label of filterModes){const option=document.createElement('option');option.value=label;option.textContent=label;mode.appendChild(option)}const input=document.createElement('input');input.className='field';input.placeholder='Escribe el texto del filtro...';input.addEventListener('input',render);mode.addEventListener('change',render);const remove=document.createElement('button');remove.className='remove-rule';remove.type='button';remove.textContent='×';remove.title='Quitar filtro';remove.setAttribute('aria-label','Quitar filtro');remove.onclick=()=>{row.remove();if(!$('filter-rules').children.length)addFilterRow();render()};row.append(mode,input,remove);$('filter-rules').appendChild(row);input.focus()}
function matches(name){const n=name.toLocaleLowerCase();return [...document.querySelectorAll('.filter-rule')].every(row=>{const q=row.querySelector('input').value.trim().toLocaleLowerCase();if(!q)return true;switch(row.querySelector('select').value){case'No contiene':return !n.includes(q);case'Inicia con':return n.startsWith(q);case'Termina con':return n.endsWith(q);case'Es igual a':return n===q;case'No es igual a':return n!==q;default:return n.includes(q)}})}
function visibleResults(){return results.map((r,i)=>({...r,index:i})).filter(r=>matches(r.name))}
function render(){const wrap=$('table-wrap'),scroll=wrap.scrollTop,list=visibleResults();$('summary').textContent=`${list.length} visibles / ${results.length} archivos`;const rows=$('rows');rows.replaceChildren();$('empty').classList.toggle('hidden',list.length>0);$('table').classList.toggle('hidden',list.length===0);if(!list.length){$('empty').innerHTML=results.length?'<div><strong>No hay coincidencias</strong>Cambia el filtro para ver otros resultados.</div>':'<div><strong>Sin resultados todavía</strong>Indica una carpeta y un nombre o extensión para buscar.</div>';wrap.scrollTop=scroll;return}const frag=document.createDocumentFragment();for(const r of list){const tr=document.createElement('tr');tr.classList.toggle('selected',r.index===selected);tr.onclick=()=>{selected=r.index;render()};for(const [v,cls,title] of [[r.name,'file-name',r.name],[r.folder,'',r.folder],[r.size,'',r.size],[r.modified,'',r.modified]]){const td=document.createElement('td');if(cls)td.className=cls;td.textContent=v;td.title=title;tr.appendChild(td)}frag.appendChild(tr)}rows.appendChild(frag);wrap.scrollTop=scroll}
async function start(){if(searching){await window.pywebview.api.stop_search();return}const path=$('path').value.trim(),name=$('name').value.trim(),extension=$('extension').value.trim();if(!path){setStatus('Selecciona una carpeta para buscar.');return}if(!name&&!extension){setStatus('Escribe parte del nombre o una extensión.');return}results=[];selected=-1;lastCount=0;render();try{const answer=await window.pywebview.api.start_search(path,name,extension);if(!answer.ok){setStatus(answer.error);return}searching=true;$('search').textContent='Detener búsqueda';$('search').classList.add('stop');$('stateText').textContent='Buscando';setStatus('Escaneando archivos...')}catch(e){setStatus('No se pudo iniciar la búsqueda: '+e)}}
$('search').onclick=start;$('path').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('name').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('extension').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('add-filter').onclick=addFilterRow;$('clear').onclick=()=>{$('filter-rules').replaceChildren();addFilterRow();render()};addFilterRow();$('browse').onclick=async()=>{try{const p=await window.pywebview.api.choose_folder();if(p){$('path').value=p;$('scope').textContent=p}}catch(e){setStatus('No se pudo abrir el selector de carpetas: '+e)}};
async function clip(value){if(!value)return;try{const result=await window.pywebview.api.copy_text(value);setStatus(result.ok?'Ruta copiada al portapapeles.':result.error,result.ok)}catch(e){setStatus('No se pudo copiar la ruta: '+e)}}
function chosen(){return results.find((_,i)=>i===selected)}
$('copyFolder').onclick=()=>{const r=chosen();if(r)clip(r.folder);else setStatus('Selecciona un archivo de la lista.')};$('copyFile').onclick=()=>{const r=chosen();if(r)clip(r.path);else setStatus('Selecciona un archivo de la lista.')};$('openFolder').onclick=async()=>{const r=chosen();if(r){const x=await window.pywebview.api.open_folder(r.path);if(!x.ok)setStatus(x.error)}else setStatus('Selecciona un archivo de la lista.')};$('openFile').onclick=async()=>{const r=chosen();if(r){const x=await window.pywebview.api.open_file(r.path);if(!x.ok)setStatus(x.error)}else setStatus('Selecciona un archivo de la lista.')};
async function poll(){try{const data=await window.pywebview.api.get_updates();if(data.items.length){for(const r of data.items)results.push(r);render();if(searching)setStatus(`Buscando... ${results.length} archivos encontrados.`)}if(data.done){searching=false;$('search').textContent='Buscar archivos';$('search').classList.remove('stop');$('stateText').textContent='Listo';setStatus(data.done,true)}}catch(e){}setTimeout(poll,250)}window.addEventListener('pywebviewready',poll);
</script>
</body></html>'''


class SearchApi:
    def __init__(self):
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.is_searching = False

    def choose_folder(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return filedialog.askdirectory(parent=root, title="Seleccionar carpeta")
        finally:
            root.destroy()

    def copy_text(self, text):
        root = tk.Tk()
        root.withdraw()
        try:
            root.clipboard_clear()
            root.clipboard_append(str(text))
            root.update()
            return {"ok": True}
        except tk.TclError as exc:
            return {"ok": False, "error": f"No se pudo copiar al portapapeles: {exc}"}
        finally:
            root.destroy()

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
        self.stop_event.clear()
        while not self.events.empty():
            try:
                self.events.get_nowait()
            except queue.Empty:
                break
        threading.Thread(
            target=self._search, args=(root_dir, name_query, extension), daemon=True
        ).start()
        return {"ok": True}

    def stop_search(self):
        self.stop_event.set()
        return True

    def get_updates(self):
        items = []
        done = None
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

    def open_file(self, path):
        if not os.path.isfile(path):
            return {"ok": False, "error": "El archivo ya no existe."}
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return {"ok": True}
        except OSError as exc:
            return {"ok": False, "error": f"No se pudo abrir el archivo: {exc}"}

    def open_folder(self, path):
        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            return {"ok": False, "error": "La carpeta ya no existe."}
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["explorer", "/select,", path])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["xdg-open", folder])
            return {"ok": True}
        except OSError as exc:
            return {"ok": False, "error": f"No se pudo abrir la carpeta: {exc}"}

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
        self.events.put(("file", {
            "name": entry.name,
            "folder": folder,
            "path": os.path.normpath(os.path.join(folder, entry.name)),
            "size": size,
            "modified": modified,
        }))

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


if __name__ == "__main__":
    api = SearchApi()
    window = webview.create_window(
        "Green Search", html=HTML, js_api=api, width=1180, height=780,
        min_size=(760, 560), background_color="#101613",
    )
    webview.start()
