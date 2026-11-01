import os
import sys
from google import genai
from google.genai import types

# ATTENZIONE: Inserisci la tua API Key tra le virgolette qui sotto
API_KEY = "AQ.Ab8RN6KkWC67JCU_Mez2dptUrJy9HnJf3MK53y__wnK5S2RYQg"

client = genai.Client(api_key=API_KEY)

def modifica_file_con_ai(filepath, istruzioni):
    print("\n--- Analisi del file: " + filepath + " ---")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            codice_originale = f.read()
    except Exception as e:
        print("Errore nella lettura del file: " + str(e))
        return

    # Prepariamo il testo per Gemini in modo pulito
    prompt = "Sei un esperto sviluppatore C++ e Android.\n"
    prompt += "Ti sto fornendo il codice sorgente di un file dell'emulatore Cemu per Android.\n"
    prompt += "Il mio obiettivo e ottimizzarlo per uno smartphone con Snapdragon 8 Gen 2 e GPU Adreno 740.\n\n"
    prompt += "Istruzioni specifiche: " + istruzioni + "\n\n"
    prompt += "Ecco il codice da analizzare:\n"
    prompt += "--------------------\n"
    prompt += codice_originale + "\n"
    prompt += "--------------------\n\n"
    prompt += "Restituisci ESATTAMENTE E SOLO il codice modificato, pronto per essere compilato.\n"
    prompt += "Non aggiungere commenti discorsivi, non usare i blocchi markdown e non spiegare cosa hai fatto. Restituisci solo il testo del file aggiornato."

    print("In attesa della risposta di Gemini (potrebbe volerci qualche secondo)...")
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        
        codice_modificato = response.text.strip()
        
        # Pulizia di sicurezza se l'AI inserisce i backtick per errore
        if codice_modificato.startswith("```"):
            codice_modificato = codice_modificato[3:]
        if codice_modificato.startswith("cpp"):
            codice_modificato = codice_modificato[3:]
        if codice_modificato.endswith("```"):
            codice_modificato = codice_modificato[:-3]

        # Creiamo un backup del file originale
        backup_path = filepath + ".bak"
        os.rename(filepath, backup_path)
        
        # Salviamo il nuovo codice
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(codice_modificato.strip())
            
        print("✅ Successo! File modificato. (Backup salvato in " + backup_path + ")")

    except Exception as e:
        print("❌ Errore durante la chiamata a Gemini: " + str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agent.py <percorso_del_file>")
        sys.exit(1)
        
    percorso_file = sys.argv[1]
    istruzioni = "Ottimizza questo codice per ridurre l'uso della CPU. Cerca colli di bottiglia."
    
    modifica_file_con_ai(percorso_file, istruzioni)
