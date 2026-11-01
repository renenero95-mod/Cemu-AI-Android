import os
import sys
import subprocess
import re
from google import genai
from google.genai import types

API_KEY = "AQ.Ab8RN6KkWC67JCU_Mez2dptUrJy9HnJf3MK53y__wnK5S2RYQg"
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.5-flash-lite"

def trova_funzione_e_file(log_path):
    print(f"🕵️‍♂️ Analisi del log: {log_path}")
    with open(log_path, 'r', encoding='utf-8') as f:
        log = f.read()
    
    match = re.search(r' 3# (.*?)\(', log)
    if not match:
        match = re.search(r' 4# (.*?)\(', log)
    
    if not match:
        print("❌ Impossibile trovare la funzione colpevole nel log.")
        return None, None

    funzione_completa = match.group(1).strip()
    nome_funzione = funzione_completa.split('(')[0].split('::')[-1].strip()
    
    print(f"🎯 Bersaglio identificato: {nome_funzione}")
    print(f"🔍 Ricerca del file nel repository...")
    
    result = subprocess.run(f"grep -rln '{nome_funzione}' Cemu/src/", shell=True, capture_output=True, text=True)
    files = result.stdout.strip().split('\n')
    
    if not files or files[0] == '':
        print(f"❌ File non trovato per {nome_funzione}.")
        return None, None
        
    filepath = files[0]
    print(f"📁 File trovato: {filepath}")
    return filepath, nome_funzione

def estrai_funzione(codice_completo, nome_funzione):
    idx = codice_completo.find(nome_funzione + "(")
    if idx == -1:
        return None
    start_body = codice_completo.find("{", idx)
    if start_body == -1:
        return None
    start_def = codice_completo.rfind(";", 0, idx) + 1
    if start_def == 0: start_def = codice_completo.rfind("}", 0, idx) + 1
    if start_def == 0: start_def = 0

    braces = 0
    end_body = -1
    for i in range(start_body, len(codice_completo)):
        if codice_completo[i] == '{':
            braces += 1
        elif codice_completo[i] == '}':
            braces -= 1
            if braces == 0:
                end_body = i
                break

    if end_body != -1:
        return codice_completo[start_def:end_body+1].strip()
    return None

def estrai_e_correggi(log_path):
    filepath, nome_funzione = trova_funzione_e_file(log_path)
    if not filepath:
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        codice_completo = f.read()
    
    funzione_originale = estrai_funzione(codice_completo, nome_funzione)
    
    if not funzione_originale:
        print(f"❌ Impossibile estrarre il corpo della funzione {nome_funzione} dal file.")
        return

    print(f"✅ Funzione isolata ({len(funzione_originale)} caratteri).")

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    max_tentativi = 3
    funzione_corretta = ""
    approvato = False
    critica_precedente = "" # <--- QUI SALVIAMO IL COMMENTO DEL REVIEWER

    for tentativo in range(1, max_tentativi + 1):
        print(f"\n--- 🛠️ Tentativo {tentativo}: Il Fixer sta elaborando... ---")
        
        prompt_fixer = f"""
        Sei un esperto C++ di emulatori.
        Il log di crash indica un 'Signal 11' in {nome_funzione}.
        Ecco il log:
        {log_content}
        
        Ecco il codice ESATTO della funzione:
        {funzione_originale}
        
        Correggi il bug. Restituisci SOLO il codice C++ della funzione corretta, senza markdown.
        """
        
        # Se c'è una critica precedente, la aggiungiamo al prompt!
        if critica_precedente:
            prompt_fixer += f"\n\nATTENZIONE: Il revisore ha bocciato il tuo tentativo precedente con questa motivazione:\n{critica_precedente}\nRisolvi ASSOLUTAMENTE questo problema."

        response_fixer = client.models.generate_content(
            model=MODEL, contents=prompt_fixer, config=types.GenerateContentConfig(temperature=0.2)
        )
        proposta = response_fixer.text.strip()
        
        if proposta.startswith("```"):
            proposta = "\n".join(proposta.split("\n")[1:])
        if proposta.endswith("```"):
            proposta = "\n".join(proposta.split("\n")[:-1])

        print("--- 🧐 Il Reviewer sta controllando la proposta... ---")
        prompt_reviewer = f"""
        Sei un revisore di codice C++ super severo.
        Il log mostra un crash in {nome_funzione}.
        Codice originale: 
        {funzione_originale}
        
        La tua AI ha proposto questa modifica:
        {proposta}
        
        Valuta se la modifica risolve DAVVERO il problema o se è una perdita di tempo.
        Se va bene, rispondi ESATTAMENTE con la parola "APPROVATO" seguito da una breve spiegazione.
        Se fa schifo, rispondi ESATTAMENTE con "BOCCIATO" seguito dal motivo e da come dovrebbe essere corretta.
        """
        
        response_reviewer = client.models.generate_content(
            model=MODEL, contents=prompt_reviewer, config=types.GenerateContentConfig(temperature=0.1)
        )
        
        verdetto = response_reviewer.text.strip()
        print(f"📝 Verdetto Reviewer:\n{verdetto}\n")

        if "APPROVATO" in verdetto.upper() and "BOCCIATO" not in verdetto.upper():
            funzione_corretta = proposta
            approvato = True
            break
        else:
            print("❌ Proposta bocciata. Riprovo...")
            critica_precedente = verdetto # Salviamo il verdetto per il prossimo giro!

    if not approvato:
        print("⚠️ Nessuna modifica ha superato il controllo del Reviewer. Annullo.")
        return

    print("--- 📦 Generazione della Patch Definitiva ---")
    codice_nuovo = codice_completo.replace(funzione_originale, funzione_corretta.strip())
    
    file_temp = filepath + ".temp"
    with open(file_temp, 'w', encoding='utf-8') as f:
        f.write(codice_nuovo)

    with open("patch.diff", "w") as f:
        subprocess.run(["git", "diff", "--no-index", filepath, file_temp], stdout=f)
    
    os.replace(file_temp, filepath)
    print("✅ Fatto! Patch generata.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agent_auto_fixer.py <file_log>")
        sys.exit(1)
    estrai_e_correggi(sys.argv[1])
