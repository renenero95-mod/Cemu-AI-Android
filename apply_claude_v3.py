import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")
target_saf = "Cemu/src/Cafe/Filesystem/fscDeviceAndroidSAF.cpp"
target_wua = "Cemu/src/Cafe/Filesystem/fscDeviceWua.cpp"

# 1. Controlliamo che i file di Claude siano in Download
claude_saf = os.path.join(dl_dir, "fscDeviceAndroidSAF.cpp")
claude_wua = os.path.join(dl_dir, "fscDeviceWua.cpp")

if not os.path.exists(claude_saf) or not os.path.exists(claude_wua):
    print("❌ Errore: Assicurati di aver scaricato i file 'fscDeviceAndroidSAF.cpp' e 'fscDeviceWua.cpp' nella cartella Download!")
    exit(1)

print("📁 Copiando i file di Claude nel progetto...")
shutil.copy(claude_saf, target_saf)
shutil.copy(claude_wua, target_wua)

# 2. Scarichiamo gli originali per fare il diff
print("📥 Scaricando gli originali da GitHub per il confronto...")
subprocess.run("wget -q -O orig_SAF.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cafe/Filesystem/fscDeviceAndroidSAF.cpp", shell=True)
subprocess.run("wget -q -O orig_WUA.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cafe/Filesystem/fscDeviceWua.cpp", shell=True)

# 3. Creiamo le due patch separate
print("📦 Generazione della patch...")
subprocess.run(f"git diff --no-index orig_SAF.cpp {target_saf} > patch_SAF.diff", shell=True)
subprocess.run(f"git diff --no-index orig_WUA.cpp {target_wua} > patch_WUA.diff", shell=True)

# 4. Sistemiamo i percorsi per GitHub Actions
subprocess.run("sed -i 's|--- orig_SAF.cpp|--- a/src/Cafe/Filesystem/fscDeviceAndroidSAF.cpp|' patch_SAF.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {target_saf}|+++ b/src/Cafe/Filesystem/fscDeviceAndroidSAF.cpp|' patch_SAF.diff", shell=True)

subprocess.run("sed -i 's|--- orig_WUA.cpp|--- a/src/Cafe/Filesystem/fscDeviceWua.cpp|' patch_WUA.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {target_wua}|+++ b/src/Cafe/Filesystem/fscDeviceWua.cpp|' patch_WUA.diff", shell=True)

# 5. Uniamo le patch in un unico file
with open("patch.diff", "w") as outfile:
    for fname in ["patch_SAF.diff", "patch_WUA.diff"]:
        if os.path.exists(fname):
            with open(fname) as infile:
                outfile.write(infile.read())

# Pulizia
for f in ["orig_SAF.cpp", "orig_WUA.cpp", "patch_SAF.diff", "patch_WUA.diff"]:
    if os.path.exists(f): os.remove(f)

print("✅ Patch creata con successo!")

# 6. Push su GitHub
print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v3: safe_saf_read e safe_archive_read (SAF e WUA)"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
