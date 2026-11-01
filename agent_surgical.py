import os
import sys
import subprocess
import re
from google import genai
from google.genai import types

API_KEY = "AQ.Ab8RN6KkWC67JCU_Mez2dptUrJy9HnJf3MK53y__wnK5S2RYQg"
client = genai.Client(api_key=API_KEY)

def estrai_e_correggi(filepath, nome_funzione, log_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        codice_completo = f.read()
    
    # Regex aggiornata: ora gestisce "static", "void" e spazi extra
    pattern = re.compile(r'((?:static\s+)?void\s+' + nome_funzione + r'\(.*?\)\s*\{.*?\n\})', re.DOTALL)
    match = pattern.search(codice_completo)
    
    if not match:
        print(f"❌ Impossibile trovare la funzione {nome_funzione} nel file {filepath}.")
        return

    funzione_originale = match.group(1)
    print(f"✅ Funzione {nome_funzione} isolata ({len(funzione_originale)} caratteri).")

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    prompt = f"""
    Sei un esperto C++ di emulatori.
    Il log di crash indica un 'Signal 11' in {nome_funzione}.
    Ecco il log:
    {log_content}
    
    Ecco il codice ESATTO della funzione che ha causato il crash:
    {funzione_originale}
    
    Correggi il bug di memoria (es. indirizzo non valido). Restituisci SOLO il codice C++ della funzione corretta, senza markdown o spiegazioni.
    """

    print("In attesa della correzione chirurgica da Gemini...")
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite", 
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )
    
    funzione_corretta = response.text.strip()
    if funzione_corretta.startswith("```"):
        funzione_corretta = "\n".join(funzione_corretta.split("\n")[1:])
    if funzione_corretta.endswith("```"):
        funzione_corretta = "\n".join(funzione_corretta.split("\n")[:-1])

    codice_nuovo = codice_completo.replace(funzione_originale, funzione_corretta.strip())
    
    file_temp = filepath + ".temp"
    with open(file_temp, 'w', encoding='utf-8') as f:
        f.write(codice_nuovo)

    print("--- 📦 Generazione della Patch Chirurgica ---")
    with open("patch.diff", "w") as f:
        subprocess.run(["git", "diff", "--no-index", filepath, file_temp], stdout=f)
    
    os.replace(file_temp, filepath)
    print("✅ Fatto! Patch generata con successo per la funzione.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python agent_surgical.py <file_hpp> <nome_funzione> <log>")
        sys.exit(1)
    estrai_e_correggi(sys.argv[1], sys.argv[2], sys.argv[3])
