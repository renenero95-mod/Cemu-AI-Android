import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")
target_file = "Cemu/src/Common/FileStream_saf.cpp"
orig_file = "Cemu/src/Common/FileStream_saf.h" # Finto, serve solo per far capire a Cemu la cartella

claude_file = os.path.join(dl_dir, "FileStream_saf.cpp")
if not os.path.exists(claude_file):
    print("❌ Assicurati di aver scaricato 'FileStream_saf.cpp' in Download!")
    exit(1)

# 1. Copia il file di Claude
print("📁 Copiando il file di Claude...")
shutil.copy(claude_file, target_file)

# 2. Scarica l'originale
print("📥 Scaricando l'originale da GitHub...")
subprocess.run("wget -q -O orig_FS.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Common/FileStream_saf.cpp", shell=True)

# 3. Crea la patch
print("📦 Generazione patch...")
subprocess.run(f"git diff --no-index orig_FS.cpp {target_file} > patch.diff", shell=True)
subprocess.run("sed -i 's|--- orig_FS.cpp|--- a/src/Common/FileStream_saf.cpp|' patch.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {target_file}|+++ b/src/Common/FileStream_saf.cpp|' patch.diff", shell=True)
if os.path.exists("orig_FS.cpp"): os.remove("orig_FS.cpp")

# 4. Push
print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v4: Risolto failbit in FileStream_saf (Android)"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
