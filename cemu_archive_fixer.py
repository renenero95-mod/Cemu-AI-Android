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
    raise Exception("❌ API non disponibile.")

def fix_archivi():
    log_path = os.path.expanduser("~/storage/downloads/log.txt")
    if not os.path.exists(log_path): log_path = "crash.log"
    
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    print("🕵️‍♂️ Analisi mirata: File I/O e Threading (WUA Loader)...")
    
    # Cerchiamo i file che gestiscono il formato WUA e il FileSystem (FS) di Cemu
    print("🔍 Ricerca dei file di gestione archivi WUA in Cemu...")
    search_cmd = "grep -rln --include='*.cpp' --include='*.h' -i 'wua' Cemu/src/Cafe/OS/ | head -n 5"
    res = subprocess.run(search_cmd, shell=True, capture_output=True, text=True)
    files = res.stdout.strip().split('\n')
    
    if not files or files[0] == '':
        # Fallback: cerca i file del FileSystem (FS) o coreinit
        print("🔍 File WUA non trovati, cerco nel FileSystem (FS)...")
        search_cmd = "grep -rln --include='*.cpp' --include='*.h' 'FSOpenFile\\|FSReadFile' Cemu/src/Cafe/OS/libs/coreinit/ | head -n 5"
        res = subprocess.run(search_cmd, shell=True, capture_output=True, text=True)
        files = res.stdout.strip().split('\n')

    if not files or files[0] == '':
        print("❌ File degli archivi non trovati.")
        return
        
    # Prendiamo il file più probabile (il primo della lista)
    filepath = files[0]
    print(f"📁 File target: {filepath}")
    
    with open(filepath, 'r') as f:
        codice_completo = f.read()

    # Diamo all'AI un estratto del codice per farsi un'idea
    contesto_codice = codice_completo[:6000]

    print("\n🧠 Fase 1: L'AI analizza il problema di caricamento .wua...")
    prompt_piano = f"""
    Sei un esperto di Cemu Android. Il gioco Watch Dogs crasha con Signal 11 in ppcMem_readDataU32 (il gioco emulato legge un indirizzo non valido). 
    Il log mostra che il thread attivo era 'CDelayedArchivesOpenThread' e stava eseguendo 'InitArchiveCache'. Il gioco sta caricando un file .wua tramite l'Storage Access Framework (content://...).

    Ecco il log:
    {log_content[-2000:]}

    Ecco il codice di Cemu che gestisce gli archivi/file system:
    {contesto_codice}

    Qual è il vero problema? Perché il gioco riceve un puntatore nullo o invalido quando cerca di aprire l'archivio?
    Considera: 
    1. Il file è troppo grande e la lettura va in timeout (specialmente su Android SAF)?
    2. Il thread 'CDelayedArchivesOpenThread' crea una race condition?
    3. Manca un controllo sulla validità del file descriptor o del buffer?
    
    Scrivi un piano d'azione dettagliato per risolvere il problema in questo file: {filepath}.
    """
    piano = chiedi_a_gemini(prompt_piano, temp=0.5)
    print(f"\n📝 Piano dell'AI:\n{piano}\n")

    print("\n💻 Fase 2: Scrittura della patch...")
    prompt_codice = f"""
    Basandoti su questo piano:
    {piano}
    
    Scrivi il codice C++ corretto per il file {filepath}. 
    Aggiungi controlli di sicurezza (es. se il file non si apre, restituisci un errore pulito invece di crashare) e gestisci eventuali race condition.
    Restituisci SOLO il codice corretto della funzione da modificare, senza markdown.
    """
    proposta = chiedi_a_gemini(prompt_codice, temp=0.2).strip()
    if proposta.startswith("```"): proposta = "\n".join(proposta.split("\n")[1:])
    if proposta.endswith("```"): proposta = "\n".join(proposta.split("\n")[:-1])

    print("\n😈 Fase 3: Lo Skeptic valuta la patch...")
    prompt_skeptic = f"""
    Sei un revisore C++ severo. Valuta questa modifica per il file {filepath}:
    {proposta}
    
    Risolve il problema del crash durante il caricamento degli archivi o è un cerotto inutile?
    Rispondi 'APPROVATO' o 'BOCCIATO' con motivazione.
    """
    verdetto = chiedi_a_gemini(prompt_skeptic, temp=0.3)
    print(f"⚖️ Verdetto:\n{verdetto}\n")

    if "APPROVATO" in verdetto.upper() and "BOCCIATO" not in verdetto.upper():
        print("✅ Patch approvata. Generazione file...")
        with open("patch_archive.diff", "w") as f:
            f.write(f"--- {filepath}\n+++ {filepath}\n")
            f.write(f"# PROPOSTA AI:\n{proposta}\n")
        print("📦 File patch_archive.diff generato. Controlla il codice prima di pushare!")
    else:
        print("❌ Bocciato. L'AI deve rivedere il piano.")

if __name__ == "__main__":
    fix_archivi()
