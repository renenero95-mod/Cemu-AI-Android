import os
import subprocess

target_file = "Cemu/src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"
orig_path = "src/Cafe/HW/Espresso/Interpreter/PPCInterpreterImpl.cpp"

# Il nuovo codice fornito da ChatGPT
new_func = """	inline static uint32 ppcMem_readDataU32(PPCInterpreter_t* hCPU, uint32 address)
	{
		if (!memory_isValidRange(address, sizeof(uint32)))
		{
			const uint32 ip = hCPU->instructionPointer;

			if (memory_isValidRange(ip, sizeof(uint32)))
			{
				const uint32 instruction = memory_readCodeU32(hCPU, ip);
				const uint32 opcode = instruction >> 26;

				if (opcode == 32) // LWZ
				{
					const uint32 rt = (instruction >> 21) & 0x1F;
					const uint32 ra = (instruction >> 16) & 0x1F;
					const sint16 displacement = (sint16)(instruction & 0xFFFF);

					cemuLog_log(LogType::Force,
						"[PPC READ FAULT] LWZ"
						" EA=0x{:08X}"
						" IP=0x{:08X}"
						" instruction=0x{:08X}"
						" RT=r{}"
						" RA=r{}"
						" displacement={}",
						address,
						ip,
						instruction,
						rt,
						ra,
						displacement);
				}
				else
				{
					cemuLog_log(LogType::Force,
						"[PPC READ FAULT] Non-LWZ"
						" EA=0x{:08X}"
						" IP=0x{:08X}"
						" instruction=0x{:08X}"
						" opcode={}",
						address,
						ip,
						instruction,
						opcode);
				}
			}
			else
			{
				cemuLog_log(LogType::Force,
					"[PPC READ FAULT] EA=0x{:08X}"
					" IP=0x{:08X}"
					" (invalid instruction address)",
					address,
					ip);
			}

			PPCState_t_dataAccessFault(hCPU, address);
			return 0;
		}

		void* ptr = memory_getPointerFromVirtualOffset(address);

		if (ptr == nullptr)
		{
			cemuLog_log(LogType::Force,
				"[PPC READ FAULT] Null pointer"
				" EA=0x{:08X}"
				" IP=0x{:08X}",
				address,
				hCPU->instructionPointer);

			PPCState_t_dataAccessFault(hCPU, address);
			return 0;
		}

		uint32 v;
		std::memcpy(&v, ptr, sizeof(uint32));

		return CPU_swapEndianU32(v);
	}"""

print("📁 Lettura del file originale...")
with open(target_file, 'r') as f:
    content = f.read()

# Trova l'inizio della vecchia funzione
start_str = "inline static uint32 ppcMem_readDataU32(PPCInterpreter_t* hCPU, uint32 address)"
start_idx = content.find(start_str)

if start_idx == -1:
    print("❌ Impossibile trovare la vecchia funzione nel file.")
    exit(1)

# Trova la parentesi graffa di apertura
brace_start = content.find("{", start_idx)
braces = 0
end_idx = -1

# Trova la parentesi graffa di chiusura corrispondente contandole
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

print("✂️ Sostituzione della funzione in corso (conteggio parentesi sicuro)...")
# Sostituisce l'intera funzione
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
subprocess.run(["git", "commit", "-m", "ChatGPT Fix v2: Logger PPC READ FAULT per LWZ (codice pulito)"])
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
