# Guió de la Presentació — Defensa TFM

**Durada estimada:** 20 minuts  
**Autor:** Xavier Maltas Tarridas

---

## Diapositiva 1 — Portada

"Bon dia/Bona tarda. Sóc Xavier Maltas i avui us presentaré el meu Treball Final de Màster sobre l'ús de models de llenguatge per optimitzar processos documentals en entorns sanitaris."

---

## Diapositiva 2 — Índex

"Abans de començar, us faré un breu resum del que veurem avui. Primer, analitzarem el problema de la sobrecàrrega administrativa en l'àmbit sanitari i la meva motivació personal. Després, us presentaré la solució proposada i veurem l'arquitectura del sistema. Seguidament, presentarem els resultats obtinguts en tres casos d'ús clínics. També parlarem de les limitacions identificades i el treball futur. I finalment, faré una demostració pràctica del sistema en funcionament."

---

## Diapositiva 3 — El gran repte estructural: La sobrecàrrega administrativa

"Segons un estudi de Sinsky publicat a Annals of Internal Medicine, els professionals sanitaris dediquen el 49,2% del seu temps a tasques administratives, mentre que només el 27% es destina a l'atenció directa al pacient. Aquesta és la paradoxa del sistema sanitari modern: la burocràcia desplaça el pacient del centre, sent el factor principal associat a l'esgotament professional o burnout.

Aquest projecte neix d'una motivació personal: he viscut la saturació del sistema sanitari públic. Llargues esperes a urgències, professionals clarament esgotats, i la sensació que el temps dels metges es dedica més a omplir informes que a escoltar els pacients.

Aquesta realitat m'ha portat a preguntar-me: i si poguéssim alliberar aquest temps? I si la tecnologia pogués automatitzar la part més mecànica de la documentació per retornar el temps als professionals i, en definitiva, als pacients?"

---

## Diapositiva 4 — La proposta de valor: Documentació assistida

"Davant d'aquest problema, la meva proposta és un sistema de documentació assistida. I vull emfatitzar la paraula 'assistida': l'objectiu NO és substituir el criteri mèdic, sinó automatitzar la càrrega repetitiva.

Com funciona? Abans, el metge havia de redactar manualment cada informe des de zero, dedicant hores a tasques mecàniques. Ara, el sistema recupera automàticament els protocols oficials, genera un esborrany basat en aquestes fonts verificades, i el metge revisa, edita i signa el document final. És un procés 'Human-in-the-loop': la IA assisteix, però el professional manté sempre el control i l'autoritat clínica.

Això permet tres beneficis clau: reducció del temps mecànic, alineació estricta amb protocols oficials, i manteniment de l'autoritat clínica del professional."

---

## Diapositiva 5 — El triangle de confiança

"El sistema es fonamenta en tres pilars tecnològics:

Models de llenguatge. He seleccionat Llama 3.2, un model petit però eficient que funciona en CPU sense necessitat de GPU, i que ha demostrat 100% de precisió diagnòstica amb zero al·lucinacions.

Retrieval-Augmented Generation o RAG. Això significa que abans de generar cap document, el sistema recupera automàticament els protocols i guies clíniques oficials rellevants de fonts com NICE, ESC o ADA, garantint que la informació generada està fonamentada en fonts verificades.

Ontologies semàntiques mèdiques com SNOMED CT, ICD-10 i ATC, que són els estàndards internacionals per codificar diagnòstics, procediments i medicaments.

Aquests tres pilars treballen conjuntament per garantir una automatització clínica segura: el model genera el text, el RAG el fonamenta en protocols oficials, i les ontologies asseguren la precisió semàntica."

---

## Diapositiva 6 — Integració Ontològica

"I aquí està la clau de volta del sistema: la integració ontològica.

