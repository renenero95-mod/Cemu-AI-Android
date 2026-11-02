import os
import shutil
import subprocess

dl_dir = os.path.expanduser("~/storage/downloads")
target_file = "Cemu/src/Cemu/Logging/CemuLogging.cpp"
claude_file = os.path.join(dl_dir, "CemuLogging.cpp")

if not os.path.exists(claude_file):
    print("❌ Assicurati di aver scaricato 'CemuLogging.cpp' in Download!")
    exit(1)

print("📁 Copiando il file CemuLogging.cpp...")
shutil.copy(claude_file, target_file)

print("📥 Scaricando l'originale...")
subprocess.run(f"wget -q -O orig_log.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cemu/Logging/CemuLogging.cpp", shell=True)

print("📦 Generazione patch...")
subprocess.run(f"git diff --no-index orig_log.cpp {target_file} > patch.diff", shell=True)
subprocess.run("sed -i 's|--- orig_log.cpp|--- a/src/Cemu/Logging/CemuLogging.cpp|' patch.diff", shell=True)
subprocess.run(f"sed -i 's|+++ {target_file}|+++ b/src/Cemu/Logging/CemuLogging.cpp|' patch.diff", shell=True)
if os.path.exists("orig_log.cpp"): os.remove("orig_log.cpp")

print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "Claude Fix v8: Log Append, Banner Sessione e Build Marker"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
