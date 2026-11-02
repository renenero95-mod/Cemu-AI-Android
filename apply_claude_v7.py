import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")
target_file = "Cemu/src/Cafe/Filesystem/fsc.cpp"
claude_file = os.path.join(dl_dir, "fsc.cpp")

if not os.path.exists(claude_file):
    print("❌ Errore: Assicurati di aver scaricato 'fsc.cpp' in Download!")
    exit(1)

# 1. Copia il file
print("📁 Copiando il file fsc.cpp di Claude...")
shutil.copy(claude_file, target_file)

# 2. Scarica l'originale
print("📥 Scaricando l'originale...")
subprocess.run("wget -q -O orig_fsc.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cafe/Filesystem/fsc.cpp", shell=True)

# 3. Crea patch
print("📦 Generazione patch...")
subprocess.run(f"git diff --no-index orig_fsc.cpp {target_file} > patch.diff", shell=True)
subprocess.run("sed -i 's|--- orig_fsc.cpp|--- a/src/Cafe/Filesystem/fsc.cpp|' patch.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {target_file}|+++ b/src/Cafe/Filesystem/fsc.cpp|' patch.diff", shell=True)
if os.path.exists("orig_fsc.cpp"): os.remove("orig_fsc.cpp")

# 4. Push
print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v7: Logging diretto in fsc.cpp per scovare errori di apertura"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
