"""AI AGENT GUIDE
Purpose: Run the Green Search desktop interface and connect it to independent
search and XML comparison engines.
Boundary: This is the only module that may import pywebview, Tkinter, or contain
HTML/CSS/JavaScript presentation. Do not move filesystem search or XML comparison
algorithms into this module; delegate them to motor_busqueda and motor_comparador.
Extension contract: SearchApi adapts UI calls to engine APIs and returns JSON-safe
plain dictionaries. Keep UI-specific dialogs and window startup here.
"""
import os
import platform
import subprocess
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog
import webview

from motor_busqueda import SearchEngine
from motor_comparador import SnapshotEngine


HTML = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Green Search</title>
<style>
:root{
  color-scheme: dark;
  --bg: #101613;
  --side: #151e19;
  --panel: #1b2620;
  --panel2: #202d26;
  --line: #304137;
  --text: #e3eee6;
  --muted: #91a398;
  --green: #b9ef70;
  --teal: #67d6b1;
  --orange: #f2a76b;
  --red: #f27f79;
}
*{box-sizing:border-box}
body{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font:14px "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
  height:100vh;
  overflow:hidden;
  -webkit-font-smoothing: antialiased;
}
button,input,select{font:inherit}
button{cursor:pointer;color:inherit;border:1px solid var(--line);background:var(--panel2);border-radius:6px;padding:9px 12px;transition:background 0.15s, border-color 0.15s}
button:hover{border-color:var(--green);background:#27372d}
button:disabled{opacity:.45;cursor:default}

.hidden { display: none !important; }

.app{height:100vh;display:grid;grid-template-columns:218px minmax(0,1fr);width:100vw;overflow:hidden}
aside{background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:20px 14px;min-height:0}
.brand{display:flex;align-items:center;gap:10px;padding:0 7px 22px;border-bottom:1px solid var(--line)}
.brand-mark{width:28px;height:28px;border:1px solid var(--green);border-radius:7px;display:grid;place-items:center;color:var(--green);font-size:17px}
.brand strong{letter-spacing:1px;font-size:14px}
.brand small{display:block;color:var(--muted);font-size:11px;margin-top:3px}
.nav-label{font-size:10px;color:var(--muted);letter-spacing:1px;margin:23px 8px 10px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 9px;border-radius:6px;color:var(--muted);border:none;background:transparent;width:100%;text-align:left}
.nav-item.active{background:#27372d;color:var(--green)}
.nav-icon{width:17px;text-align:center}
.scope{margin-top:9px;border:1px solid var(--line);padding:10px;border-radius:6px;color:var(--muted);font-size:11px;line-height:1.5;overflow-wrap:anywhere}
.scope b{color:var(--text);font-size:12px}
.side-bottom{margin-top:auto;color:var(--muted);font-size:11px;padding:12px 8px 0;border-top:1px solid var(--line)}

main{min-width:0;display:flex;flex-direction:column;padding:24px 28px 20px;gap:16px;height:100vh;overflow:hidden}
.top{display:flex;align-items:flex-start;justify-content:space-between}
.eyebrow{color:var(--green);font-size:10px;letter-spacing:1.5px;text-transform:uppercase}
.top h1{font-size:23px;margin:5px 0 0;font-weight:600}
.top-right{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:12px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--teal)}

.search-panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;flex-shrink:0}
.path-row{display:flex;gap:8px;align-items:center}
.field{background:#111a15;border:1px solid var(--line);border-radius:5px;color:var(--text);height:39px;padding:0 11px;outline:0;min-width:0}
.field:focus{border-color:var(--green)}
.path-input{flex:1}
.subfields{display:grid;grid-template-columns:minmax(170px,1fr) 210px auto;gap:8px;margin-top:10px}
.search-btn{background:var(--green);border-color:var(--green);color:#182114;font-weight:700;padding:0 21px;height:39px}
.search-btn:hover{background:#c9f895}
.search-btn.stop{background:var(--red);border-color:var(--red);color:#211515}

.filter-panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 16px;flex-shrink:0;display:grid;gap:8px;min-width:0}
.filter-toolbar{display:flex;align-items:center;gap:8px}
.filter-label{font-size:12px;color:var(--muted);white-space:nowrap}
.filter-row select{width:150px}
.summary{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap}
.filter-rules{display:grid;gap:7px;max-height:110px;overflow-y:auto}
.filter-rule{display:grid;grid-template-columns:150px minmax(100px,1fr) 36px;gap:8px}
.filter-rule select,.filter-rule input{width:100%;height:36px}
.filter-rule .remove-rule{padding:0;font-size:18px;line-height:1;color:var(--muted);background:transparent;border:1px solid var(--line)}
.filter-rule .remove-rule:hover{color:var(--red);border-color:var(--red)}
.add-rule{color:var(--green);font-size:12px;padding:7px 10px;background:transparent;border:1px solid #527344}

.table-wrap{
  flex:1 1 0;
  min-height:0;
  border:1px solid var(--line);
  border-radius:8px;
  overflow-y:auto;
  overflow-x:auto;
  background:#141c17;
  scrollbar-width:thin;
  scrollbar-color:#526b45 #141c17;
}
.table-wrap::-webkit-scrollbar{width:8px;height:8px}
.table-wrap::-webkit-scrollbar-track{background:#141c17}
.table-wrap::-webkit-scrollbar-thumb{background:#526b45;border-radius:4px}
.table-wrap::-webkit-scrollbar-thumb:hover{background:var(--green)}

table{border-collapse:collapse;width:100%;table-layout:fixed}
thead{position:sticky;top:0;background:#202d26;z-index:2}
th{text-align:left;color:#a9b8ad;font-weight:600;font-size:11px;letter-spacing:.3px;padding:12px 13px;border-bottom:1px solid var(--line)}
td{padding:10px 13px;border-bottom:1px solid #26332b;font-size:12px;color:#d6e2d9;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tbody tr{cursor:pointer}
tbody tr:hover{background:#202c25}
tbody tr.selected{background:#26382b;box-shadow:inset 3px 0 var(--green)}
th:nth-child(1), td:nth-child(1){width:28%}
th:nth-child(2), td:nth-child(2){width:48%}
th:nth-child(3), td:nth-child(3){width:10%;text-align:right}
th:nth-child(4), td:nth-child(4){width:14%}

.file-name{color:var(--text);font-weight:600}
.empty{height:100%;min-height:180px;display:grid;place-items:center;text-align:center;color:var(--muted);padding:20px}
.empty strong{display:block;color:var(--text);font-size:14px;font-weight:500;margin-bottom:6px}

.footer{height:50px;flex-shrink:0;border-top:1px solid var(--line);display:flex;align-items:center;gap:8px}
.status{color:var(--muted);font-size:12px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.status.ok{color:var(--teal)}
.foot-btn{padding:7px 10px;font-size:11px}
.foot-btn.primary{color:var(--green);border-color:#527344}
.export-btn{color:var(--green);border-color:#527344;font-weight:600}

.view{display:flex;flex:1;min-height:0;flex-direction:column;gap:16px;overflow:hidden}
.view.hidden{display:none!important}

.compare-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:18px;display:grid;gap:14px;flex-shrink:0}
.compare-files{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.compare-file{padding:14px;border:1px solid var(--line);border-radius:7px;display:grid;gap:9px;background:#141c17}
.compare-file strong{font-size:13px}
.compare-file span{font-size:11px;color:var(--muted);overflow-wrap:anywhere;min-height:16px}
.compare-actions{display:flex;gap:10px;align-items:center}

@media(max-width:900px){
  .app{grid-template-columns:70px 1fr}
  aside{padding:16px 8px}
  .brand-copy,.nav-label,.nav-text,.scope,.side-bottom{display:none}
  .brand{padding:0 0 16px;justify-content:center}
  .nav-item{justify-content:center;padding:11px 4px}
  main{padding:18px}
  .subfields{grid-template-columns:1fr 120px auto}
}
@media(max-width:650px){
  .compare-files{grid-template-columns:1fr}
  .compare-actions{align-items:stretch;flex-direction:column}
  .subfields{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="app">
<aside>
  <div class="brand"><div class="brand-mark">G</div><div class="brand-copy"><strong>GREEN SEARCH</strong><small>Buscador</small></div></div>
  <div class="nav-label">WORKSPACE</div>
  <button class="nav-item active" id="nav-search"><span class="nav-icon">⌕</span><span class="nav-text">Buscador</span></button>
  <button class="nav-item" id="nav-compare"><span class="nav-icon">⇄</span><span class="nav-text">Comparar XML</span></button>
  <div class="nav-label">UBICACIÓN</div>
  <div class="scope" id="scope">Selecciona carpeta</div>
  <div class="side-bottom">GREEN SEARCH <span style="color:var(--green)">/</span> v1.1</div>
</aside>
<main>
  <header class="top"><div><div class="eyebrow">Herramientas / Archivos</div><h1 id="page-title">Buscador de archivos</h1></div><div class="top-right"><span class="dot"></span><span id="stateText">Listo</span></div></header>

  <div id="search-view" class="view">
    <section class="search-panel">
      <div class="path-row"><input id="path" class="field path-input" placeholder="Ruta de búsqueda" value=""><button id="browse">Elegir carpeta</button></div>
      <div class="subfields"><input id="name" class="field" placeholder="Nombre o patrón (ej. informe*)" autocomplete="off"><input id="extension" class="field" placeholder="Extensión (ej. pdf)"><button id="search" class="search-btn">Buscar archivos</button></div>
    </section>

    <section class="filter-panel">
      <div class="filter-toolbar"><span class="filter-label">Filtrar resultados</span><span class="summary" id="summary">0 archivos</span><button class="add-rule" id="add-filter">+ Añadir filtro</button><button id="clear">Limpiar</button></div>
      <div class="filter-rules" id="filter-rules"></div>
    </section>

    <section class="table-wrap" id="table-wrap">
      <div class="empty" id="empty"><div><strong>Sin resultados todavía</strong>Indica una carpeta y un criterio para buscar.</div></div>
      <table id="table" class="hidden"><thead><tr><th>ARCHIVO</th><th>UBICACIÓN</th><th>TAMAÑO</th><th>MODIFICADO</th></tr></thead><tbody id="rows"></tbody></table>
    </section>

    <footer class="footer" id="search-footer"><div class="status" id="status">Listo para buscar.</div><button class="foot-btn" id="copyFolder">Copiar carpeta</button><button class="foot-btn" id="copyFile">Copiar ruta</button><button class="foot-btn primary" id="openFolder">Abrir ubicación</button><button class="foot-btn" id="openFile">Abrir archivo</button><button class="foot-btn export-btn" id="export">Exportar</button></footer>
  </div>

  <div id="compare-view" class="view hidden">
    <section class="compare-card">
      <div><strong>Compara dos capturas de búsqueda</strong><div class="filter-label" style="margin-top:4px">Carga archivos XML exportados por Green Search para contrastar diferencias.</div></div>
      <div class="compare-files">
        <div class="compare-file"><strong>XML A · Anterior</strong><span id="xml-a-name">Ningún XML cargado</span><button id="load-xml-a">Cargar XML A</button></div>
        <div class="compare-file"><strong>XML B · Reciente</strong><span id="xml-b-name">Ningún XML cargado</span><button id="load-xml-b">Cargar XML B</button></div>
      </div>
      <div class="compare-actions"><button class="foot-btn primary" id="run-compare">Comparar archivos</button><div class="status" id="compare-status">Carga los dos XML para comenzar.</div></div>
    </section>
    <section class="table-wrap" id="compare-table-wrap">
      <div class="empty" id="compare-empty"><div><strong>Sin comparación todavía</strong>Carga dos archivos XML y pulsa Comparar archivos.</div></div>
      <table id="compare-table" class="hidden"><thead><tr><th>ARCHIVO NUEVO</th><th>UBICACIÓN</th><th>TAMAÑO</th><th>MODIFICADO</th></tr></thead><tbody id="compare-rows"></tbody></table>
    </section>
  </div>
</main>
</div>
<script>
const $=id=>document.getElementById(id);let results=[],selected=-1,searching=false,comparisonPaths=null;
function setStatus(text,ok=false){$('status').textContent=text;$('status').classList.toggle('ok',ok)}
const filterModes=['Contiene','No contiene','Inicia con','Termina con','Es igual a','No es igual a'];
function addFilterRow(){const row=document.createElement('div');row.className='filter-rule';const mode=document.createElement('select');mode.className='field';for(const label of filterModes){const option=document.createElement('option');option.value=label;option.textContent=label;mode.appendChild(option)}const input=document.createElement('input');input.className='field';input.placeholder='Texto del filtro...';input.addEventListener('input',render);mode.addEventListener('change',render);const remove=document.createElement('button');remove.className='remove-rule';remove.type='button';remove.textContent='×';remove.title='Quitar filtro';remove.onclick=()=>{row.remove();if(!$('filter-rules').children.length)addFilterRow();render()};row.append(mode,input,remove);$('filter-rules').appendChild(row);input.focus()}
function matches(name){const n=name.toLocaleLowerCase();return [...document.querySelectorAll('.filter-rule')].every(row=>{const q=row.querySelector('input').value.trim().toLocaleLowerCase();if(!q)return true;switch(row.querySelector('select').value){case'No contiene':return !n.includes(q);case'Inicia con':return n.startsWith(q);case'Termina con':return n.endsWith(q);case'Es igual a':return n===q;case'No es igual a':return n!==q;default:return n.includes(q)}})}
function visibleResults(){return results.map((r,i)=>({...r,index:i})).filter(r=>matches(r.name)&&(!comparisonPaths||comparisonPaths.has(r.path.toLocaleLowerCase())))}
function render(){const wrap=$('table-wrap'),scroll=wrap.scrollTop,list=visibleResults();$('summary').textContent=`${list.length} visibles / ${results.length} archivos`;const rows=$('rows');rows.replaceChildren();$('empty').classList.toggle('hidden',list.length>0);$('table').classList.toggle('hidden',list.length===0);if(!list.length){wrap.scrollTop=scroll;return}const frag=document.createDocumentFragment();for(const r of list){const tr=document.createElement('tr');tr.classList.toggle('selected',r.index===selected);tr.onclick=()=>{selected=r.index;render()};for(const [v,cls,title] of [[r.name,'file-name',r.name],[r.folder,'',r.folder],[r.size,'',r.size],[r.modified,'',r.modified]]){const td=document.createElement('td');if(cls)td.className=cls;td.textContent=v;td.title=title;tr.appendChild(td)}frag.appendChild(tr)}rows.appendChild(frag);wrap.scrollTop=scroll}
async function start(){if(searching){await window.pywebview.api.stop_search();return}const path=$('path').value.trim(),name=$('name').value.trim(),extension=$('extension').value.trim();if(!path){setStatus('Selecciona una carpeta para buscar.');return}if(!name&&!extension){setStatus('Escribe parte del nombre o una extensión.');return}results=[];selected=-1;comparisonPaths=null;render();try{const answer=await window.pywebview.api.start_search(path,name,extension);if(!answer.ok){setStatus(answer.error);return}searching=true;$('search').textContent='Detener búsqueda';$('search').classList.add('stop');$('stateText').textContent='Buscando';setStatus('Escaneando archivos...')}catch(e){setStatus('No se pudo iniciar la búsqueda: '+e)}}
$('search').onclick=start;$('path').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('name').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('extension').addEventListener('keydown',e=>{if(e.key==='Enter')start()});$('add-filter').onclick=addFilterRow;$('clear').onclick=()=>{$('filter-rules').replaceChildren();addFilterRow();render()};addFilterRow();$('browse').onclick=async()=>{try{const p=await window.pywebview.api.choose_folder();if(p){$('path').value=p;$('scope').textContent=p}}catch(e){setStatus('No se pudo abrir el selector: '+e)}};
async function exportResults(){if(searching){setStatus('Espera a que termine la búsqueda.');return}if(!results.length){setStatus('Realiza una búsqueda primero.');return}try{const choice=await window.pywebview.api.choose_export_destination();if(!choice.ok){if(!choice.cancelled)setStatus(choice.error);return}const saved=await window.pywebview.api.export_results(choice.path,results,$('path').value.trim(),$('name').value.trim(),$('extension').value.trim());setStatus(saved.ok?`Exportados ${saved.count} archivos: ${saved.path}`:saved.error,saved.ok)}catch(e){setStatus('Error al exportar: '+e)}}
document.getElementById('export').onclick=exportResults;
let comparisonFiles={a:null,b:null};
function setView(view){$('search-view').classList.toggle('hidden',view!=='search');$('search-footer').classList.toggle('hidden',view!=='search');$('compare-view').classList.toggle('hidden',view!=='compare');$('nav-search').classList.toggle('active',view==='search');$('nav-compare').classList.toggle('active',view==='compare');$('page-title').textContent=view==='search'?'Buscador de archivos':'Comparar XML'}
document.getElementById('nav-search').onclick=()=>setView('search');document.getElementById('nav-compare').onclick=()=>setView('compare');
async function loadComparisonFile(slot){try{const data=await window.pywebview.api.choose_snapshot();if(!data)return;if(data.error){$('compare-status').textContent=data.error;return}comparisonFiles[slot]=data.path;$(`xml-${slot}-name`).textContent=data.name;$('compare-status').textContent='XML cargado correctamente.'}catch(e){$('compare-status').textContent='Error al cargar XML: '+e}}
$('load-xml-a').onclick=()=>loadComparisonFile('a');$('load-xml-b').onclick=()=>loadComparisonFile('b');
$('run-compare').onclick=async()=>{if(!comparisonFiles.a||!comparisonFiles.b){$('compare-status').textContent='Carga ambos archivos XML.';return}try{const data=await window.pywebview.api.compare_snapshots(comparisonFiles.a,comparisonFiles.b);if(!data.ok){$('compare-status').textContent=data.error;return}const rows=$('compare-rows');rows.replaceChildren();$('compare-empty').classList.toggle('hidden',data.items.length>0);$('compare-table').classList.toggle('hidden',data.items.length===0);if(!data.items.length)$('compare-empty').innerHTML='<div><strong>No hay archivos nuevos</strong>XML B no contiene rutas nuevas frente a XML A.</div>';for(const file of data.items){const tr=document.createElement('tr');for(const [value,cls] of [[file.name,'file-name'],[file.folder,''],[file.size,''],[file.modified,'']]){const td=document.createElement('td');td.textContent=value;if(cls)td.className=cls;td.title=value;tr.appendChild(td)}rows.appendChild(tr)}$('compare-status').textContent=`Comparación completa: ${data.items.length} nuevo(s) en XML B.`}catch(e){$('compare-status').textContent='Error en comparación: '+e}};
async function clip(value){if(!value){setStatus('No hay una ruta para copiar.');return}try{const result=await window.pywebview.api.copy_text(value);setStatus(result.ok?'Ruta copiada al portapapeles.':result.error,result.ok)}catch(e){setStatus('Error al copiar: '+e)}}
function chosen(){return selected>=0?results[selected]:null}
$('copyFolder').onclick=()=>{const r=chosen();if(r)clip(r.folder);else setStatus('Selecciona una fila de archivo antes de copiar.')};$('copyFile').onclick=()=>{const r=chosen();if(r)clip(r.path);else setStatus('Selecciona una fila de archivo antes de copiar.')};$('openFolder').onclick=async()=>{const r=chosen();if(r){const x=await window.pywebview.api.open_folder(r.path);if(!x.ok)setStatus(x.error)}else setStatus('Selecciona un archivo.')};$('openFile').onclick=async()=>{const r=chosen();if(r){const x=await window.pywebview.api.open_file(r.path);if(!x.ok)setStatus(x.error)}else setStatus('Selecciona un archivo.')};
async function poll(){try{const data=await window.pywebview.api.get_updates();if(data.items.length){const wasEmpty=results.length===0;for(const r of data.items)results.push(r);if(wasEmpty&&results.length)selected=0;render();if(searching)setStatus(`Buscando... ${results.length} encontrados.`)}if(data.done){searching=false;$('search').textContent='Buscar archivos';$('search').classList.remove('stop');$('stateText').textContent='Listo';setStatus(data.done,true)}}catch(e){}setTimeout(poll,250)}window.addEventListener('pywebviewready',poll);
</script>
</body>
</html>'''


class SearchApi:
    """GUI adapter that delegates search and XML operations to standalone engines."""

    def __init__(self):
        self.search_engine = SearchEngine()
        self.snapshot_engine = SnapshotEngine()

    def _dialog(self, callback, **options):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return callback(parent=root, **options)
        finally:
            root.destroy()

    def choose_folder(self):
        return self._dialog(filedialog.askdirectory, title="Seleccionar carpeta")

    def choose_snapshot(self):
        path = self._dialog(filedialog.askopenfilename, title="Seleccionar captura XML",
            filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")])
        if not path:
            return None
        return {"path": os.path.abspath(path), "name": os.path.basename(path)}

    def copy_text(self, text):
        text = str(text)
        if platform.system() == "Windows":
            try:
                return self._copy_text_windows(text)
            except OSError as exc:
                return {"ok": False, "error": f"No se pudo copiar la ruta al portapapeles: {exc}"}
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

    @staticmethod
    def _copy_text_windows(text):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        GMEM_MOVEABLE = 0x0002
        CF_UNICODETEXT = 13
        kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
        kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
        kernel32.GlobalUnlock.restype = wintypes.BOOL
        kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
        kernel32.GlobalFree.restype = wintypes.HGLOBAL
        kernel32.GlobalFree.argtypes = (wintypes.HGLOBAL,)
        user32.OpenClipboard.restype = wintypes.BOOL
        user32.OpenClipboard.argtypes = (wintypes.HWND,)
        user32.EmptyClipboard.restype = wintypes.BOOL
        user32.SetClipboardData.restype = wintypes.HANDLE
        user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
        user32.CloseClipboard.restype = wintypes.BOOL
        if not user32.OpenClipboard(None):
            raise OSError("Windows no pudo abrir el portapapeles.")
        handle = None
        try:
            if not user32.EmptyClipboard():
                raise OSError("Windows no pudo vaciar el portapapeles.")
            encoded = (text + "\0").encode("utf-16-le")
            handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
            if not handle:
                raise OSError("Windows no pudo reservar memoria para la ruta.")
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                raise OSError("Windows no pudo bloquear memoria para la ruta.")
            try:
                ctypes.memmove(pointer, encoded, len(encoded))
            finally:
                kernel32.GlobalUnlock(handle)
            if not user32.SetClipboardData(CF_UNICODETEXT, handle):
                raise OSError("Windows no pudo guardar la ruta en el portapapeles.")
            handle = None  # The clipboard owns the allocation after SetClipboardData.
            return {"ok": True}
        finally:
            if handle:
                kernel32.GlobalFree(handle)
            user32.CloseClipboard()

    def start_search(self, root_dir, name_query, extension):
        return self.search_engine.start_search(root_dir, name_query, extension)

    def stop_search(self):
        return self.search_engine.stop_search()

    def get_updates(self):
        return self.search_engine.get_updates()

    def choose_export_destination(self):
        filename = "busqueda_" + __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S") + ".xml"
        path = self._dialog(filedialog.asksaveasfilename, title="Exportar resultados de búsqueda",
            defaultextension=".xml", initialfile=filename,
            filetypes=[("Archivo XML", "*.xml")])
        if not path:
            return {"ok": False, "cancelled": True}
        if not path.lower().endswith(".xml"):
            path += ".xml"
        return {"ok": True, "path": path}

    def export_results(self, target, files, search_root, query, extension):
        return self.snapshot_engine.export_results(files, search_root, query, extension, target)

    def compare_snapshots(self, older_path, newer_path):
        return self.snapshot_engine.compare_snapshots(older_path, newer_path)

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


def main():
    api = SearchApi()
    webview.create_window("Green Search", html=HTML, js_api=api, width=1180, height=780,
        min_size=(760, 560), background_color="#101613")
    webview.start()


if __name__ == "__main__":
    main()
