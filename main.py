#!/usr/bin/env python3
import argparse
import shutil
import sys
import tempfile
from pathlib import Path
import urllib.request
import zipfile
import os

# Check ffmpeg
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        # spróbuj automatycznie pobrać i zainstalować ffmpeg lokalnie
        try:
            ensured = ensure_ffmpeg()
            if not ensured:
                print("Wymagane ffmpeg. Nie udało się pobrać automatycznie — zainstaluj je ręcznie i dodaj do PATH.")
                sys.exit(1)
        except Exception:
            print("Wymagane ffmpeg. Zainstaluj je i dodaj do PATH.")
            sys.exit(1)


def ensure_ffmpeg(install_dir: Path = None) -> bool:
    """Ensure ffmpeg is available. If not found, download static build and extract.

    Returns True if ffmpeg is available after the call.
    """
    if shutil.which("ffmpeg") is not None:
        return True

    # target dir under user profile
    if install_dir is None:
        install_dir = Path.home() / '.transkryber' / 'ffmpeg'
    install_dir = Path(install_dir)
    bin_dir = install_dir / 'bin'
    ffmpeg_exe = bin_dir / 'ffmpeg.exe'

    if ffmpeg_exe.exists():
        os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
        return True

    # Windows only automatic download for now
    if sys.platform != 'win32':
        return False

    # choose a known static build URL (Gyan builds)
    url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'

    try:
        install_dir.mkdir(parents=True, exist_ok=True)
        print('Pobieranie ffmpeg...')
        with tempfile.TemporaryDirectory() as td:
            tmpzip = Path(td) / 'ffmpeg.zip'
            urllib.request.urlretrieve(url, tmpzip)
            with zipfile.ZipFile(tmpzip, 'r') as z:
                z.extractall(td)
            # znajdź rozpakowany folder z bin
            extracted = Path(td)
            ff_bin = None
            for p in extracted.iterdir():
                candidate = p / 'bin' / 'ffmpeg.exe'
                if candidate.exists():
                    ff_bin = p / 'bin'
                    break
            if ff_bin is None:
                # możliwa inna struktura - search
                for p in extracted.rglob('ffmpeg.exe'):
                    ff_bin = p.parent
                    break
            if ff_bin is None:
                return False
            # skopiuj pliki bin do naszego folderu
            bin_dir.mkdir(parents=True, exist_ok=True)
            for f in ff_bin.iterdir():
                target = bin_dir / f.name
                try:
                    if f.is_file():
                        with f.open('rb') as src, target.open('wb') as dst:
                            dst.write(src.read())
                except Exception:
                    # ignore copy errors
                    pass
        # dodajemy do PATH dla bieżącego procesu
        os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
        # final check
        return shutil.which('ffmpeg') is not None
    except Exception as e:
        return False


def download_audio(url: str, out_dir: Path) -> Path:
    try:
        import yt_dlp
    except Exception:
        print("Zainstaluj zależność: yt-dlp (pip install yt-dlp)")
        sys.exit(1)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(out_dir / 'audio.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        audio_path = Path(filename).with_suffix('.mp3')
        if not audio_path.exists():
            candidates = list(out_dir.glob('audio.*'))
            if candidates:
                audio_path = candidates[0]
        return audio_path


def transcribe(path: Path, model_size: str) -> str:
    # Try faster-whisper first, fallback to openai/whisper
    try:
        from faster_whisper import WhisperModel
        USE_FASTER = True
    except Exception:
        USE_FASTER = False

    if USE_FASTER:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(path))
        text = "".join([seg.text for seg in segments])
        return text
    else:
        try:
            import whisper
        except Exception:
            print("Brak biblioteki transkrypcyjnej. Zainstaluj 'faster-whisper' lub 'openai-whisper'.")
            sys.exit(1)
        model = whisper.load_model(model_size)
        result = model.transcribe(str(path))
        return result.get('text', '')


def save_txt(text: str, out_path: Path):
    out_path.write_text(text, encoding='utf-8')


def save_docx(text: str, out_path: Path):
    try:
        from docx import Document
    except Exception:
        print("Zainstaluj zależność: python-docx (pip install python-docx)")
        sys.exit(1)
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(out_path)


def main():
    parser = argparse.ArgumentParser(description='Transkrypcja audio z filmu (YouTube) do pliku .txt lub .docx')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL filmu YouTube')
    group.add_argument('--file', help='Lokalna ścieżka do pliku wideo/audio')
    parser.add_argument('--output', '-o', help='Ścieżka wyjściowa (bez rozszerzenia)', default='transkrypcja')
    parser.add_argument('--format', '-f', choices=['txt', 'docx'], default='txt', help='Format wyjściowy')
    parser.add_argument('--model', '-m', default='small', help='Rozmiar modelu Whisper (tiny, base, small, medium, large)')
    args = parser.parse_args()

    check_ffmpeg()

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        if args.url:
            print('Pobieram audio...')
            audio_path = download_audio(args.url, td_path)
        else:
            audio_path = Path(args.file)
            if not audio_path.exists():
                print('Plik nie istnieje:', audio_path)
                sys.exit(1)

        print('Transkrypcja — model:', args.model)
        text = transcribe(audio_path, args.model)

        out_base = Path(args.output)
        if args.format == 'txt':
            out_file = out_base.with_suffix('.txt')
            save_txt(text, out_file)
        else:
            out_file = out_base.with_suffix('.docx')
            save_docx(text, out_file)

        print('Zapisano:', out_file)


if __name__ == '__main__':
    main()
