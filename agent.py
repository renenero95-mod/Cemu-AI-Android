import os
import sys
import subprocess
from google import genai
from google.genai import types

# La chiave API verrà inserita automaticamente dal comando successivo
API_KEY = "AQ.Ab8RN6KkWC67JCU_Mez2dptUrJy9HnJf3MK53y__wnK5S2RYQg"
client = genai.Client(api_key=API_KEY)

def pianifica_e_modifica(filepath):
    print(f"\n--- 🧠 Fase 1: Pianificazione per {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        codice_originale = f.read()

    prompt_piano = f"Sei un esperto sviluppatore C++ per Cemu (Android). Analizza questo codice e scrivi un breve piano (max 3 righe) su come ottimizzarlo per Snapdragon 8 Gen 2. Sii specifico su cosa cambiare:\n\n{codice_originale}"
    
    risposta_piano = client.models.generate_content(
        model="gemini-3.5-flash-lite", contents=prompt_piano
    )
    print(f"📝 Piano dell'AI:\n{risposta_piano.text}\n")

    print("--- 💻 Fase 2: Scrittura del Codice ---")
    prompt_codice = f"Applica il seguente piano al codice sorgente. Restituisci SOLO il codice C++ modificato, senza spiegazioni, senza markdown, senza backtick.\n\nPIANO:\n{risposta_piano.text}\n\nCODICE ORIGINALE:\n{codice_originale}"
    
    risposta_codice = client.models.generate_content(
        model="gemini-3.5-flash-lite", contents=prompt_codice
    )
    
    codice_modificato = risposta_codice.text.strip()
    if codice_modificato.startswith("```"):
        codice_modificato = "\n".join(codice_modificato.split("\n")[1:])
    if codice_modificato.endswith("```"):
        codice_modificato = "\n".join(codice_modificato.split("\n")[:-1])

    file_temp = filepath + ".temp"
    with open(file_temp, 'w', encoding='utf-8') as f:
        f.write(codice_modificato)

    print("--- 📦 Fase 3: Generazione della Patch per GitHub ---")
    try:
        with open("patch.diff", "w") as f:
            subprocess.run(["git", "diff", "--no-index", filepath, file_temp], stdout=f)
        
        os.replace(file_temp, filepath)
        print(f"✅ Fatto! File modificato e 'patch.diff' generato.")
        print("⚠️ Ricordati di inviare la patch a GitHub con: git add patch.diff && git commit -m 'AI Patch' && git push origin main")
    except Exception as e:
        print(f"❌ Errore nella creazione della patch: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agent.py <percorso_del_file>")
        sys.exit(1)
    pianifica_e_modifica(sys.argv[1])
