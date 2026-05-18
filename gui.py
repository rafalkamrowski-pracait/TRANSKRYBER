#!/usr/bin/env python3
import threading
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from main import check_ffmpeg, download_audio, transcribe, save_txt, save_docx
except Exception:
    check_ffmpeg = None
    download_audio = None
    transcribe = None
    save_txt = None
    save_docx = None


class TranscriberGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('TRANSKRYBER')
        self.geometry('560x300')
        self.create_widgets()

    def create_widgets(self):
        pad = {'padx': 8, 'pady': 6}

        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, **pad)

        ttk.Label(frame, text='URL YouTube (lub zostaw puste, wybierz plik)').grid(row=0, column=0, sticky='w')
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky='w', **pad)
        ttk.Button(frame, text='Wklej', command=self.paste_url).grid(row=1, column=2, sticky='w', padx=4)

        ttk.Label(frame, text='Lokalny plik:').grid(row=2, column=0, sticky='w')
        self.file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.file_var, width=48).grid(row=2, column=1, sticky='w')
        ttk.Button(frame, text='Wybierz...', command=self.choose_file).grid(row=2, column=2, sticky='w')

        ttk.Label(frame, text='Folder zapisu transkrypcji:').grid(row=3, column=0, sticky='w')
        default_save = Path.home() / 'Pobrane transkrypcje'
        self.save_dir_var = tk.StringVar(value=str(default_save))
        ttk.Entry(frame, textvariable=self.save_dir_var, width=42).grid(row=3, column=1, sticky='w')
        ttk.Button(frame, text='Wybierz...', command=self.choose_save_dir).grid(row=3, column=2, sticky='w')

        ttk.Label(frame, text='Nazwa pliku (bez rozszerzenia):').grid(row=4, column=0, sticky='w')
        self.out_var = tk.StringVar(value='transkrypcja')
        ttk.Entry(frame, textvariable=self.out_var, width=30).grid(row=4, column=1, sticky='w')

        ttk.Label(frame, text='Format:').grid(row=5, column=0, sticky='w')
        self.format_var = tk.StringVar(value='txt')
        ttk.Combobox(frame, textvariable=self.format_var, values=['txt', 'docx'], width=6, state='readonly').grid(row=5, column=1, sticky='w')

        ttk.Label(frame, text='Model:').grid(row=6, column=0, sticky='w')
        self.model_var = tk.StringVar(value='small')
        ttk.Combobox(frame, textvariable=self.model_var, values=['tiny', 'base', 'small', 'medium', 'large'], width=10, state='readonly').grid(row=6, column=1, sticky='w')

        self.progress = ttk.Label(frame, text='Gotowy')
        self.progress.grid(row=7, column=0, columnspan=2, sticky='w', **pad)

        ttk.Button(frame, text='Start', command=self.start).grid(row=7, column=2, sticky='e')

    def choose_file(self):
        fp = filedialog.askopenfilename(title='Wybierz plik wideo/audio')
        if fp:
            self.file_var.set(fp)

    def paste_url(self, event=None):
        try:
            clipboard_text = self.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except Exception as e:
            messagebox.showerror('Błąd', f'Nie można wkleiće z schowka: {e}')

    def choose_save_dir(self):
        dp = filedialog.askdirectory(title='Wybierz folder zapisu')
        if dp:
            self.save_dir_var.set(dp)

    def start(self):
        if check_ffmpeg is None:
            messagebox.showerror('Błąd', 'Nie można załadować modułów — uruchom skrypt z katalogu projektu.')
            return
        out_name = self.out_var.get().strip()
        if not out_name or out_name == 'transkrypcja':
            messagebox.showerror('Błąd', 'Podaj inną nazwę pliku niż domyślna "transkrypcja".\nAby uniknąć nadpisywania pliku.')
            self.out_var.focus()
            return
        t = threading.Thread(target=self.run_transcription, daemon=True)
        t.start()

    def run_transcription(self):
        self.set_progress('Sprawdzam ffmpeg...')
        try:
            check_ffmpeg()
        except SystemExit:
            messagebox.showerror('Błąd', 'Brak ffmpeg w PATH. Zainstaluj go i spróbuj ponownie.')
            self.set_progress('Błąd: brak ffmpeg')
            return

        url = self.url_var.get().strip()
        filep = self.file_var.get().strip()
        save_dir = self.save_dir_var.get().strip() or str(Path.home() / 'Pobrane transkrypcje')
        out_name = self.out_var.get().strip() or 'transkrypcja'
        outbase = Path(save_dir) / out_name
        fmt = self.format_var.get()
        model = self.model_var.get()

        Path(save_dir).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            try:
                if url:
                    self.set_progress('Pobieram audio...')
                    audio = download_audio(url, td_path)
                else:
                    if not filep:
                        messagebox.showerror('Błąd', 'Podaj URL lub wybierz plik lokalny')
                        self.set_progress('Anulowano')
                        return
                    audio = Path(filep)

                self.set_progress('Transkrypcja... (model: %s)' % model)
                text = transcribe(audio, model)

                self.set_progress('Zapis...')
                if fmt == 'txt':
                    save_txt(text, outbase.with_suffix('.txt'))
                    res = outbase.with_suffix('.txt')
                else:
                    save_docx(text, outbase.with_suffix('.docx'))
                    res = outbase.with_suffix('.docx')

                self.set_progress('Zakończono: %s' % res)
                messagebox.showinfo('Gotowe', f'Zapisano: {res}')
            except Exception as e:
                messagebox.showerror('Błąd', str(e))
                self.set_progress('Błąd')

    def set_progress(self, text: str):
        def _():
            self.progress.config(text=text)
        self.after(0, _)


def run():
    app = TranscriberGUI()
    app.mainloop()


if __name__ == '__main__':
    run()
