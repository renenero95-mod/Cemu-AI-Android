import os
import shutil
import zipfile

# File da includere
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if not os.path.exists(log_file): log_file = "crash.log"

source_file = "Cemu/src/Cafe/OS/libs/coreinit/coreinit_FS.cpp"
ppc_file = "Cemu/src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"

# Creiamo la cartella temporanea
temp_dir = "claude_upload"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 1. Copiamo i file
print("📁 Copiando i file nel pacco...")
shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))
shutil.copy(source_file, os.path.join(temp_dir, "coreinit_FS.cpp"))
shutil.copy(ppc_file, os.path.join(temp_dir, "PPCInterpreterImpl.cpp"))

# 2. Creiamo le istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix)

Ciao Claude. Sei un esperto sviluppatore C++ specializzato in emulatori. 
Stiamo lavorando su Cemu per Android.

## Il Problema
Watch Dogs (un gioco pesante) va in crash con `Signal 11` (SIGSEGV). Il log mostra che il crash avviene nella funzione `ppcMem_readDataU32` (file PPCInterpreterImpl.cpp), ma la causa radice è il caricamento del file `.wua` (un archivio enorme).
Su Android, il sistema di storage (SAF) fa le "Short Reads": la funzione `read()` o `pread()` legge meno byte del richiesto, lasciando la memoria piena di zeri. Il gioco va in crash quando legge questi zeri.

## Il tuo compito
Devi modificare il file `coreinit_FS.cpp` per implementare una lettura sicura.
Ti ho allegato il file del File System (`coreinit_FS.cpp`).

1. Aggiungi una funzione `safe_saf_read` (con un loop `while (totalRead < count)`) per garantire che TUTTI i byte vengano letti.
2. Modifica le funzioni di lettura del file system all'interno di `coreinit_FS.cpp` per usare `safe_saf_read` invece delle normali chiamate `read()` o `pread()`.

## Formato dell'Output
Per favore, restituisci **SOLO ED ESCLUSIVAMENTE** il codice completo e modificato del file `coreinit_FS.cpp`.
Non scrivere spiegazioni, non usare i blocchi markdown (```cpp). 
Inizia il tuo output esattamente con questa riga:
<<<FILE_START>>>
...e finisci il tuo output esattamente con questa riga:
<<<FILE_END>>>
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_PER_CLAUDE.md"), 'w') as f:
    f.write(instructions)

# 3. Creiamo lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context.zip")
print(f"🗜️ Creazione archivio ZIP in {zip_name}...")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            zipf.write(os.path.join(root, file), file)

shutil.rmtree(temp_dir)
print("✅ Fatto! Il file 'claude_context.zip' è pronto nella cartella Download del telefono.")
