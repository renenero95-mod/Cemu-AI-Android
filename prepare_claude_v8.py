import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v8"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

print("📁 Preparazione Pacco v8 (Log Unico con Separatori)...")

# 1. Copiamo il log
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file): 
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))
    print("  Aggiunto: log.txt")

# 2. Copiamo i file modificati
shutil.copy("Cemu/src/Cafe/Filesystem/fsc.cpp", os.path.join(temp_dir, "fsc.cpp"))
shutil.copy("Cemu/src/Cemu/Logging/CemuLogging.cpp", os.path.join(temp_dir, "CemuLogging.cpp"))
res = subprocess.run("find Cemu -name 'zarchivereader.cpp'", shell=True, capture_output=True, text=True)
if res.stdout:
    path_zarch = res.stdout.strip().split('\n')[0]
    shutil.copy(path_zarch, os.path.join(temp_dir, "zarchivereader.cpp"))
print("  Aggiunti file di codice.")

# 3. Istruzioni per Claude (AGGIORNATE)
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 8)

Ciao Claude. Ho applicato il tuo log in `fsc.cpp` (LogType::Force) e ricompilato.
Il gioco crasha ancora in `InitArchiveCache` con `r3=0`. MA NEL LOG NON C'È NESSUNA RIGA "FSC open". 
Questo significa che il crash avviene PRIMA di aprire un file (forse una malloc fallita o un FSGetStat?).

## LE TUE DUE MISSIONI:

### Missione 1: Risolvere il crash (r3=0)
Ti ho allegato il log, `fsc.cpp`, `CemuLogging.cpp` e `zarchivereader.cpp`.
1. Se non ci sono log di `fsc_open`, quali altre funzioni (es. `FSGetStat`, `FSReadDir`, o `malloc`) falliscono prima?
2. Come possiamo loggare le richieste di allocazione di memoria (`MEMAllocFromDefaultHeap`) per vedere se il gioco esaurisce la RAM?
3. Come possiamo intercettare l'errore a monte per evitare il crash?

### Missione 2: Log Unico con Append e Separatori (NO timestamp)
Voglio che tu modifichi `CemuLogging.cpp` in modo che:
1. Il file `log.txt` NON venga mai sovrascritto, ma aperto in modalità Append (es. `std::ios::app` in C++).
2. Ogni volta che viene avviato un nuovo gioco (cerca dove nel codice viene stampato "Run title" nel log), venga inserita una riga di separazione evidente, tipo:
`=========================================================`
`================== NUOVA SESSIONE DI GIOCO ==================`
`=========================================================`
In questo modo posso avere tutti i test in un unico file e capire dove inizia uno e finisce l'altro.

## Formato dell'Output
Restituisci il codice completo di `CemuLogging.cpp` (e le eventuali patch per la memoria), usando il solito formato `// FILE_START` e `// FILE_END`.
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V8.md"), 'w') as f:
    f.write(instructions)

# 4. Creiamo lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v8.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name} con le nuove istruzioni per il Log Unico!")