Però què és una ontologia? En termes simples, és un vocabulari controlat que defineix de forma precisa cada concepte mèdic. És com un diccionari universal on cada malaltia, procediment o medicament té un identificador únic que tothom entén de la mateixa manera, eliminant qualsevol tipus d'ambigüitats.

El sistema no només 'llegeix' el text, sinó que l''entén' clínicament. Quan un pacient presenta un 'infart agut de miocardi', el sistema mapeja aquest text a tres ontologies mèdiques internacionals:

SNOMED CT, que conté més de 350.000 conceptes clínics per a diagnòstics i procediments.
ICD-10, la classificació estandarditzada per a facturació i interoperabilitat internacional.
I ATC, per a la classificació farmacològica exacta de medicaments.

Aquesta capa ontològica és la que evita les al·lucinacions diagnòstiques i garanteix que el llenguatge humà es converteixi en dades mèdiques precises i traçables, assegurant la coherència clínica global. Sense aquesta capa, tindríem un sistema que genera text coherent però clínicament no validat."

---

## Diapositiva 7 — L’Arquitectura del Sistema: Pipeline RAG Híbrid

"L'arquitectura del sistema funciona en tres blocs principals:

Bloc 1: Ingesta. Processem protocols i guies clíniques, que són les fonts no estructurades d'informació mèdica verificada.

Bloc 2: Indexació. Generem embeddings multilingües amb el model BGE-M3 i els emmagatzemem a la base vectorial Qdrant, separant text i conceptes ontològics per millorar la precisió de la cerca.

I Bloc 3: Generació RAG. El pipeline executa 11 passos: recupera el protocol exacte que necessita, i el model de llenguatge Llama 3.2 genera l'informe de forma segura, basat només en aquestes fonts verificades."

---

## Diapositiva 8 — El Pipeline RAG: De la petició al document

"Vegem com funciona el pipeline pas a pas:

1. El metge sol·licita l'esborrany de l'informe.

2. El sistema fa una cerca semàntica a la base de dades vectorial Qdrant, recuperant els protocols i vectors històrics més rellevants al cas.

3. Punt clau: s'aplica un filtratge ontològic. Aquí és on el sistema no només llegeix, sinó que entén clínicament el text. Les ontologies SNOMED CT i ICD-10 tradueixen el llenguatge humà ambigu en dades mèdiques precises, garantint la coherència en tot el sistema i evitant al·lucinacions diagnòstiques.

4. Llama 3.2 genera el text de l'informe de forma segura, fonamentant-se en els protocols recuperats i garantint una precisió diagnòstica del 100%.

5. El sistema valida la traçabilitat documental abans d'entregar l'esborrany al metge per a la seva revisió i signatura.

Tot aquest procés triga entre 16 i 30 segons, complint l'objectiu de latència acceptable per a l'ús clínic real."

---

## Diapositiva 9 — Casos d'Ús Clínics

"He implementat i avaluat tres casos d'ús clínics reals:

Informe de derivació a especialista. L'objectiu és transferir el pacient a un especialista garantint la continuïtat assistencial, amb el motiu clínic i els antecedents rellevants.

Resum clínic previ a consulta. És una síntesi automatitzada de l'historial del pacient per facilitar la preparació del metge abans de la visita.

Informe d'alta hospitalària. L'objectiu és resumir el procés assistencial complet: diagnòstics, tractaments i recomanacions de seguiment en sortir de l'hospital."

---

## Diapositiva 10 — Metodologia d'Avaluació

"Com avaluar el sistema sense comprometre la privacitat del pacient?

A causa de l'estricta privacitat de dades reals, he creat Gold Standards Sintètics: documents de referència creats manualment basats en guies internacionals com les del NICE, l'ESC i l'AAFP.

Amb aquests gold standards, he generat 13 casos clínics complexos que cobreixen cardiologia, pneumologia, nefrologia i endocrinologia, garantint la diversitat diagnòstica.

