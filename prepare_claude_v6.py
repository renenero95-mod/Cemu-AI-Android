import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v6"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 1. Troviamo e copiamo i file richiesti da Claude (Mega-Pacco)
print("🔍 Ricerca dei file di ZArchive, TitleList, Logging e Filesystem...")
# Cerchiamo in tutto il progetto per essere sicuri di trovare zarchivereader
res = subprocess.run("find Cemu -type f \\( -name '*zarchive*' -o -name 'TitleInfo.cpp' -o -name 'CemuLogging.*' -o -name 'FdStream*' \\)", shell=True, capture_output=True, text=True)
files_to_copy = [f for f in res.stdout.strip().split('\n') if f]

# Aggiungiamo anche il log
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file): shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))

# Copiamo i file
for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))
        print(f"  Aggiunto: {os.path.basename(f)}")

# Aggiungiamo i file del FileSystem (dove avvengono le letture)
fs_dir = "Cemu/src/Cafe/Filesystem"
if os.path.exists(fs_dir):
    for f in os.listdir(fs_dir):
        if f.endswith(".cpp") or f.endswith(".h"):
            shutil.copy(os.path.join(fs_dir, f), os.path.join(temp_dir, f))
            print(f"  Aggiunto (FS): {f}")

# 2. Istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 6)

Ciao Claude, hai perfettamente ragione. Ti ho preparato un pacchetto "Mega" con tutto quello che serve:
- Il file `zarchivereader.cpp` e `.h` (cercati in tutto il progetto)
- Il file `TitleInfo.cpp` (dove viene aperto il .wua)
- I file `CemuLogging.cpp` e `.h`
- L'intera cartella `Cafe/Filesystem`
- `FdStream.h`

## Il problema da risolvere
Il gioco va in crash (`r3=0`) in `InitArchiveCache` perché una chiamata precedente (come FSOpenFile o ZArchiveReader) fallisce e restituisce zero.
Inoltre, non sappiamo quale file specifico fallisce.

## Il tuo compito
1. Analizza `zarchivereader.cpp`. Viene usato `std::ifstream`, `FdStream`, o un altro metodo di lettura? Se usa un percorso diverso da `FileStream_saf`, correggilo per gestire le short reads di Android SAF.
2. Analizza `TitleInfo.cpp` e come viene aperto il `.wua`.
3. Forniscimi il codice per attivare il log `CoreinitFile` (ti ho allegato `CemuLogging.cpp`). Dimmi esattamente cosa modificare, o restituisci il file `CemuLogging.cpp` modificato.

## Formato dell'Output
Restituisci SOLO il codice completo dei file che modifichi, usando ESATTAMENTE questo formato:
// FILE_START: <nome_del_file>
<codice_completo_del_file>
// FILE_END: <nome_del_file>
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V6.md"), 'w') as f:
    f.write(instructions)

# 3. Crea lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v6.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name} nella cartella Download. Pronto per Claude!")
