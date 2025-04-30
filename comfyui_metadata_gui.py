import os
import json
import re
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

# AJOUT pour le glisser-déposer
from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import Image, ImageTk, PngImagePlugin, ExifTags

def extraire_metadata(image_path):
    img = Image.open(image_path)
    raw = img.info.get("parameters") or img.info.get("prompt") or ""
    if not raw and hasattr(img, "text"):
        for v in img.text.values():
            if isinstance(v, str) and any(k in v.lower() for k in ("prompt","sampler","steps","cfg","ckpt","checkpoint","text")):
                raw = v
                break
    if not raw:
        for key,val in img.info.items():
            if key.lower() in ("description","comment","xmp","xml","keywords") and isinstance(val,str) and len(val)>20:
                raw = val
                break
    if not raw and img.format in ("JPEG","JPG"):
        comment = img.info.get('comment')
        if comment:
            if isinstance(comment,(bytes,bytearray)):
                raw = comment.decode('utf-8','ignore')
            elif isinstance(comment,(list,tuple)):
                try:
                    raw = b"".join(comment).decode('utf-8','ignore')
                except:
                    raw = ""
            elif isinstance(comment,str):
                raw = comment
    if not raw and img.format in ("JPEG","JPG"):
        exif = img.getexif()
        parts = []
        for tag,val in exif.items():
            name = ExifTags.TAGS.get(tag, tag)
            if name in ("ImageDescription","UserComment","XPComment"):
                if isinstance(val,(bytes,bytearray)):
                    try:
                        parts.append(val.decode('utf-8','ignore'))
                    except:
                        pass
                elif isinstance(val,str):
                    parts.append(val)
        raw = "\n".join(parts)
    if not raw:
        try:
            with open(image_path, "rb") as f:
                raw = f.read().decode('latin-1', errors='ignore')
        except:
            raw = ""
    if not raw:
        return {"Erreur":"Aucune métadonnée trouvée."}

    champs = ["Prompt","Sampler","Steps","Model","Lora","CFG Scale","Seed","VAE"]
    meta = {c:"Non trouvé" for c in champs}
    try:
        parsed = json.loads(raw)
    except:
        parsed = None
    if isinstance(parsed, dict) and any(isinstance(v,dict) and 'class_type' in v for v in parsed.values()):
        # Extraction via workflow JSON
        for node in parsed.values():
            if node.get('class_type')=='CLIPTextEncode':
                txt = node.get('inputs',{}).get('text')
                if isinstance(txt,str) and txt.strip():
                    meta['Prompt'] = txt.strip()
                    break
        for node in parsed.values():
            ct = node.get('class_type','')
            inp = node.get('inputs',{})
            if 'Sampler' in ct:
                meta['Sampler'] = inp.get('sampler_name') or inp.get('scheduler') or meta['Sampler']
                meta['Steps']   = str(inp.get('steps',meta['Steps']))
                meta['CFG Scale'] = str(inp.get('cfg') or inp.get('cfg_scale', meta['CFG Scale']))
                meta['Seed']    = str(inp.get('seed', meta['Seed']))
                break
        for node in parsed.values():
            kl = node.get('class_type','').lower()
            if any(x in kl for x in ('loader','checkp','loadergguf')):
                for key in ('unet_name','checkpoint','ckpt_name','model','ckpt_path'):
                    v = node.get('inputs',{}).get(key)
                    if isinstance(v,str) and v:
                        meta['Model'] = os.path.basename(v)
                        break
                if meta['Model'] != 'Non trouvé':
                    break
        for node in parsed.values():
            if 'VAE' in node.get('class_type',''):
                v = node.get('inputs',{}).get('vae_name') or node.get('inputs',{}).get('vae')
                if isinstance(v,str) and v:
                    meta['VAE'] = os.path.basename(v)
                    break
        loras = []
        for node in parsed.values():
            if 'Lora' in node.get('class_type',''):
                for k,v in node.get('inputs',{}).items():
                    if k.startswith('lora_') and isinstance(v,str) and v.lower()!='none':
                        num = k.split('_')[1]
                        strg = node.get('inputs',{}).get(f'strength_{num}')
                        loras.append(f"{os.path.basename(v)} ({strg})")
        if loras:
            meta['Lora'] = ', '.join(loras)
    else:
        # Analyse brut
        def ext(p):
            m = re.search(p, raw, re.IGNORECASE)
            return m.group(1).strip() if m else None
        meta['Prompt']  = ext(r'Prompt\s*[:=]\s*(.+?)(?:,|$)') or meta['Prompt']
        meta['Sampler'] = ext(r'Sampler\s*[:=]\s*([\w\d_+]+)') or meta['Sampler']
        meta['Steps']   = ext(r'Steps\s*[:=]\s*(\d+)') or meta['Steps']
        meta['Model']   = ext(r'Model(?: name)?\s*[:=]\s*([\w\-/.]+)') or meta['Model']
        meta['CFG Scale'] = ext(r'cfg(?:_scale)?\s*[:=]\s*([0-9.]+)') or meta['CFG Scale']
        meta['Seed']      = ext(r'seed\s*[:=]\s*(\d+)') or meta['Seed']
        meta['VAE']       = ext(r'vae(?:_name)?\s*[:=]\s*([\w\-_.]+)') or meta['VAE']
        l = re.findall(r'([\w\-_.]+\.(safetensors|gguf))\s*\((\d+(?:\.\d+)?)\)', raw)
        if l:
            meta['Lora'] = ', '.join(f"{n} ({s})" for n,_,s in l)
    return meta

class MetaViewerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title('Meta Viewer')
        if os.path.exists('icon.ico'):
            self.iconbitmap('icon.ico')
        self.geometry('600x400')
        self.configure(padx=5, pady=5)
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill='x')
        ttk.Button(top, text='Ouvrir image', command=self.choose_image).pack(side='left')

        bottom = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        bottom.pack(fill='both', expand=True)

        self.preview = ttk.Label(bottom, text='Déposez une image ici', anchor='center')
        bottom.add(self.preview, weight=1)

        # Active le glisser-déposer
        self.preview.drop_target_register(DND_FILES)
        self.preview.dnd_bind('<<Drop>>', self.on_drop)

        self.text_display = ScrolledText(bottom, wrap='word', font=('Consolas', 10))
        self.text_display.configure(state='normal')
        self.text_display.bind('<Button-3>', self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label='Copier', command=lambda: self.text_display.event_generate('<<Copy>>'))
        self.context_menu.add_command(label='Select All', command=lambda: self.text_display.tag_add('sel', '1.0', 'end'))
        bottom.add(self.text_display, weight=3)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.jpeg')])
        if path:
            meta = extraire_metadata(path)
            self.show_preview(path)
            self.show_metadata(meta)

    def on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path):
            meta = extraire_metadata(path)
            self.show_preview(path)
            self.show_metadata(meta)

    def show_preview(self, path):
        img = Image.open(path)
        img.thumbnail((100,100))
        self.tk_img = ImageTk.PhotoImage(img)
        self.preview.configure(image=self.tk_img, text='')

    def show_metadata(self, meta):
        self.text_display.delete('1.0', tk.END)
        for k, v in meta.items():
            self.text_display.insert(tk.END, f"{k}: {v}\n")
        self.text_display.see('1.0')

if __name__ == '__main__':
    app = MetaViewerApp()
    app.mainloop()
