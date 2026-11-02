import os
import shutil
import zipfile
import subprocess

temp_dir = "claude_upload_v4"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Troviamo i file di basso livello richiesti da Claude
print("🔍 Ricerca dei file FileStream e FilesystemAndroid...")
res = subprocess.run("find Cemu/src/Common/ -type f \\( -name 'FileStream*' -o -name 'FilesystemAndroid*' \\)", shell=True, capture_output=True, text=True)
files_to_copy = [f for f in res.stdout.strip().split('\n') if f]

# Aggiungiamo anche il log più recente
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if not os.path.exists(log_file): log_file = "crash.log"
if os.path.exists(log_file):
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))

# Copiamo i file
for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))
        print(f"  Aggiunto: {os.path.basename(f)}")

# Istruzioni per Claude
instructions = """
# ISTRUZIONI PER CLAUDE (Cemu Android Fix - Parte 4)

Ciao Claude. Il tuo fix per `fscDeviceAndroidSAF.cpp` e `fscDeviceWua.cpp` è stato compilato, ma il gioco crasha ancora. 
Il tuo log personalizzato ("safe_saf_read: short read") NON è apparso nel log di Cemu. Quindi la lettura parziale potrebbe avvenire più in basso.

## Il Crash Attuale
Il crash è ancora `Signal 11` in `ppcMem_readDataU32`. 
La CPU emulata (PowerPC) sta cercando di leggere un indirizzo nullo: `r3 = 0x00000000`. Il gioco ha ricevuto un puntatore vuoto da una funzione precedente e non ha controllato.

## Il tuo compito
Ti ho allegato i file di basso livello che mi avevi chiesto:
- `FileStream.cpp` e `FileStream.h`
- `FilesystemAndroid.cpp` e `FilesystemAndroid.h`
- `log.txt` (il nuovo log)

Analizza `FileStream::readData()`. C'è una possibilità che su Android SAF questa funzione restituisca 0 (o -1) senza gestire correttamente un errore di I/O? O che restituisca un buffer corrotto?
Voglio che tu implementi la lettura sicura (safe_saf_read) direttamente dentro `FileStream.cpp` se necessario, o che mi dica esattamente dove si genera questo `0x00000000`.

## Formato dell'Output
Restituisci SOLO il codice completo dei file che modifichi, usando ESATTAMENTE questo formato:
// FILE_START: <nome_del_file>
<codice_completo_del_file>
// FILE_END: <nome_del_file>
"""
with open(os.path.join(temp_dir, "ISTRUZIONI_V4.md"), 'w') as f:
    f.write(instructions)

# Crea lo ZIP
zip_name = os.path.expanduser("~/storage/downloads/claude_context_v4.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name} nella cartella Download. Pronto per Claude!")
