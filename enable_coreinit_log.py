import os
import subprocess

filepath = "Cemu/src/Cemu/Logging/CemuLogging.cpp"

with open(filepath, 'r') as f:
    content = f.read()

# Cerchiamo la funzione per impostare i log
func_sig = "void cemuLog_setActiveLoggingFlags(uint64 flagMask)"
idx = content.find(func_sig)

if idx != -1:
    # Troviamo la parentesi graffa di apertura
    start_body = content.find("{", idx)
    # Inseriamo la forzatura del flag
    injection = """
    // FORCE CORENIT FILE LOGGING
    flagMask |= (1ULL << (uint32)LogType::CoreinitFile);
"""
    content = content[:start_body+1] + injection + content[start_body+1:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    print("✅ Log CoreinitFile forzato nel codice.")
    
    # Creiamo la patch per GitHub
    print("📥 Scaricando originale per il diff...")
    subprocess.run("wget -q -O orig_Log.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/src/Cemu/Logging/CemuLogging.cpp", shell=True)
    
    subprocess.run(f"git diff --no-index orig_Log.cpp {filepath} > patch.diff", shell=True)
    subprocess.run("sed -i 's|--- orig_Log.cpp|--- a/src/Cemu/Logging/CemuLogging.cpp|' patch.diff", shell=True)
    subprocess.run(f"sed -i 's|+++ {filepath}|+++ b/src/Cemu/Logging/CemuLogging.cpp|' patch.diff", shell=True)
    if os.path.exists("orig_Log.cpp"): os.remove("orig_Log.cpp")
    
    print("🚀 Push su GitHub...")
    subprocess.run(["git", "add", "patch.diff"])
    subprocess.run(["git", "commit", "-m", "Debug: Forzato log CoreinitFile per tracciare errori WUA"])
    subprocess.run(["git", "push", "origin", "main"])
    print("✅ Fatto! Vai su GitHub Actions.")
else:
    print("❌ Funzione cemuLog_setActiveLoggingFlags non trovata nel file.")
