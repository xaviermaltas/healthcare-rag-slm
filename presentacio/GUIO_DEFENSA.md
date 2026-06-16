# Guió de la Defensa — TFM

**Durada estimada:** 3-4 minuts  
**Autor:** Xavier Maltas Tarridas

---

## Diapositiva 1 — Portada

"Bon dia/Bona tarda. Sóc Xavier Maltas i avui us presentaré el meu Treball Final de Màster sobre l'ús de models de llenguatge per optimitzar processos documentals en entorns sanitaris."

---

## Diapositiva 2 — Problema i Objectiu

"El problema que adreço és la sobrecàrrega administrativa dels professionals sanitaris. Segons diferents estudis presentats, dediquen un 49,2% del seu temps a tasques documentals, mentre que només un 27% del temps a l'atenció directa al pacient.

Aquesta és la paradoxa del sistema sanitari modern que desplaça el pacient del centre i és el factor principal associat a l'esgotament professional.

L'objectiu d'aquest projecte és el de desenvolupar un sistema d'assistència a la documentació clínica que alliberi temps als professionals i el retorni als pacients."

---

## Diapositiva 3 — Metodologia

"La metodologia del sistema proposat es basa en tres components clau:

RAG: Arquitectura Retrieval-Augmented Generation que recupera protocols oficials verificats garantint que el sistema utilitzi fonts fiables. Mitjançant l'ús d'una base de dades vectorial com Qdrant amb embeddings multilingües BGE-M3 per suportar català, castellà i anglès.

Model de llenguatge Llama 3.2: Genera esborranys d'informes basant-se exclusivament en els protocols recuperats sense al·lucinacions diagnòstiques.

Ontologies mèdiques: Estàndards internacionals per codificar diagnòstics, procediments i medicaments. És un vocabulari controlat que defineix de forma precisa cada concepte mèdic. Cada malaltia, procediment o medicament té un identificador únic que tothom entén de la mateixa manera, eliminant qualsevol tipus d'ambigüitats.

Tot dins d'un paradigma Human-in-the-loop: el professional sanitari revisa i valida sempre el document final. El sistema assisteix. No substitueix.

Hem avaluat el sistema en tres casos d'ús clínics reals del sistema sanitari: informes d'alta, derivació mèdica i resums clínics."

---

## Diapositiva 4 — Resultats

"S'ha demostrat que hem desenvolupat un sistema funcional amb tres casos d'ús, amb viabilitat tècnica amb infraestructures estàndard sense GPU, latència molt baixa i desplegament 100% en local complint el RGPD.

A la vegada, s'ha aconseguit que un cas d'ús sigui apte per desplegament pilot assistit Human-in-the-loop.

Com a repte principal a futur: millora del multilingüisme, on una solució futura passa per embeddings clínics i diccionaris mèdics adaptats al català."

---

## Diapositiva 5 — Gràcies

"Moltes gràcies per la vostra atenció. Quedo a la vostra disposició per a qualsevol pregunta."

---
