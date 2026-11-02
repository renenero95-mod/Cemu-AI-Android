import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")
target_path = "Cemu/src/Cemu/Logging/CemuLogging.cpp"
claude_file = os.path.join(dl_dir, "CemuLogging.cpp")

if not os.path.exists(claude_file):
    print("❌ Assicurati di aver scaricato 'CemuLogging.cpp' in Download!")
    exit(1)

print("📁 Copiando il file di Claude...")
shutil.copy(claude_file, target_path)

print("📥 Scaricando l'originale...")
subprocess.run("wget -q -O orig_log.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cemu/Logging/CemuLogging.cpp", shell=True)

print("📦 Generazione della patch con i percorsi corretti...")
res = subprocess.run(["git", "diff", "--no-index", "orig_log.cpp", target_path], capture_output=True, text=True)
diff_text = res.stdout

# Sostituiamo i percorsi in modo che GitHub li capisca (relativi alla cartella Cemu)
# Sostituisce 'a/orig_log.cpp' con 'a/src/Cemu/Logging/CemuLogging.cpp'
diff_text = diff_text.replace("a/orig_log.cpp", "a/src/Cemu/Logging/CemuLogging.cpp")
# Sostituisce 'b/Cemu/src/...' con 'b/src/Cemu/...'
diff_text = diff_text.replace(f"b/{target_path}", "b/src/Cemu/Logging/CemuLogging.cpp")

with open("patch.diff", "w") as f:
    f.write(diff_text)

if os.path.exists("orig_log.cpp"): os.remove("orig_log.cpp")

print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Fix Patch: Corretto percorsi per GitHub Actions"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
