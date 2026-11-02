import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v7"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

print("📁 Preparazione Pacco v7...")

# 1. Copiamo il log
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file): 
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))
    print("  Aggiunto: log.txt")

# 2. Copiamo ZArchiveHelpers.h
helpers_path = "Cemu/src/util/helpers/ZArchiveHelpers.h"
if os.path.exists(helpers_path):
    shutil.copy(helpers_path, os.path.join(temp_dir, "ZArchiveHelpers.h"))
    print("  Aggiunto: ZArchiveHelpers.h")

# 3. Copiamo i file modificati
shutil.copy("Cemu/src/Cemu/Logging/CemuLogging.cpp", os.path.join(temp_dir, "CemuLogging.cpp"))
res = subprocess.run("find Cemu -name 'zarchivereader.cpp'", shell=True, capture_output=True, text=True)
if res.stdout:
    path_zarch = res.stdout.strip().split('\n')[0]
    shutil.copy(path_zarch, os.path.join(temp_dir, "zarchivereader.cpp"))
print("  Aggiunti: CemuLogging.cpp e zarchivereader.cpp")

# 4. Istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 7 - FINALE)

Ciao Claude. Ho applicato i tuoi fix a `ZArchiveReader` e ho forzato il log `CoreinitFile`.
Ho compilato e avviato Watch Dogs. Il gioco va in crash con lo stesso errore (r3=0 in InitArchiveCache).
MA IL LOG CORENITFILE NON C'È. Il log è identico a prima. 
Probabilmente avevi ragione tu: il crash avviene così in fretta che il thread del logger non fa in tempo a scrivere i file.

Ti ho allegato:
- `log.txt` (il log senza i dettagli CoreinitFile)
- `ZArchiveHelpers.h`
- `CemuLogging.cpp` (con il tuo fix)
- `zarchivereader.cpp` (con il tuo fix)

## Il tuo compito finale
1. Guarda `ZArchiveHelpers.h`. Vedi se c'è un percorso di apertura del `.wua` che bypassa tutto?
2. Il fix su `CemuLogging.cpp` è corretto? C'è un modo per forzare la scrittura IMMEDIATA del log (flush) per non perdere le ultime righe prima del crash?
3. C'è un modo per avvolgere `InitArchiveCache` (anche se è codice del gioco emulato) in un blocco try/catch o in un controllo di errore per evitare il crash e farci vedere cosa succede?

Dammi la soluzione definitiva o dimmi cosa fare per far apparire quel log.
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V7.md"), 'w') as f:
    f.write(instructions)

# 5. Creiamo lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v7.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name}. Pronto per essere caricato su Claude.")
