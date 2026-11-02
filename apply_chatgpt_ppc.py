import os
import subprocess

target_file = "Cemu/src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"
orig_path = "src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"

# Il codice esatto fornito da ChatGPT
new_func = """\tinline static uint32 ppcMem_readDataU32(PPCInterpreter_t* hCPU, uint32 address)
\t{
\t\tauto logReadFault = [&]()
\t\t{
\t\t\tconst uint32 ip = hCPU->instructionPointer;
\t\t\tconst uint32 lr = hCPU->spr.LR;

\t\t\tif (memory_isValidRange(ip, sizeof(uint32)))
\t\t\t{
\t\t\t\tconst uint32 instruction = memory_readCodeU32(hCPU, ip);
\t\t\t\tconst uint32 primaryOpcode = instruction >> 26;

\t\t\t\tif (primaryOpcode == 32) // LWZ
\t\t\t\t{
\t\t\t\t\tconst uint32 rt = (instruction >> 21) & 0x1F;
\t\t\t\t\tconst uint32 ra = (instruction >> 16) & 0x1F;
\t\t\t\t\tconst sint16 displacement = (sint16)(instruction & 0xFFFF);

\t\t\t\t\tcemuLog_log(LogType::Force,
\t\t\t\t\t\t"[PPC READ FAULT] LWZ"
\t\t\t\t\t\t" EA=0x{:08x}"
\t\t\t\t\t\t" IP=0x{:08x}"
\t\t\t\t\t\t" LR=0x{:08x}"
\t\t\t\t\t\t" instruction=0x{:08x}"
\t\t\t\t\t\t" RT=r{}"
\t\t\t\t\t\t" RA=r{}"
\t\t\t\t\t\t" displacement={}",
\t\t\t\t\t\taddress, ip, lr, instruction,
\t\t\t\t\t\trt, ra, displacement);
\t\t\t\t}
\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tcemuLog_log(LogType::Force,
\t\t\t\t\t\t"[PPC READ FAULT] Non-LWZ"
\t\t\t\t\t\t" EA=0x{:08x}"
\t\t\t\t\t\t" IP=0x{:08x}"
\t\t\t\t\t\t" LR=0x{:08x}"
\t\t\t\t\t\t" instruction=0x{:08x}"
\t\t\t\t\t\t" opcode={}",
\t\t\t\t\t\taddress, ip, lr, instruction, primaryOpcode);
\t\t\t\t}
\t\t\t}
\t\t\telse
\t\t\t{
\t\t\t\tcemuLog_log(LogType::Force,
\t\t\t\t\t"[PPC READ FAULT] EA=0x{:08x}"
\t\t\t\t\t" IP=0x{:08x} (instruction address invalid)"
\t\t\t\t\t" LR=0x{:08x}",
\t\t\t\t\taddress, ip, lr);
\t\t\t}
\t\t};

\t\tif (!memory_isValidRange(address, sizeof(uint32)))
\t\t{
\t\t\tlogReadFault();
\t\t\tPPCState_t_dataAccessFault(hCPU, address);
\t\t\treturn 0;
\t\t}

\t\tvoid* ptr = memory_getPointerFromVirtualOffset(address);
\t\tif (!ptr)
\t\t{
\t\t\tlogReadFault();
\t\t\tPPCState_t_dataAccessFault(hCPU, address);
\t\t\treturn 0;
\t\t}

\t\tuint32 v;
\t\tstd::memcpy(&v, ptr, sizeof(uint32));
\t\treturn CPU_swapEndianU32(v);
\t}"""

print("📁 Lettura del file originale...")
with open(target_file, 'r') as f:
    content = f.read()

# Trova l'inizio della funzione (cerca la stringa)
start_idx = content.find("inline static uint32 ppcMem_readDataU32")
if start_idx == -1:
    print("❌ Impossibile trovare la funzione nel file.")
    exit(1)

# Trova la parentesi graffa di apertura
brace_start = content.find("{", start_idx)
braces = 0
end_idx = -1

# Trova la parentesi graffa di chiusura corrispondente
for i in range(brace_start, len(content)):
    if content[i] == '{': braces += 1
    elif content[i] == '}':
        braces -= 1
        if braces == 0:
            end_idx = i
            break

if end_idx == -1:
    print("❌ Impossibile trovare la fine della funzione.")
    exit(1)

print("✂️ Sostituzione della funzione in corso...")
# Sostituisce la vecchia funzione con quella nuova
new_content = content[:start_idx] + new_func + content[end_idx+1:]

with open(target_file, 'w') as f:
    f.write(new_content)

print("📥 Scaricando l'originale per il diff...")
subprocess.run(f"wget -q -O orig_ppc.cpp https://raw.githubusercontent.com/SapphireRhodonite/Cemu/android-port/{orig_path}", shell=True)

print("📦 Generazione patch...")
res = subprocess.run(["git", "diff", "--no-index", "orig_ppc.cpp", target_file], capture_output=True, text=True)
diff_text = res.stdout
diff_text = diff_text.replace("a/orig_ppc.cpp", f"a/{orig_path}")
diff_text = diff_text.replace(f"b/{target_file}", f"b/{orig_path}")

with open("patch.diff", "w") as f:
    f.write(diff_text)

if os.path.exists("orig_ppc.cpp"): os.remove("orig_ppc.cpp")

print("🚀 Push su GitHub...")
subprocess.run(["git", "add", "patch.diff"])
subprocess.run(["git", "commit", "-m", "ChatGPT Fix: Logger PPC READ FAULT per LWZ"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
