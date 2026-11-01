import os
import subprocess
import re

# 1. Aumentiamo il livello di log globale di Cemu
log_file = "Cemu/src/Cemu/Logging/Logging.cpp"
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        content = f.read()
    # Forza il livello a Debug se esiste una configurazione
    content = content.replace("cemuLog_setLogLevel(LogType::Info);", "cemuLog_setLogLevel(LogType::Debug);")
    content = content.replace("cemuLog_setLogLevel(LogType::Warning);", "cemuLog_setLogLevel(LogType::Debug);")
    with open(log_file, 'w') as f:
        f.write(content)
    print("✅ Livello di log globale impostato su Debug.")
else:
    print("⚠️ File Logging.cpp non trovato, salto questo passaggio.")

# 2. Iniettiamo un logger per tracciare gli accessi alla memoria
target_file = "Cemu/src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"
if os.path.exists(target_file):
    with open(target_file, 'r') as f:
        code = f.read()

    # Cerchiamo la funzione ppcMem_readDataU32
    idx = code.find("ppcMem_readDataU32(PPCInterpreter_t* hCPU, uint32 address)")
    if idx != -1:
        start_body = code.find("{", idx)
        # Inseriamo il log subito dopo la parentesi graffa di apertura
        injection = f'''
    // --- DEBUG LOG INJECTION ---
    void* ptr_debug = memory_getPointerFromVirtualOffset(address);
    if (ptr_debug == nullptr) {{
        cemuLog_log(LogType::Force, "[DEEP DEBUG] Tentativo di leggere da indirizzo NON VALIDO: 0x{{:08X}} - IP: 0x{{:08X}}", address, hCPU->instructionPointer);
    }}
    // ---------------------------
'''
        code = code[:start_body+1] + injection + code[start_body+1:]
        with open(target_file, 'w') as f:
            f.write(code)
        print("✅ Logger di memoria iniettato in PPCInterpreterImpl.cpp.")
    else:
        print("⚠️ Funzione ppcMem_readDataU32 non trovata, salto l'iniezione.")

# 3. Push su GitHub
print("🚀 Preparazione del push su GitHub...")
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Feat: Deep Debugging - Livello log massimo e tracciamento indirizzi di memoria"])
print("🔄 Push in corso (potrebbe chiedere le credenziali)...")
subprocess.run(["git", "push", "origin", "main"])
print("✅ Push completato! Vai su GitHub Actions per compilare.")
