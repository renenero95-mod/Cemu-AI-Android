import os
import sys
import subprocess
import re
import time
import json
from google import genai
from google.genai import types

# Carica la configurazione dal file esterno
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    API_KEY = config['api_key']
    MODEL = config['model']
    FALLBACK_MODELS = config.get('fallback_models', [])
except Exception as e:
    print(f"❌ Errore nel leggere config.json: {e}")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

def chiedi_a_gemini(prompt, temp=0.1):
    # Mette il modello principale in cima alla lista da provare
    modelli_da_provare = [MODEL] + FALLBACK_MODELS
    
    for modello in modelli_da_provare:
        print(f"🤖 Provo con {modello}...")
        for tentativo in range(2):
            try:
                response = client.models.generate_content(
                    model=modello, 
                    contents=prompt, 
                    config=types.GenerateContentConfig(temperature=temp)
                )
                return response.text
            except Exception as e:
                err = str(e)
                if "503" in err or "UNAVAILABLE" in err:
                    print(f"  ⚠️ {modello} occupato. Aspetto 5 secondi...")
                    time.sleep(5)
                elif "404" in err or "NOT_FOUND" in err or "no longer available" in err:
                    print(f"  ❌ {modello} non disponibile. Passo al prossimo modello della lista.")
                    break # Esce dal ciclo dei tentativi per questo modello e passa al successivo
                else:
                    print(f"  ❌ Errore inaspettato: {err}")
                    break
    raise Exception("❌ Tutti i modelli sono occupati o non disponibili in questo momento.")

def trova_log():
    paths = [
        os.path.expanduser("~/storage/downloads/log.txt"),
        os.path.expanduser("~/storage/downloads/log (1).txt"),
        "crash.log"
    ]
    for p in paths:
        if os.path.exists(p):
            print(f"📄 Log trovato in: {p}")
            return p
    print("❌ Nessun log trovato. Salva il file in Download come 'log.txt'.")
    sys.exit(1)

def estrai_funzione(codice, nome_funzione):
    idx = codice.find(nome_funzione + "(")
    if idx == -1: return None
    start_body = codice.find("{", idx)
    if start_body == -1: return None
    start_def = codice.rfind(";", 0, idx) + 1
    if start_def == 0: start_def = codice.rfind("}", 0, idx) + 1
    if start_def == 0: start_def = 0

    braces = 0
    for i in range(start_body, len(codice)):
        if codice[i] == '{': braces += 1
        elif codice[i] == '}':
            braces -= 1
            if braces == 0:
                return codice[start_def:i+1].strip()
    return None

def elabora():
    log_path = trova_log()
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    print("🕵️‍♂️ Fase 1: Analisi del Crash...")
    match = re.search(r' 3# (.*?)\(', log_content) or re.search(r' 4# (.*?)\(', log_content)
    if not match:
        print("❌ Impossibile trovare la funzione colpevole nel log.")
        return
    nome_funzione = match.group(1).split('(')[0].split('::')[-1].strip()
    print(f"🎯 Funzione colpevole: {nome_funzione}")

    print("🔍 Fase 2: Ricerca del file nel codice sorgente...")
    res = subprocess.run(f"grep -rln '{nome_funzione}' Cemu/src/", shell=True, capture_output=True, text=True)
    filepath = res.stdout.strip().split('\n')[0]
    if not filepath:
        print(f"❌ File non trovato per {nome_funzione}.")
        return
    print(f"📁 File: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        codice_completo = f.read()
    
    funzione_originale = estrai_funzione(codice_completo, nome_funzione)
    if not funzione_originale:
        print("❌ Impossibile estrarre la funzione.")
        return

    print("\n🧠 Fase 3: Ragionamento profondo (Plan Mode)...")
    prompt_piano = f"""
    Sei un ingegnere capo di Cemu. Crash 'Signal 11' in {nome_funzione}.
    Log: {log_content}
    Codice: {funzione_originale}
    Spiega perché va in crash (allineamento, null ptr, ecc.) e scrivi un piano d'azione dettagliato.
    """
    piano = chiedi_a_gemini(prompt_piano, temp=0.4)
    print(f"\n📝 Piano dell'AI:\n{piano}\n")

    print("💻 Fase 4: Scrittura del codice...")
    prompt_codice = f"Basandoti su questo piano:\n{piano}\nScrivi SOLO il codice C++ corretto della funzione. Niente markdown."
    proposta = chiedi_a_gemini(prompt_codice, temp=0.1).strip()
    
    if proposta.startswith("```"): proposta = "\n".join(proposta.split("\n")[1:])
    if proposta.endswith("```"): proposta = "\n".join(proposta.split("\n")[:-1])

    print("\n🧐 Fase 5: Revisione (Reviewer)...")
    prompt_rev = f"Codice originale:\n{funzione_originale}\nProposta:\n{proposta}\nLa modifica risolve il problema? Rispondi 'APPROVATO' o 'BOCCIATO' con una spiegazione tecnica."
    verdetto = chiedi_a_gemini(prompt_rev, temp=0.1)
    print(f"\n📝 Verdetto:\n{verdetto}\n")

    if "APPROVATO" in verdetto.upper() and "BOCCIATO" not in verdetto.upper():
        print("✅ Patch approvata. Generazione e Push su GitHub...")
        codice_nuovo = codice_completo.replace(funzione_originale, proposta)
        file_temp = filepath + ".temp"
        with open(file_temp, 'w', encoding='utf-8') as f: f.write(codice_nuovo)
        with open("patch.diff", "w") as f:
            subprocess.run(["git", "diff", "--no-index", filepath, file_temp], stdout=f)
        os.replace(file_temp, filepath)

        subprocess.run(["git", "add", "patch.diff"])
        subprocess.run(["git", "commit", "-m", f"AI Auto-Fix: {nome_funzione}"])
        subprocess.run(["git", "push", "origin", "main"])
        print("🚀 Fatto! Vai su GitHub Actions per vedere la build.")
    else:
        print("❌ Bocciato. L'AI deve migliorare la sua proposta.")

if __name__ == "__main__":
    elabora()
