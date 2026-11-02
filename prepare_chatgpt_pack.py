import os
import shutil
import zipfile

temp_dir = "chatgpt_upload"
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

print("📁 Preparazione Pacco per ChatGPT...")

files_to_copy = [
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM.cpp",
    "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_ExpHeap.cpp",
    "Cemu/src/Cafe/Filesystem/fscDeviceWua.cpp",
    "Cemu/src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"
]

for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))
        print(f"  Aggiunto: {os.path.basename(f)}")

# Aggiungiamo anche il log più recente
log_file = os.path.expanduser("~/storage/downloads/log.txt")
if os.path.exists(log_file):
    shutil.copy(log_file, os.path.join(temp_dir, "log.txt"))
    print("  Aggiunto: log.txt")

zip_name = os.path.expanduser("~/storage/downloads/chatgpt_context.zip")
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = os.path.join(root, file)
            zipf.write(filepath, os.path.basename(filepath))

shutil.rmtree(temp_dir)
print(f"✅ Creato {zip_name}. Pronto per essere caricato su ChatGPT.")
