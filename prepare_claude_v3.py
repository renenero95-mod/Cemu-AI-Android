import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v3"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 1. Lista dei file da includere (quelli che ci hai appena dato)
files_to_copy = [
    "Cemu/src/Cafe/Filesystem/fsc.cpp",
    "Cemu/src/Cafe/Filesystem/fsc.h",
    "Cemu/src/Cafe/Filesystem/fscDeviceAndroidSAF.cpp",
    "Cemu/src/Cafe/Filesystem/fscDeviceAndroidSAF.h",
    "Cemu/src/Cafe/Filesystem/fscDeviceWua.cpp"
]

# Aggiungiamo il log
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if not os.path.exists(log_file): log_file = "crash.log"
if os.path.exists(log_file):
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))

# 2. Copiamo i file
for f in files_to_copy:
    if os.path.exists(f):
        dest = os.path.join(temp_dir, os.path.basename(f))
        shutil.copy(f, dest)
        print(f"  Aggiunto: {f}")

# 3. Istruzioni per Claude (Aggiornate)
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 3)

Ciao Claude, avevi ragione! Il vero colpevole è il driver Android.
Ti ho allegato:
- `fscDeviceAndroidSAF.cpp` (il driver che parla con Android)
- `fscDeviceWua.cpp` (il lettore del formato .wua)
- `fsc.cpp` e `fsc.h` (il core del filesystem)
- `log.txt` (il crash)

## Il tuo compito
Implementa la lettura sicura (`safe_saf_read`) direttamente in `fscDeviceAndroidSAF.cpp`, perché è lì che avvengono le letture reali.
1. Cerca le chiamate a `read()`, `pread()`, o `AFile_read()` in `fscDeviceAndroidSAF.cpp`.
2. Implementa una funzione di lettura a prova di "Short Read" (loop `while`, gestione `EINTR`, ecc.).
3. Sostituisci le letture originali con la tua funzione sicura.
4. Verifica se `fscDeviceWua.cpp` ha bisogno di adattamenti per gestire i ritorni della nuova funzione.

## Formato dell'Output
Per favore, restituisci il codice completo dei file che modifichi, usando ESATTAMENTE questo formato per ogni file:
// FILE_START: <nome_del_file>
<codice_completo_del_file>
// FILE_END: <nome_del_file>
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V3.md"), 'w') as f:
    f.write(instructions)

# 4. Crea lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v3.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name} nella cartella Download. Pronto per Claude!")
