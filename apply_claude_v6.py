import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")

# 1. Troviamo i percorsi esatti nel progetto
print("🔍 Ricerca dei percorsi originali...")
res = subprocess.run("find Cemu -name 'CemuLogging.cpp'", shell=True, capture_output=True, text=True)
path_logging = res.stdout.strip().split('\n')[0]

# ZArchiveReader di solito sta in dependencies
res = subprocess.run("find Cemu -name 'zarchivereader.cpp'", shell=True, capture_output=True, text=True)
path_zarchive = res.stdout.strip().split('\n')[0]

if not path_logging or not path_zarchive:
    print("❌ Impossibile trovare i file originali nel progetto.")
    exit(1)

print(f"📁 Logging: {path_logging}")
print(f"📁 ZArchive: {path_zarchive}")

# 2. Copiamo i file di Claude
claude_logging = os.path.join(dl_dir, "CemuLogging.cpp")
claude_zarchive = os.path.join(dl_dir, "zarchivereader.cpp")

if not os.path.exists(claude_logging) or not os.path.exists(claude_zarchive):
    print("❌ Assicurati di aver scaricato 'CemuLogging.cpp' e 'zarchivereader.cpp' in Download!")
    exit(1)

shutil.copy(claude_logging, path_logging)
shutil.copy(claude_zarchive, path_zarchive)
print("✅ File di Claude copiati nel progetto.")

# 3. Scarichiamo gli originali per il diff
print("📥 Scaricando gli originali...")
subprocess.run(f"wget -q -O orig_log.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/{path_logging.replace('Cemu/', '')}", shell=True)
subprocess.run(f"wget -q -O orig_zarch.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/{path_zarchive.replace('Cemu/', '')}", shell=True)

# 4. Creiamo la patch
print("📦 Generazione patch...")
subprocess.run(f"git diff --no-index orig_log.cpp {path_logging} > patch_log.diff", shell=True)
subprocess.run(f"git diff --no-index orig_zarch.cpp {path_zarchive} > patch_zarch.diff", shell=True)

# Sistemiamo i percorsi per GitHub
subprocess.run(f"sed -i 's|--- orig_log.cpp|--- a/{path_logging.replace('Cemu/', '')}|' patch_log.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {path_logging}|+++ b/{path_logging.replace('Cemu/', '')}|' patch_log.diff", shell=True)

subprocess.run(f"sed -i 's|--- orig_zarch.cpp|--- a/{path_zarchive.replace('Cemu/', '')}|' patch_zarch.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {path_zarchive}|+++ b/{path_zarchive.replace('Cemu/', '')}|' patch_zarch.diff", shell=True)

# Uniamo
with open("patch.diff", "w") as out:
    for f in ["patch_log.diff", "patch_zarch.diff"]:
        if os.path.exists(f):
            with open(f) as infile:
                out.write(infile.read())

# Pulizia
for f in ["orig_log.cpp", "orig_zarch.cpp", "patch_log.diff", "patch_zarch.diff"]:
    if os.path.exists(f): os.remove(f)

# 5. Push
print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v6: Risolto failbit in ZArchiveReader e forzato log CoreinitFile"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
