import os
import shutil
import zipfile
import subprocess
import re

temp_dir = "claude_upload_v5"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 1. Troviamo i file richiesti
print("🔍 Ricerca FdStream e ZArchiveReader...")
res = subprocess.run("find Cemu/src/ -type f \\( -name 'FdStream*' -o -name '*archivereader*' -o -name '*ZArchiveReader*' \\)", shell=True, capture_output=True, text=True)
files_to_copy = [f for f in res.stdout.strip().split('\n') if f]

# 2. Aggiungiamo il log
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file): shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))

# 3. Copiamo i file
for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))
        print(f"  Aggiunto: {os.path.basename(f)}")

# 4. Istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 5)

Ciao Claude. Il fix su `FileStream_saf.cpp` è stato compilato e pushato. 
Il crash però persiste, e il log non mostra "short read" di SAF, WUA o FileStream. La CPU va in crash leggendo `r3=0x00000000` in `CNomadArchiveManager::InitArchiveCache`.

Ti ho allegato `FdStream` e `ZArchiveReader`, come mi avevi chiesto.

## Il tuo compito
1. Analizza come `ZArchiveReader` apre e legge il file `.wua`. C'è un controllo che manca sugli errori?
2. Guarda `FdStream.h` (e i file collegati) per capire se una chiamata fallisce e restituisce 0.
3. Fornisci una patch mirata per impedire che un puntatore nullo arrivi al gioco, o per gestire l'errore in modo pulito.
4. Inoltre, dimmi come posso attivare il log `CoreinitFile` nel codice di Cemu (magari dimmi in che file e a che riga si trova `cemuLog_setLogLevel` per aggiungerlo).

## Formato dell'Output
Restituisci SOLO il codice completo dei file che modifichi, usando ESATTAMENTE questo formato:
// FILE_START: <nome_del_file>
<codice_completo_del_file>
// FILE_END: <nome_del_file>
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V5.md"), 'w') as f:
    f.write(instructions)

# 5. Crea ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v5.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name} nella cartella Download. Pronto per Claude!")
