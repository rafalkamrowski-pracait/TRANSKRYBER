#!/usr/bin/env python3
import argparse
import shutil
import sys
import tempfile
from pathlib import Path

# Check ffmpeg
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("Wymagane ffmpeg. Zainstaluj je i dodaj do PATH.")
        sys.exit(1)


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
