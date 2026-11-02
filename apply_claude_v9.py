import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")

# Percorsi di destinazione nel progetto
targets = {
    "coreinit_MEM.cpp": "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM.cpp",
    "coreinit_MEM_ExpHeap.cpp": "Cemu/src/Cafe/OS/libs/coreinit/coreinit_MEM_ExpHeap.cpp",
    "fscDeviceWua.cpp": "Cemu/src/Cafe/Filesystem/fscDeviceWua.cpp"
}

print("📁 Copiando i file di Claude...")
for filename, target_path in targets.items():
    claude_file = os.path.join(dl_dir, filename)
    if not os.path.exists(claude_file):
        print(f"❌ Errore: Manca {filename} in Download!")
        exit(1)
    shutil.copy(claude_file, target_path)

print("📥 Scaricando gli originali per il diff...")
orig_paths = {
    "coreinit_MEM.cpp": "src/Cafe/OS/libs/coreinit/coreinit_MEM.cpp",
    "coreinit_MEM_ExpHeap.cpp": "src/Cafe/OS/libs/coreinit/coreinit_MEM_ExpHeap.cpp",
    "fscDeviceWua.cpp": "src/Cafe/Filesystem/fscDeviceWua.cpp"
}

for filename, orig_path in orig_paths.items():
    url = f"https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/{orig_path}"
    subprocess.run(f"wget -q -O orig_{filename} {url}", shell=True)

print("📦 Generazione della patch unificata...")
with open("patch.diff", "w") as patch_file:
    for filename, target_path in targets.items():
        res = subprocess.run(["git", "diff", "--no-index", f"orig_{filename}", target_path], capture_output=True, text=True)
        diff_text = res.stdout
        
        # Sostituiamo i percorsi per GitHub
        diff_text = diff_text.replace(f"a/orig_{filename}", f"a/{orig_paths[filename]}")
        diff_text = diff_text.replace(f"b/{target_path}", f"b/{orig_paths[filename]}")
        
        patch_file.write(diff_text)

# Pulizia file temporanei
for filename in targets.keys():
    if os.path.exists(f"orig_{filename}"): 
        os.remove(f"orig_{filename}")

print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v9: Log di allocazione memoria e diagnostica WUA"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions e aspetta la build.")
