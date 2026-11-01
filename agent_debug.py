import os
import sys
import subprocess
from google import genai
from google.genai import types

# La chiave API verrà inserita automaticamente dal comando successivo
API_KEY = "AQ.Ab8RN6KkWC67JCU_Mez2dptUrJy9HnJf3MK53y__wnK5S2RYQg"
client = genai.Client(api_key=API_KEY)

def analizza_errore(log_path, target_file):
    print(f"\n--- 🕵️‍♂️ Fase 1: Analisi del Crash Log ({log_path}) ---")
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
    except Exception as e:
        print(f"❌ Errore lettura log: {e}")
        return

    print(f"--- 📖 Fase 2: Lettura del codice da correggere ({target_file}) ---")
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            codice_originale = f.read()
    except Exception as e:
        print(f"❌ Errore lettura codice: {e}")
        return

    prompt = f"""
    Sei un esperto sviluppatore C++ specializzato in emulatori (Cemu).
    Il seguente log mostra un crash (Signal 11) nel file {target_file}.
    
    LOG DI ERRORE:
    {log_content}
    
    CODICE SORGENTE DA CORREGGERE:
    {codice_originale}
    
    Analizza il log, capisci esattamente dove si trova l'errore di memoria (es. null pointer, out of bounds) e applica una correzione al codice.
    Restituisci SOLO il codice C++ corretto, senza spiegazioni, senza markdown, senza backticks.
    """

    print("In attesa dell'analisi e della correzione da Gemini (potrebbe volerci un minuto)...")
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", 
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        
        codice_modificato = response.text.strip()
        if codice_modificato.startswith("```"):
            codice_modificato = "\n".join(codice_modificato.split("\n")[1:])
        if codice_modificato.endswith("```"):
            codice_modificato = "\n".join(codice_modificato.split("\n")[:-1])

        file_temp = target_file + ".temp"
        with open(file_temp, 'w', encoding='utf-8') as f:
            f.write(codice_modificato)

        print("--- 📦 Fase 3: Generazione della Patch ---")
        with open("patch.diff", "w") as f:
            subprocess.run(["git", "diff", "--no-index", target_file, file_temp], stdout=f)
        
        os.replace(file_temp, target_file)
        print(f"✅ Fatto! Patch generata per correggere il crash.")
        print("⚠️ Invia la patch a GitHub con: git add patch.diff && git commit -m 'AI Crash Fix' && git push origin main")
    except Exception as e:
        print(f"❌ Errore durante la chiamata a Gemini: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python agent_debug.py <file_log> <file_codice>")
        sys.exit(1)
    analizza_errore(sys.argv[1], sys.argv[2])
