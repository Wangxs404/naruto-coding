import tkinter as tk
from tkinter import scrolledtext
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name

class CodeEditor(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="white")
        self.text = CustomText(self)
        self.linenumbers = TextLineNumbers(self, width=40, bg='white')
        self.linenumbers.attach(self.text)

        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

        self.text.bind("<KeyRelease>", self.highlight)

    def _on_change(self, event):
        self.linenumbers.redraw()

    def highlight(self, event=None):
        code = self.text.get("1.0", "end-1c")
        self.text.mark_set("range_start", "1.0")
        for token, content in lex(code, PythonLexer()):
            self.text.mark_set("range_end", f"range_start + {len(content)}c")
            self.text.tag_add(str(token), "range_start", "range_end")
            self.text.mark_set("range_start", "range_end")

    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        self.text.insert(*args, **kwargs)
        self.highlight()

    def delete(self, *args, **kwargs):
        self.text.delete(*args, **kwargs)

    def bind(self, *args, **kwargs):
        self.text.bind(*args, **kwargs)

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum, fill="#A0A0A0")
            i = self.textwidget.index(f"{i}+1line")

class CustomText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use a monospaced font
        self.config(font=("Courier New", 10), bg="white", fg="black", insertbackground="black")

        # Configure Pygments styles
        style = get_style_by_name('default') # Use a light theme style
        for token, style_def in style:
            kwargs = {}
            fg = style_def['color']
            bg = style_def['bgcolor']
            if fg:
                kwargs['foreground'] = f'#{fg}'
            if bg:
                kwargs['background'] = f'#{bg}'
            if kwargs:
                self.tag_configure(str(token), **kwargs)

        self.bind("<<Modified>>", self._on_modified)

    def _on_modified(self, event=None):
        self.event_generate("<<Change>>")
        self.edit_modified(False)