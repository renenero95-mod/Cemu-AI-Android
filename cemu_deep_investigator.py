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
MODEL = config['model']

def chiedi_a_gemini(prompt, temp=0.1):
    for tentativo in range(3):
        try:
            return client.models.generate_content(
                model=MODEL, contents=prompt, 
                config=types.GenerateContentConfig(temperature=temp)
            ).text
        except Exception as e:
            print(f"⚠️ Server occupato/Errore. Aspetto 5s...")
            time.sleep(5)
    raise Exception("❌ Impossibile contattare l'API.")

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

def investiga_a_fondo():
    log_path = os.path.expanduser("~/storage/downloads/log.txt")
    if not os.path.exists(log_path): log_path = "crash.log"
    if not os.path.exists(log_path): return

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    print("🕵️‍♂️ FASE 1: L'Esploratore analizza l'intero Stack Trace...")
    # Estrae tutte le funzioni dallo stack trace (dalla riga 3 alla 6)
    stack_functions = []
    for i in range(3, 7):
        match = re.search(rf' {i}# (.*?)\(', log_content)
        if match:
            func = match.group(1).split('::')[-1].strip()
            if func not in stack_functions:
                stack_functions.append(func)
    
    print(f"🎯 Funzioni coinvolte: {', '.join(stack_functions)}")

    # Cerca i file per tutte le funzioni coinvolte
    file_contents = {}
    for func in stack_functions:
        res = subprocess.run(f"grep -rln '{func}' Cemu/src/", shell=True, capture_output=True, text=True)
        filepath = res.stdout.strip().split('\n')[0]
        if filepath:
            with open(filepath, 'r') as f:
                file_contents[filepath] = f.read()
            print(f"📁 Trovato file per {func}: {filepath}")

    if not file_contents:
        print("❌ Nessun file trovato.")
        return

    # Prepariamo il contesto del codice (limitato per non sforare i token)
    contesto_codice = ""
    for path, code in file_contents.items():
        # Prendiamo solo i primi 3000 caratteri di ogni file per dare un'idea
        contesto_codice += f"\n--- FILE: {path} ---\n{code[:3000]}\n"

    print("\n🧠 FASE 2: Il Visionario genera MOLTE ipotesi...")
    prompt_visionario = f"""
    Sei un team di ingegneri capo di Cemu. Il gioco Watch Dogs va in crash.
    Ecco lo stack trace: {', '.join(stack_functions)}
    Log completo: {log_content[:2000]}
    
    Ecco il codice delle funzioni coinvolte:
    {contesto_codice}
    
    NON fermarti alla prima idea. Genera almeno 5 ipotesi DIVERSE sulla causa radice del problema. 
    Considera: race condition, allineamento memoria ARM, bug nel parser .wua, problemi di thread safety, GPU/Vulkan.
    Per ogni ipotesi, spiega brevemente come la risolveresti.
    """
    ipotesi = chiedi_a_gemini(prompt_visionario, temp=0.7)
    print(f"📝 Ipotesi generate:\n{ipotesi}\n")

    print("\n💻 FASE 3: Il Fixer sceglie la migliore e scrive il codice...")
    target_file = list(file_contents.keys())[0] # Scegliamo il primo file per semplicità
    target_code = file_contents[target_file]
    target_func = stack_functions[0]
    funzione_originale = estrai_funzione(target_code, target_func)

    if not funzione_originale:
        print("❌ Impossibile estrarre la funzione dal file.")
        return

    prompt_fixer = f"""
    Basandoti sulle ipotesi:
    {ipotesi}
    
    Scrivi il codice C++ corretto per la funzione {target_func} (nel file {target_file}).
    Codice originale:
    {funzione_originale}
    
    Restituisci SOLO il codice corretto, senza markdown.
    """
    proposta = chiedi_a_gemini(prompt_fixer, temp=0.2).strip()
    if proposta.startswith("```"): proposta = "\n".join(proposta.split("\n")[1:])
    if proposta.endswith("```"): proposta = "\n".join(proposta.split("\n")[:-1])

    print("\n😈 FASE 4: Lo Skeptic (Scettico) cerca di distruggere la soluzione...")
    prompt_skeptic = f"""
    Sei un revisore di codice C++ ESTREMAMENTE SEVERO E CRITICO.
    Il tuo unico scopo è trovare bug, memory leak, o errori logici nel codice proposto.
    
    Codice originale:
    {funzione_originale}
    
    Proposta del Fixer:
    {proposta}
    
    Se trovi ANCHE UN SOLO dubbio, devi rispondere 'BOCCIATO' e spiegare perché.
    Rispondi 'APPROVATO' SOLO se il codice è perfetto, sicuro e risolve davvero il problema.
    """
    verdetto = chiedi_a_gemini(prompt_skeptic, temp=0.3)
    print(f"⚖️ Verdetto dello Skeptic:\n{verdetto}\n")

    if "APPROVATO" in verdetto.upper() and "BOCCIATO" not in verdetto.upper():
        print("✅ Lo Skeptic è stato zittito. Patch approvata!")
        codice_nuovo = target_code.replace(funzione_originale, proposta)
        file_temp = target_file + ".temp"
        with open(file_temp, 'w', encoding='utf-8') as f: f.write(codice_nuovo)
        with open("patch.diff", "w") as f:
            subprocess.run(["git", "diff", "--no-index", target_file, file_temp], stdout=f)
        os.replace(file_temp, target_file)
        print("📦 patch.diff generata.")
    else:
        print("🛑 Lo Skeptic ha bloccato la patch. L'AI deve ragionare di più.")

if __name__ == "__main__":
    investiga_a_fondo()