I finalment, he aplicat mètriques automatitzades en tres categories: textuals, com BLEU i ROUGE-L per avaluar la qualitat del text; estructurals, per verificar la completesa de les seccions; i semàntiques, amb l'Ontological F1 Score per avaluar la precisió de la codificació mèdica."

---

## Diapositiva 11 — Taula de Resultats

"Els resultats mostren un rendiment heterogeni:

L'informe de derivació ha assolit un 73% d'Overall Score, amb una precisió del 100% en detectar l'especialitat i el nivell d'urgència. Aquest cas està apte per a un pilot assistit.

El resum clínic ha obtingut entre un 58 i un 71%, mostrant una bona síntesi textual, però la detecció d'interaccions farmacològiques és millorable.

I l'informe d'alta ha quedat per sota de l'objectiu del 60%, amb un 51,3%. El problema principal és la barrera lingüística: les ontologies estan dissenyades per a l'anglès, i això provoca una pèrdua de precisió semàntica durant el mapping ontològic quan treballem en català. Com a solució futura, caldria implementar capes de traducció dedicades i validació automàtica de codis per al corpus català abans de la injecció al pipeline RAG.

Dels tres casos, dos funcionen molt bé per a documents d'estructura sintètica i objectius clars. L'informe d'alta, en canvi, necessita refinament per aquesta barrera lingüística i la seva alta complexitat narrativa."

---

## Diapositiva 12 — Viabilitat Operativa

"El sistema és viable operativament en entorns de salut pública.

Primer, hardware: consumeix menys de 16 GB de RAM, amb una mitjana de 4,5 GB. Executable en CPUs estàndard d'hospital, sense necessitat de GPU dedicada.

Segon, latència d'inferència: respostes ràpides en menys de 30 segons, adaptades perfectament al flux clínic diari.

I tercer, seguretat i RGPD: desplegament on-premise estricte. Les dades clíniques mai surten de l'hospital, garantint el compliment total amb la normativa de protecció de dades sanitàries."

---

## Diapositiva 13 — Síntesi i lliçons apreses

"D'aquest projecte n'extrec tres lliçons clau:

Primera: dades són més importants que la mida del model. Un corpus estructurat amb RAG compensa l'ús d'un model gran.

Segona: latència és igual a adopció. Si el sistema tarda més que el metge en escriure-ho, fracassa.

I tercera: la frontera semàntica. Les ontologies en anglès limiten dràsticament el rendiment en català, amb F1 scores del 29 al 37 per cent."

---

## Diapositiva 14 — Treballs Futurs: Full de ruta

"El full de ruta futur té tres fases clau:

Fase 1: Refinament ontològic multilingüe. Desenvolupar embeddings clínics per català, integrar diccionaris de traducció mèdica, i millorar els F1 scores del 29% actual fins a més del 70%.

Fase 2: Validació clínica en entorn real. Pilot amb metges d'atenció primària, mesurant la reducció de temps de documentació amb casos reals, no sintètics.

I Fase 3: Expansió a processos complexos. Generació de receptes assistida amb validació ontològica automàtica i integració amb sistemes hospitalaris.

L'objectiu final és transformar l'esgotament administratiu en temps real per al pacient."

---

## Diapositiva 15 — Demostració

*(Demostració en viu del sistema)*

---

## Diapositiva 16 — Conclusions

"En conclusió, he assolit els objectius del projecte:

He desenvolupat un sistema funcional amb tres casos d'ús, on he demostrat la viabilitat tècnica amb infraestructures estàndard sense GPU, i he aconseguit que un cas d'ús sigui apte per desplegament pilot assistit Human-in-the-loop.

Sistema eficient, local i segur: desplegament 100% local complint el RGPD.

I el multilingüisme continua sent el repte de futur, amb solucions proposades d'embeddings clínics per català.

L'objectiu final: transformar l'esgotament administratiu en temps real per al pacient."

---

## Diapositiva 17 — Gràcies / Preguntes

*(Torn de preguntes del tribunal)*

---
