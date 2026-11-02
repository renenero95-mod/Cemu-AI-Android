import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v9"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

print("📁 Preparazione Pacco v9 (Memory Logging)...")

# 1. Copiamo il log (se c'è, altrimenti usa quello vecchio)
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file): 
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))
    print("  Aggiunto: log.txt")

# 2. Copiamo i file di memoria che Claude ci ha chiesto
mem_files = [
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM.cpp",
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_BlockHeap.cpp",
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_ExpHeap.cpp",
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_FrmHeap.cpp",
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_UnitHeap.cpp"
]
for f in mem_files:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))
        print(f"  Aggiunto: {os.path.basename(f)}")

# 3. Istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 9)

Ciao Claude. Ecco i file di memoria che mi avevi chiesto.
Il gioco crasha sempre con `r3=0` (puntatore nullo) in una funzione chiamata da `InitArchiveCache`.

## Il tuo compito
1. Analizza come funziona `MEMAllocFromDefaultHeap` e le altre funzioni di allocazione nei file che ti ho allegato.
2. Aggiungi dei log (`cemuLog_log(LogType::Force, ...)`) all'interno delle funzioni di allocazione per tracciare:
   - La dimensione richiesta.
   - Il puntatore restituito (se è 0, loggalo come errore evidente!).
   - L'heap utilizzato.
3. Se pensi che il problema non sia la memoria, dimmi se c'è un altro punto in cui inserire log per capire cosa restituisce `0` al gioco.

## Formato dell'Output
Restituisci il codice completo dei file che modifichi (specialmente `coreinit_MEM.cpp`), usando il solito formato `// FILE_START` e `// FILE_END`.
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V9.md"), 'w') as f:
    f.write(instructions)

# 4. Creiamo lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v9.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name}. Pronto per essere caricato su Claude.")
