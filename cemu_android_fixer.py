import os
import sys
import subprocess
import re
import time
import json
from google import genai
from google.genai import types

with open('config.json', 'r') as f:
    config = json.load(f)
client = genai.Client(api_key=config['api_key'])
MODELS = [config['model']] + config.get('fallback_models', [])

def chiedi_a_gemini(prompt, temp=0.1):
    for model_name in MODELS:
        for attempt in range(2):
            try:
                print(f"🤖 Chiamata a {model_name}...")
                return client.models.generate_content(
                    model=model_name, contents=prompt, 
                    config=types.GenerateContentConfig(temperature=temp)
                ).text
            except Exception as e:
                if "503" in str(e) or "429" in str(e):
                    print(f"  ⚠️ {model_name} occupato. Aspetto 5s...")
                    time.sleep(5)
                else:
                    break
    raise Exception("❌ API non disponibile. Riprova più tardi.")

def fix_android_io():
    log_path = os.path.expanduser("~/storage/downloads/log.txt")
    if not os.path.exists(log_path): log_path = "crash.log"
    
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    print("🕵️‍♂️ Analisi mirata: File System I/O su Android...")
    
    # Cerchiamo ESPLICITAMENTE il file che gestisce il File System (FS) di Cemu
    print("🔍 Ricerca del file coreinit_FS.cpp...")
    res = subprocess.run("find Cemu/src/ -name 'coreinit_FS.cpp'", shell=True, capture_output=True, text=True)
    filepath = res.stdout.strip().split('\n')[0]
    
    if not filepath:
        print("❌ File coreinit_FS.cpp non trovato.")
        return
        
    print(f"📁 File target: {filepath}")
    
    with open(filepath, 'r') as f:
        codice_completo = f.read()

    # Prendiamo una buona fetta del file per far vedere le funzioni di lettura
    contesto_codice = codice_completo[:8000]

    print("\n🧠 Fase 1: L'AI analizza il problema di lettura su Android...")
    prompt_piano = f"""
    Sei un esperto di Cemu Android. Il gioco Watch Dogs crasha con Signal 11 in ppcMem_readDataU32.
    L'analisi precedente ha scoperto che il problema è nel File System (SAF) di Android: le chiamate read() sui file .wua (ZSTD) fanno "Short Reads" e non riempiono il buffer, causando zeri in memoria e crash.
    
    Ecco il log:
    {log_content[-2000:]}

    Ecco il codice del File System di Cemu:
    {contesto_codice}

    Scrivi un piano d'azione per implementare un loop di lettura garantita (safe_saf_read) in questo file. 
    NON suggerire workaround da PC o conversioni di file. Dobbiamo risolverlo nel codice C++ per Android.
    """
    piano = chiedi_a_gemini(prompt_piano, temp=0.5)
    print(f"\n📝 Piano dell'AI:\n{piano}\n")

    print("\n💻 Fase 2: Scrittura della patch C++ per Android...")
    prompt_codice = f"""
    Basandoti su questo piano:
    {piano}
    
    Scrivi SOLO il codice C++ corretto per implementare la lettura sicura (safe_saf_read) nel file {filepath}.
    Restituisci la funzione completa modificata, senza markdown, senza spiegazioni, senza esempi da PC.
    """
    proposta = chiedi_a_gemini(prompt_codice, temp=0.2).strip()
    if proposta.startswith("```"): proposta = "\n".join(proposta.split("\n")[1:])
    if proposta.endswith("```"): proposta = "\n".join(proposta.split("\n")[:-1])

    print("\n😈 Fase 3: Lo Skeptic valuta la patch...")
    prompt_skeptic = f"""
    Sei un revisore C++ severo. Valuta questa modifica per il file {filepath}:
    {proposta}
    
    Risolve il problema delle "Short Reads" su Android o è un cerotto inutile?
    Rispondi 'APPROVATO' o 'BOCCIATO' con motivazione.
    """
    verdetto = chiedi_a_gemini(prompt_skeptic, temp=0.3)
    print(f"⚖️ Verdetto:\n{verdetto}\n")

    if "APPROVATO" in verdetto.upper() and "BOCCIATO" not in verdetto.upper():
        print("✅ Patch approvata. Generazione file patch...")
        # Salviamo la patch per applicarla
        with open("patch_android_io.diff", "w") as f:
            f.write(f"--- {filepath}\n+++ {filepath}\n")
            f.write(f"# PROPOSTA AI:\n{proposta}\n")
        print("📦 File patch_android_io.diff generato. Controlla il codice prima di pushare!")
    else:
        print("❌ Bocciato.")

if __name__ == "__main__":
    fix_android_io()
