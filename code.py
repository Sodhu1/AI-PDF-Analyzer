#test parziali con ollama

import re
import csv
import camelot
import pandas as pd
import json
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Literal, Union
import os
import ollama

class Taglie(BaseModel):
  taglia: str
  qta: int

class Prodotti(BaseModel):
  code: str
  qta: int
  taglia: Optional[List[Taglie]] = None 
  seriali: Optional[List[str]] = None

class ElencoProdotti(BaseModel):
  prodotto: list[Prodotti]

class PDFTableProcessor:

    def processor(self,pdf_path):
        self.output = ""
        self.process_pdf(pdf_path)
        return self.output

    def extract_tables(self, pdf_path):
        """Estrae le tabelle dal PDF usando Camelot in modalità lattice."""
        print(f"📄 Elaborazione del PDF: {pdf_path}")
        try:
            tables = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')
            print(f"✅ Estratte {len(tables)} tabelle", "type: ", type(tables))
            for table in tables:
                print("table:  \n")
                print(table.df, "\n")
            return tables
        except Exception as e:
            print(f"❌ Errore nell'estrazione delle tabelle: {str(e)}")
            return None


    def structure_table_data(self,table):
        """Usa Ollama per strutturare i dati della tabella in JSON."""

        prompt = (
            "Analyze the following product table and extract structured JSON data based on the schema below:\n\n"
            f"{table}\n\n"
            "Some products have multiple sizes listed directly below their entry; other products do not have size information."
            "The size can be either european (M,L,XL...) or numerical"
            "If sizes are listed under a product, include them in the taglia field with the corresponding quantity."
            "If no size information exists, set the taglia field to null."
            "If no size information exists, set the serili field to null."
            "Ensure strict adherence to the JSON schema and return valid JSON only, without any extra explanations."
        )

        response = ollama.chat(
            model = "phi4:14b",
            messages = [{"role": "user", "content": prompt}],
            format = ElencoProdotti.model_json_schema(),
            options = {"temperature": 0}
        )

        print("\n🤖 Risposta AI completa:")
        print(response)

        json_text = response['message']['content']

        parsed_json = json.loads(json_text)

        self.output = parsed_json

        return parsed_json

    def process_pdf(self, pdf_path, output_path="output.json"):
        """Processo completo: estrae, filtra e struttura le tabelle del PDF."""
        tables = self.extract_tables(pdf_path)
        if not tables:
            return False

        stringa_tabella = ""
        for table in tables:
            stringa_tabella += table.df.to_string(index=False, header=True)

        print("table: ", tables[0].df)


        print(f"\n🗂️ Tabella estratta:\n{stringa_tabella}")

        if stringa_tabella:
            restructured_result = self.structure_table_data(stringa_tabella)

            if restructured_result:
                # Stampa a video prima di salvare
                print("\n💾 Salvataggio risultati...")

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(restructured_result, f, indent=4, ensure_ascii=False)

                print(f"✅ Risultati salvati in {output_path}")

                # Stampa nuovamente i risultati
                print("\n📦 Contenuto salvato:")
                print(json.dumps(restructured_result, indent=4, ensure_ascii=False))

                return True
            else:
                print("\n❌ Impossibile strutturare i dati")
                return False
        else:
            print("\n❌ Nessuna tabella di prodotti trovata")
            return False

