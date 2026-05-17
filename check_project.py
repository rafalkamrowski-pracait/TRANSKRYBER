import py_compile
import importlib
import subprocess
from pathlib import Path
import sys

root = Path('.').resolve()
print('Project path:', root)

# Compile check
files = ['main.py','gui.py']
for f in files:
    p = root / f
    try:
        py_compile.compile(str(p), doraise=True)
        print(f'OK: {f} compiled')
    except Exception as e:
        print(f'ERROR: compiling {f}:', e)

# Import check
try:
    import main, gui
    print('OK: imported main and gui')
except Exception as e:
    print('ERROR: import failed:', e)

# Git status
try:
    out = subprocess.check_output(['git','status','--porcelain'], stderr=subprocess.STDOUT).decode().strip()
    print('GIT status (porcelain):')
    print(out if out else '(clean)')
except Exception as e:
    print('GIT check failed:', e)

# Zip
zip_path = root / 'TRANSKRYBER.zip'
print('TRANSKRYBER.zip exists:' , zip_path.exists())

# venv
venv_path = root / '.venv'
print('.venv exists:', venv_path.exists())

# ffmpeg check
import shutil
print('ffmpeg in PATH:', shutil.which('ffmpeg') is not None)

print('\nCheck complete')
