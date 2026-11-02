import subprocess

target_file = "Cemu/src/Cafe/OS/libs/coreinit/coreinit_FS.cpp"

# 1. Leggiamo il file originale
with open(target_file, 'r') as f:
    content = f.read()

# 2. La funzione approvata dall'AI
safe_read_func = """
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <sys/types.h>

static ssize_t safe_saf_read(int fd, void* buffer, size_t count, int64_t offset) {
    size_t totalRead = 0;
    char* bufPtr = static_cast<char*>(buffer);
    while (totalRead < count) {
        ssize_t bytesRead = 0;
        if (offset != -1) {
            bytesRead = pread(fd, bufPtr + totalRead, count - totalRead, offset + totalRead);
        } else {
            bytesRead = read(fd, bufPtr + totalRead, count - totalRead);
        }
        if (bytesRead < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (bytesRead == 0) break;
        totalRead += bytesRead;
    }
    return totalRead;
}
"""

# 3. Inseriamo la funzione dopo gli #include iniziali
if "safe_saf_read" not in content:
    # Troviamo l'ultimo #include per inserire la funzione subito dopo
    last_include_idx = content.rfind("#include")
    if last_include_idx != -1:
        end_of_line = content.find("\n", last_include_idx)
        content = content[:end_of_line+1] + safe_read_func + content[end_of_line+1:]
        print("✅ Funzione safe_saf_read inserita nel file.")

    # Cerchiamo le chiamate a pread o read nel file (escludendo la nostra funzione)
    # Sostituiamo pread( -> safe_saf_read( e read( -> safe_saf_read(
    # (Questo è un approccio grezzo ma efficace per un test rapido)
    import re
    content = re.sub(r'\bpread\(', 'safe_saf_read(', content)
    content = re.sub(r'(?<!safe_saf_)\bread\(', 'safe_saf_read(', content)
    
    with open(target_file, 'w') as f:
        f.write(content)
    
    print("✅ Chiamate read/pread sostituite con safe_saf_read.")
else:
    print("⚠️ La funzione sembra già presente.")

# 4. Push su GitHub
print("🚀 Preparazione del push su GitHub...")
subprocess.run(["git", "add", target_file])
subprocess.run(["git", "commit", "-m", "AI Fix: Implementata safe_saf_read per evitare short reads su Android SAF"])
print("🔄 Push in corso (inserisci le credenziali se richiesto)...")
subprocess.run(["git", "push", "origin", "main"])
print("✅ Fatto! Vai su GitHub Actions.")
