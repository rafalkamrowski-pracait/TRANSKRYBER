# TRANSKRYBER

**TRANSKRYBER** to prosty program do pobierania audio z filmów (np. YouTube) i transkrypcji do pliku `.txt` lub `.docx`.

## Autor
Rafal Kamrowski

## Funkcje
- pobieranie audio z YouTube przy pomocy `yt-dlp`
- transkrypcja z `faster-whisper` lub `openai-whisper`
- zapis wyniku jako `.txt` lub `.docx`
- prosty interfejs graficzny (GUI)
- domyślny folder zapisu: `%USERPROFILE%\Pobrane transkrypcje`
- możliwość uruchomienia GUI bez widocznego terminala

## Wymagania
- Python 3.9+
- `ffmpeg` dodany do PATH
- Zainstalowane zależności (`requirements.txt`)

## Instalacja
1. Zainstaluj `ffmpeg` i dodaj do PATH. Możesz pobrać go z https://ffmpeg.org lub użyć `choco install ffmpeg`.
2. Przejdź do katalogu projektu:

```powershell
cd C:\workspace\transcriber
```

3. Utwórz i aktywuj wirtualne środowisko:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Zainstaluj zależności:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

5. Jeżeli używasz `faster-whisper`, możesz dodatkowo zainstalować `torch` zgodnie z własnym sprzętem.

## Użycie CLI

```powershell
python main.py --url "https://www.youtube.com/watch?v=ID" --output transkrypcja --format txt --model small

python main.py --file "C:\sciezka\do\plik.mp4" --output transkrypcja --format docx
```

## Użycie GUI

Uruchom:

```powershell
run_gui.bat
```

Aby GUI uruchomić bez widocznego terminala, użyj:

```powershell
run_transkryber.vbs
```

## Pliki w projekcie
- `main.py` — główny skrypt transkrypcji
- `gui.py` — proste okno GUI
- `run_windows.bat` — uruchomienie CLI
- `run_gui.bat` — uruchomienie GUI
- `run_transkryber.vbs` — uruchomienie GUI bez terminala
- `requirements.txt` — lista zależności
- `.gitignore` — pliki ignorowane przez Git
- `LICENSE` — licencja MIT
- `TRANSKRYBER.zip` — archiwum do udostępniania

## Bezpieczeństwo prywatnych danych
- Projekt przeskanowano pod kątem typowych wzorców haseł, tokenów i kluczy.
- Nie znaleziono żadnych danych prywatnych w aktualnych plikach projektu.

## Licencja
Projekt jest udostępniony na licencji MIT. Zobacz plik `LICENSE`.
