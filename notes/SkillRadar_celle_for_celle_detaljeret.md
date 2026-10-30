# SkillRadar — detaljeret celle-for-celle gennemgang af `data_inspection_primary(1).ipynb`

> **Omfang:** Alle 45 celler i den uploadede notebook: 21 Markdown-celler og 24 kodeceller. Forklaringerne tager udgangspunkt i den lagrede notebook og dens eksisterende outputs — koden er **ikke** kørt igen.

> **Projektkontekst:** [SkillRadar-repositoriet](https://github.com/Lucialululu/SkillRadar), især [matcher.py](https://github.com/Lucialululu/SkillRadar/blob/main/skillradar/matcher.py). Notebooken tester datagrundlaget for et værktøj, der sammenholder CV-kompetencer med jobmarkedets efterspørgsel.

## Hvordan læses guiden?

Hver celle indeholder (1) den faktiske kode eller Markdown, (2) en detaljeret forklaring, (3) en forklaring af alle gemte outputblokke, (4) hvorfor metoden er valgt, (5) alternative metoder samt relevante forbehold. Cellenumre tælles fra 1 og inkluderer Markdown-celler. Outputtallene er historiske observationer fra notebook-kørslen i 2024-data og er ikke live tal.

## Grundlæggende begreber

- **Posting:** én jobannonce/én række, typisk identificeret med `job_link`.
- **Skill label:** en tekststreng, som en dataleverandør har koblet til en jobannonce; ikke nødvendigvis et verificeret krav.
- **Keyword matching:** søgning efter navne/aliases i tekst.
- **O*NET:** ekstern taksonomi/vokabular til softwareværktøjer.
- **Coverage:** procent med tilgængelig tekst/skills eller mindst ét fundet værktøj; afhænger af den præcise nævner.
- **Demand:** andel jobannoncer for en rolle, hvor en skill er fundet. Dette er observeret omtale, ikke direkte økonomisk efterspørgsel.
- **Procentpoint (pp):** forskellen mellem to procentsatser (fx 24% − 20% = 4 pp).
- **Snapshot:** en stikprøve fra et begrænset tidspunkt; ikke i sig selv en lang tidsserie.

## Celle 1 — Markdown

**Celletype:** `markdown`.

### Original Markdown

# **Data inspection primary with 1.3M LinkedIn Jobs & Skills (weeks 1-4)**

### Hvad sker der i denne celle?

Angiver notebookens emne og den oprindelige ugeafgrænsning.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 2 — Markdown

**Celletype:** `markdown`.

### Original Markdown

In this notebook, we inspect the second job-posting dataset ([asaniczka/1-3m-linkedin-jobs-and-skills-2024](https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024)) the same way as `data_inspection.ipynb`. The first dataset turned out to be a single 2-week scrape (April 2024), so this one has to answer some very concrete questions:

> Time coverage, is this another single scrape, and if so, *when*? If it is from a different month than the first dataset, the two together could give us two snapshots to compare (section 1).

> Skill labels, the first dataset only had 35 broad categories. Does `job_skills.csv` here actually contain tool-level skills like Docker or SQL (section 2)?

> Volume and scope, how many postings do our target roles get, and which countries are in it (section 1, section 2)?

> Text, is `job_summary.csv` the full posting text, and does our O*NET keyword matcher agree with the dataset's own skill lists (section 3, section 4)?

> Two snapshots, can we compare January (this dataset) against April (first dataset) for the same role (section 5)?

### Hvad sker der i denne celle?

Opstiller konkrete spørgsmål: tidsdækning, labelgranularitet, rollevolumen, fuldtekst og to snapshots.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 3 — Markdown

**Celletype:** `markdown`.

### Original Markdown

NOTE:

Expected layout (see `data_repo_structue.txt`): the new files live in `data/kagglev2/`. `job_summary.csv` is several GB, so we **never** load it whole, we stream it in chunks and only keep the rows we need.

### Hvad sker der i denne celle?

Dokumenterer forventet filstruktur og begrunder chunking af den meget store summary-fil.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 4 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Imports**

### Hvad sker der i denne celle?

Visuel overskrift for biblioteksafhængigheder.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 5 — Kode

**Celletype:** `code`.

### Original kode

```python
from pathlib import Path
from collections import Counter
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

### Hvad sker der?

Importerer Path (portable filstier), Counter (optælling), re (regulære udtryk), pandas (tabeller), NumPy (numeriske beregninger), matplotlib (figurer). Importer udfører ingen analyse af data.

### Output — hvad betyder det?

**Intet lagret output.** Cellen definerer import, indstillinger eller funktioner, men udskriver ikke noget på dette tidspunkt.

### Hvorfor denne metode?

Samler afhængighederne ét sted, så efterfølgende celler kan genbruge korte navne og har ensartet beregningsmiljø.

### Hvilke alternativer havde vi?

Kun standardbiblioteket csv + collections kunne bruges, men ville gøre DataFrame-operationer og figurer mere besværlige; Polars er et hurtigt alternativ til pandas, Plotly til Matplotlib.

## Celle 6 — Markdown

**Celletype:** `markdown`.

### Original Markdown

# **Kaggle**

### Hvad sker der i denne celle?

Markerer Kaggle-delen af analysen.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 7 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Data handling**

### Hvad sker der i denne celle?

Adskiller filhåndtering fra efterfølgende datainspektion.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 8 — Kode

**Celletype:** `code`.

### Original kode

```python
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_colwidth", 80)

# definitions
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data").is_dir())
DATA = ROOT / "data"
KAGGLE, KAGGLE2, ONET = DATA / "kaggle", DATA / "kagglev2", DATA / "onet"

FILES = {
    # kaggle files (this notebook)
    "v2_postings":  KAGGLE2 / "linkedin_job_postings.csv",
    "v2_skills":    KAGGLE2 / "job_skills.csv",
    "v2_summary":   KAGGLE2 / "job_summary.csv",
    # first kaggle dataset, only for the snapshot comparison
    "postings":     KAGGLE / "postings.csv",
    # O*NET for the keyword matcher
    "software_skills": ONET / "software_skills.csv",
}
```

### Hvad sker der?

Ændrer kun pandas' visningsindstillinger. Finder projektroden ved at gå fra nuværende mappe op gennem forældremapper indtil en 'data'-mappe findes. Bygger stier til tre Kaggle-filer, en ældre Kaggle-fil og O*NET-tabellen.

### Output — hvad betyder det?

**Intet lagret output.** Cellen definerer import, indstillinger eller funktioner, men udskriver ikke noget på dette tidspunkt.

### Hvorfor denne metode?

Gør notebooken mindre afhængig af den aktuelle arbejdsmappe og holder filnavne samlet. Ingen filer indlæses her.

### Hvilke alternativer havde vi?

Brug en konfigurationsfil (TOML/YAML), miljøvariabler eller en eksplicit project root; en fast absolut sti er enkel, men mindre portabel. next(...) vil rejse StopIteration hvis data-mappen ikke findes.

## Celle 9 — Kode

**Celletype:** `code`.

### Original kode

```python
# loop
for name, path in FILES.items():
    status = f"{path.stat().st_size/1e6:7.1f} MB" if path.exists() else "  MISSING"
    print(f"{status}  {name:20s} {path.relative_to(ROOT)}")
```

### Hvad sker der?

Itererer gennem FILES; tester eksistens og læser filstørrelse fra filsystemets metadata. Omregner bytes til decimal MB med 1e6 og formaterer en linje pr. fil.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
415.3 MB  v2_postings          data/kagglev2/linkedin_job_postings.csv
  672.7 MB  v2_skills            data/kagglev2/job_skills.csv
 5102.0 MB  v2_summary           data/kagglev2/job_summary.csv
  516.8 MB  postings             data/kaggle/postings.csv
    3.6 MB  software_skills      data/onet/software_skills.csv
```

**Fortolkning:** Filerne findes alle; `job_summary.csv` er 5.102 MB (ca. 5,1 GB), hvorfor chunking er nødvendig.

### Hvorfor denne metode?

Tidlig validering af store input før dyre indlæsninger. Størrelse hjælper med at vælge chunking.

### Hvilke alternativer havde vi?

pathlib.exists/stat kan erstattes af os.path; valider med en assert og informative fejl; automatisk beregning af hukommelsesbudget; brug GiB = bytes/1024**3 for binære enheder.

## Celle 10 — Kode

**Celletype:** `code`.

### Original kode

```python
# overview func
def overview(df, name):
    # one-glance summary: shape, dtypes, missingness, uniques
    print(f"── {name}: {df.shape[0]:,} rows x {df.shape[1]} cols")
    return pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing_%": (df.isna().mean() * 100).round(1),
        "n_unique": df.nunique(),
        "example": df.iloc[0] if len(df) else None,
    })

# linkedin job id from a posting url, so we can match postings across datasets
def linkedin_id(url):
    m = re.search(r"(\d{6,})/?(?:\?.*)?$", str(url))
    return int(m.group(1)) if m else np.nan
```

### Hvad sker der?

Definerer overview(): antal rækker/kolonner, datatype, andel NaN, antal distinkte værdier og første række for hver kolonne. Definerer linkedin_id(): regex fanger mindst seks cifre i slutningen af URL før eventuel slash/query, ellers NaN.

### Output — hvad betyder det?

**Intet lagret output.** Cellen definerer import, indstillinger eller funktioner, men udskriver ikke noget på dette tidspunkt.

### Hvorfor denne metode?

Genbrugelig kvalitetskontrol og en fælles nøgle til at finde eventuelt overlap mellem datasæt.

### Hvilke alternativer havde vi?

df.info(), df.describe(include='all'), pandera eller Great Expectations; extract af LinkedIn-id med urlparse + regex. Regex kan fejle på URL-varianter: 664 id'er parses ikke, så overlapstesten kan overse jobs.

## Celle 11 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Section 1 | Kaggle second data set test `linkedin_job_postings.csv` the MAIN table**

One row per posting, keyed by `job_link` (the LinkedIn url), which is also the key in `job_skills.csv` and `job_summary.csv`. No description text in here, that lives in `job_summary.csv`. `search_city` / `search_country` / `search_position` are what the scraper *searched for*, not necessarily what the job is.

### Hvad sker der i denne celle?

Specificerer hovedtabel, join-nøgle og forskellen mellem scraperens søgefelter og en stillings faktiske karakteristika.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 12 — Kode

**Celletype:** `code`.

### Original kode

```python
v2 = pd.read_csv(FILES["v2_postings"])
overview(v2, "v2_postings")
```

### Hvad sker der?

Læser hele linkedin_job_postings.csv ind i v2 og kalder overview. pandas gætter datatyper, mens overview ser på den allerede indlæste tabel.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
── v2_postings: 1,348,454 rows x 14 cols
```

**Output 2 (`execute_result`):**

```text
dtype  missing_%  n_unique  \
job_link              str        0.0   1348454   
last_processed_time   str        0.0    722748   
got_summary           str        0.0         2   
got_ner               str        0.0         2   
is_being_worked       str        0.0         2   
job_title             str        0.0    584544   
company               str        0.0     90605   
job_location          str        0.0     29153   
first_seen            str        0.0         6   
search_city           str        0.0      1018   
search_country        str        0.0         4   
search_position       str        0.0      1993   
job_level             str        0.0         2   
job_type              str        0.0         3   

                                                                                             example  
job_link             https://www.linkedin.com/jobs/view/account-executive-dispensing-norcal-north...  
last_processed_time                                                     2024-01-21 07:12:29.00256+00  
got_summary                                                                                        t  
got_ner                                                                                            t  
is_being_worked                                                                                    f  
job_title                 Account Executive - Dispensing (NorCal/Northern Nevada) - Becton Dickinson  
company                                                                                           BD  
job_location                                                                           San Diego, CA  
first_seen                                                                                2024-01-15  
search_city                                                                                 Coronado  
search_country                                                                         United States  
search_position                                                                          Color Maker  
job_level                                                                                 Mid senior  
job_type                                                                                      Onsite
```

**Fortolkning:** 1.348.454 opslag × 14 kolonner. `job_link` har 1.348.454 unikke værdier, og `first_seen` kun seks — et første tegn på kort indsamling.

### Hvorfor denne metode?

Fastslår datamængde, skema og nøgleegenskaber før filtre og joins.

### Hvilke alternativer havde vi?

read_csv(usecols=...), dtype=..., chunksize=..., Polars scan_csv eller DuckDB for større filer; valider uniqueness via v2['job_link'].is_unique.

## Celle 13 — Kode

**Celletype:** `code`.

### Original kode

```python
# check duplicates and other basic checks
print("duplicate job_link:", v2["job_link"].duplicated().sum())
v2["linkedin_id"] = v2["job_link"].map(linkedin_id)
print("could not parse a linkedin id:", v2["linkedin_id"].isna().sum())
for col in ["got_summary", "got_ner", "is_being_worked"]:
    if col in v2:
        print(f"{col}:", v2[col].value_counts(dropna=False).to_dict())
```

### Hvad sker der?

Tæller gentagne job_link, udleder LinkedIn-id fra URL'er og optæller t/f for scraperens procesflag.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
duplicate job_link: 0
could not parse a linkedin id: 664
got_summary: {'t': 1297877, 'f': 50577}
got_ner: {'t': 1296401, 'f': 52053}
is_being_worked: {'f': 1346978, 't': 1476}
```

**Fortolkning:** 0 dublerede URL-links; 664 ikke-parsbare ID-er. De tre flags har flest `t` for got_summary/got_ner og flest `f` for is_being_worked. Procesflagene er ikke en præcisionsmåling.

### Hvorfor denne metode?

Adskiller identiske URL'er fra mulige manglende ID'er og undersøger om skill/summary-processering var fuldført.

### Hvilke alternativer havde vi?

Check for dubletter på virksomhedsnavn+titel+sted eller normaliseret LinkedIn-ID; pd.Series.str.extract til id; schema-validering og kontrol af flag på tværs.

## Celle 14 — Markdown

**Celletype:** `markdown`.

### Original Markdown

##### **Time coverage, *the* premortem check again**

`first_seen` is when the scraper first saw the posting, so it is a scrape date, not necessarily the date the employer posted it. What we want to know: how many days/weeks does it span, and does it sit at a different time than the first dataset (Mar 24 – Apr 20, 2024)?

### Hvad sker der i denne celle?

Præciserer at first_seen er observationsdato, ikke oprindelig publiceringsdato.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 15 — Kode

**Celletype:** `code`.

### Original kode

```python
v2["first_seen_dt"] = pd.to_datetime(v2["first_seen"], errors="coerce")
s = v2["first_seen_dt"]
print(f"first_seen   min={s.min()}  max={s.max()}  missing={s.isna().sum()}")

# first dataset, only the date column, for comparison
old_dates = pd.to_datetime(pd.read_csv(FILES["postings"], usecols=["listed_time"])["listed_time"], unit="ms")
print(f"postings.csv min={old_dates.min()}  max={old_dates.max()}")
```

### Hvad sker der?

Konverterer first_seen til dato med ugyldige værdier som NaT; indlæser kun listed_time fra det gamle datasæt og fortolker tallene som Unix-millisekunder. Printer min/max og missing.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
first_seen   min=2024-01-12 00:00:00  max=2024-01-17 00:00:00  missing=0
postings.csv min=2024-03-24 21:50:14  max=2024-04-20 00:26:56
```

**Fortolkning:** v2: 12.–17. januar 2024, i alt seks kalenderdage. v1: 24. marts–20. april 2024. Tidsfelterne har forskellige definitioner.

### Hvorfor denne metode?

Tid er en kritisk forudsætning for projektets trendanalyse; de to tidsfelter måler dog ikke nødvendigvis samme hændelse.

### Hvilke alternativer havde vi?

pd.read_csv(parse_dates=...), pyarrow date parsing; beregn antal forskellige observationsdage, timezone og fordelinger. Et scraped first_seen kan ikke uden videre sammenlignes med arbejdsgivers listed_time.

## Celle 16 — Markdown

**Celletype:** `markdown`.

### Original Markdown

Plot both datasets on the same timeline (bars, so empty days show up as gaps and not as fake lines).

### Hvad sker der i denne celle?

Begrunder valget af søjler frem for linjer til diskrete scrape-dage.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 17 — Kode

**Celletype:** `code`.

### Original kode

```python
fig, ax = plt.subplots(figsize=(14, 4))
for dates, label in [(v2["first_seen_dt"], "v2: first_seen"), (old_dates, "postings.csv: listed_time")]:
    per_day = dates.dt.floor("D").value_counts().sort_index()
    ax.bar(per_day.index, per_day.values, width=0.9, label=label, alpha=0.8)
ax.set_title("Postings per day, both datasets")
ax.set_ylabel("postings")
ax.legend()
plt.show()

print(v2["first_seen_dt"].dt.to_period("W").value_counts().sort_index().to_string())
```

### Hvad sker der?

Grupperer datostempler per kalenderdag gennem floor('D'), tæller opslag pr. dato og tegner søjler for hvert datasæt. Printer ugentlige antal for v2.

### Output — hvad betyder det?

**Output 1 (`display_data`):**

Den gemte notebook har en grafisk figur (Matplotlib); den rene teksteksport viser kun figurens størrelse. Figuren er et søjlediagram over jobopslag pr. dag for de to datasæt. Selve pixelgrafen er ikke gengivet i Markdown.

**Output 2 (`stream`):**

```text
first_seen_dt
2024-01-08/2024-01-14    1070289
2024-01-15/2024-01-21     278165
Freq: W-SUN
```

**Fortolkning:** 1.070.289 ses i ISO-ugen 8.–14. januar og 278.165 i ugen 15.–21. januar. Det er ca. 79,4% i den første viste uge, ikke en månedlig tidsserie.

### Hvorfor denne metode?

Synliggør, om der er kontinuerlige tidsserier eller blot korte snapshots. Søjler antyder ikke observationer på mellemliggende dage.

### Hvilke alternativer havde vi?

Seaborn histplot, resample('D').size(), Plotly eller ECDF; nul-udfyld en eksplicit datoakse hvis fraværende dage skal vises som 0. To overlappende søjleserier kan skjule hinanden.

## Celle 18 — Markdown

**Celletype:** `markdown`.

### Original Markdown

Write down here what we see.

### Hvad sker der i denne celle?

En tom skrivepåmindelse; rummer ingen faktisk fortolkning.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 19 — Kode

**Celletype:** `code`.

### Original kode

```python
# who is in the data: countries, levels, job types, what the scraper searched for
for col in ["search_country", "job_level", "job_type"]:
    if col in v2:
        display(v2[col].value_counts(dropna=False).to_frame(col))
display(v2["search_position"].value_counts().head(20))
```

### Hvad sker der?

Viser value_counts for søgeland, jobniveau og jobtype samt de 20 hyppigste søgepositioner. dropna=False medtager eventuelle mangler.

### Output — hvad betyder det?

**Output 1 (`display_data`):**

```text
search_country
search_country                
United States          1149342
United Kingdom          113421
Canada                   55972
Australia                29719
```

**Output 2 (`display_data`):**

```text
job_level
job_level            
Mid senior    1204445
Associate      144009
```

**Output 3 (`display_data`):**

```text
job_type
job_type          
Onsite     1337633
Hybrid        6562
Remote        4259
```

**Output 4 (`display_data`):**

```text
search_position
Account Executive                   19468
Christian Science Nurse             16048
Consultant Education                12138
Change Person                       12025
Circulation-Sales Representative    10978
Accountant                           9571
Chef                                 9559
Agricultural-Research Engineer       9549
Extra                                9338
Car Inspector                        9230
Dermatologist                        9031
Assembler                            8738
Bakery Supervisor                    8500
Guide                                8415
Director Social                      8319
Nurse Practitioner                   8287
Anesthesiologist                     8229
Driver                               8170
Architect                            8041
Manager Benefits                     7966
Name: count, dtype: int64
```

**Fortolkning:** USA: 1.149.342; UK: 113.421; Canada: 55.972; Australien: 29.719. Næsten alt er kategoriseret som onsite, og de fleste som mid/senior; vær opmærksom på scraperens definitioner.

### Hvorfor denne metode?

Beskriver datadækningen og mulige sample-bias, herunder land, senioritet og søgestrategi.

### Hvilke alternativer havde vi?

Normaliserede procenttabeller, crosstab, stratificering på land og jobniveau, stikprøvekontrol af search_position vs faktisk job_title. Søgemetadata er ikke sikker beskrivelse af et konkret job.

## Celle 20 — Kode

**Celletype:** `code`.

### Original kode

```python
# type of jobs that dominate the data with top titles
v2["job_title"].str.lower().value_counts().head(20)
```

### Hvad sker der?

Konverterer jobtitler til små bogstaver og tæller eksakte titelstrenge; viser top 20.

### Output — hvad betyder det?

**Output 1 (`execute_result`):**

```text
job_title
customer service representative                        9436
lead sales associate-ft                                7325
shift manager                                          5849
store manager                                          5748
assistant manager                                      5540
first year tax professional                            5356
lead sales associate-pt                                4924
registered nurse                                       4336
hourly supervisor & training                           2955
travel allied health professional - ct technologist    2933
host                                                   2924
account executive                                      2638
senior accountant                                      2562
restaurant manager                                     2346
hourly supervisor and training                         2230
veterinarian                                           2201
assistant general manager                              2078
executive assistant                                    2078
operations assistant manager                           2066
maintenance supervisor                                 1874
Name: count, dtype: int64
```

**Fortolkning:** De mest almindelige eksakte titler er ikke primært teknologijobs (fx customer service representative: 9.436). En tech-relevant filtrering er derfor nødvendig.

### Hvorfor denne metode?

Giver et groft billede af dataset-sammensætningen og viser, at det ikke kun er tech-jobs.

### Hvilke alternativer havde vi?

Fjern punctuation og titelsuffikser, fuzzy clustering, embeddings eller standardiseret occupation taxonomy. Eksakt optælling adskiller nært beslægtede titler.

## Celle 21 — Kode

**Celletype:** `code`.

### Original kode

```python
# how many postings would a student-relevant role actually give us? (same patterns as notebook 1)
ROLE_PATTERNS = {
    "data scientist":    r"data scien",
    "data analyst":      r"data analy",
    "software engineer": r"software (?:engineer|developer)",
    "ml engineer":       r"(?:machine learning|ml) engineer",
    "ux designer":       r"(?:ux|ui|user experience).*design",
}

def tag_role(titles):
    # first matching role per title, NaN if none
    role = pd.Series(np.nan, index=titles.index, dtype="object")
    for r, p in ROLE_PATTERNS.items():
        hit = role.isna() & titles.str.contains(p, case=False, regex=True, na=False)
        role[hit] = r
    return role

v2["role"] = tag_role(v2["job_title"])
pd.crosstab(v2["role"], v2["search_country"], margins=True)
```

### Hvad sker der?

Definerer regex-mønstre for fem roller og tag_role; tildeler kun den første matchende rolle pr. titel og sætter ellers NaN. Bygger krydstabel med rolle og søgeland inkl. totaler.

### Output — hvad betyder det?

**Output 1 (`execute_result`):**

```text
search_country     Australia  Canada  United Kingdom  United States    All
role                                                                      
data analyst              55     157             174           1797   2183
data scientist            20      46              90            951   1107
ml engineer               10      16               7            501    534
software engineer        179     407             721           9782  11089
ux designer               22      47              80            700    849
All                      286     673            1072          13731  15762
```

**Fortolkning:** Der identificeres 15.762 opslag på tværs af fem roller; software engineer udgør 11.089, data scientist 1.107, ML engineer 534. Tabellen viser søgeland, ikke nødvendigvis joblokation.

### Hvorfor denne metode?

Et simpelt forklarligt baseline-filter, der viser om der er nok jobs i målgrupperne til videre analyse.

### Hvilke alternativer havde vi?

ESCO/O*NET-kodning, supervised job title classifier, multilabel klassificering eller sentence embeddings; mønstre kan give false positives/negatives, og rækkefølgen af ROLE_PATTERNS bestemmer konflikter.

## Celle 22 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Section 2 | Kaggle `job_skills.csv`, finally tool-level skills?**

One row per posting, `job_skills` is a single comma-separated string. The Kaggle page says the postings were *augmented* with skills, it does not say how (probably automatic extraction, so this is **not** ground truth). Things to check: are they tool-level (Python, Docker) or soft/generic ("communication"), how messy are the spellings, and how many postings have them.

### Hvad sker der i denne celle?

Forklarer forventning om støjende automatisk genererede skill labels, som ikke bør behandles som facit.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 23 — Kode

**Celletype:** `code`.

### Original kode

```python
skills = pd.read_csv(FILES["v2_skills"])
display(overview(skills, "v2_skills"))
print("postings with a skill list:", f"{v2['job_link'].isin(skills['job_link']).mean():.1%}")
print("skill rows without a posting:", (~skills["job_link"].isin(v2["job_link"])).sum())

skills["skill_list"] = skills["job_skills"].fillna("").str.split(r",\s*").map(
    lambda xs: [x.strip().lower() for x in xs if x.strip()])
skills["n_skills"] = skills["skill_list"].map(len)
skills["n_skills"].describe().round(1)
```

### Hvad sker der?

Indlæser separat skill-tabel, kontrollerer nøglematch, splitter komma-separerede skills, trimmer mellemrum, lowercaser hvert label og tæller skills pr. opslag.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
── v2_skills: 1,296,381 rows x 2 cols
```

**Output 2 (`display_data`):**

```text
dtype  missing_%  n_unique  \
job_link     str        0.0   1296381   
job_skills   str        0.2   1287101   

                                                                                    example  
job_link    https://www.linkedin.com/jobs/view/housekeeper-i-pt-at-jacksonville-state-un...  
job_skills  Building Custodial Services, Cleaning, Janitorial Services, Materials Handli...
```

**Output 3 (`stream`):**

```text
postings with a skill list: 96.1%
skill rows without a posting: 0
```

**Output 4 (`execute_result`):**

```text
count    1296381.0
mean          20.8
std           11.7
min            0.0
25%           13.0
50%           19.0
75%           25.0
max          463.0
Name: n_skills, dtype: float64
```

**Fortolkning:** 1.296.381 skill-rækker; 96,1% af v2-links findes i skills. Medianen er 19 labels og gennemsnittet 20,8. Maksimum 463 giver anledning til datakvalitetskontrol.

### Hvorfor denne metode?

Tester om der er brugbare værktøjslabels og hvor stor dækningen er før de bruges til match eller benchmark.

### Hvilke alternativer havde vi?

Brug et robust CSV-skema/parsing, valider skills via stikprøvekontrol, normaliser med aliases og kanoniske IDs; behold originale labels parallelt, da lowercasing kan ændre betydning og kan give konflikter med case-sensitive aliasmatch.

## Celle 24 — Kode

**Celletype:** `code`.

### Original kode

```python
# all skills in one Counter (faster and lighter than exploding 1M+ rows)
skill_counts = Counter(sk for lst in skills["skill_list"] for sk in lst)
print(f"distinct skill strings: {len(skill_counts):,}")
print(f"used only once: {sum(1 for c in skill_counts.values() if c == 1):,}")
pd.Series(dict(skill_counts.most_common(40)), name="n_postings")
```

### Hvad sker der?

Flader skill-lister logisk ud i en generator til Counter. Tæller antallet af unikke strenge og frekvensen af hver streng, og viser top 40.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
distinct skill strings: 2,773,202
used only once: 1,951,214
```

**Output 2 (`execute_result`):**

```text
communication             370143
customer service          278102
teamwork                  227609
communication skills      195949
leadership                185187
problem solving           149032
time management           142911
attention to detail       133975
problemsolving            129329
project management        121563
interpersonal skills      100267
patient care               99926
sales                      93031
nursing                    88015
collaboration              87116
training                   83656
data analysis              81964
microsoft office suite     75531
organizational skills      75274
inventory management       71911
high school diploma        67267
scheduling                 64461
bachelor's degree          63490
multitasking               62044
analytical skills          60768
microsoft office           60604
adaptability               59121
flexibility                56896
critical thinking          53081
documentation              51875
organization               47045
safety                     45908
budgeting                  45401
troubleshooting            44508
excel                      41498
problemsolving skills      41468
written communication      41235
conflict resolution        40955
supervision                39138
coaching                   38473
Name: n_postings, dtype: int64
```

**Fortolkning:** 2.773.202 forskellige skill-strenge, hvoraf 1.951.214 kun ses én gang. Populære brede labels som communication og teamwork dominerer på tværs af alle brancher.

### Hvorfor denne metode?

Måler vokabularstøj uden at oprette en meget stor explode-tabel.

### Hvilke alternativer havde vi?

explode().value_counts() er kortere, men kan kræve mere hukommelse; streaming Counter og approximate sketches er bedre ved meget store data. Counter her tæller forekomster, ikke nødvendigvis unikke job pr. skill.

## Celle 25 — Kode

**Celletype:** `code`.

### Original kode

```python
# how messy is it? all spellings that contain a few tools we care about
for word in ["python", "sql", "docker", "aws", "power bi"]:
    variants = {k: v for k, v in skill_counts.items() if word in k}
    top = sorted(variants.items(), key=lambda kv: -kv[1])[:8]
    print(f"{word:9s} {len(variants):5,} variants · top: {top}")
```

### Hvad sker der?

For hvert af fem søgeord filtreres alle labels ved delstrengsmatch, og otte hyppigste vises.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
python    1,580 variants · top: [('python', 25168), ('python scripting', 244), ('python programming', 232), ('python (programming language)', 82), ('python3', 64), ('scripting languages (powershell go python)', 46), ('programming languages: c/c++ java javascript python', 40), ('5+ years of experience in java scala python go or node.js', 37)]
sql       2,981 variants · top: [('sql', 22035), ('nosql', 3237), ('sql server', 2825), ('mysql', 2331), ('postgresql', 1614), ('nosql databases', 1009), ('pl/sql', 877), ('microsoft sql server', 799)]
docker      271 variants · top: [('docker', 6254), ('docker containers', 76), ('docker swarm', 33), ('dockers', 21), ('containerization technologies (docker kubernetes)', 17), ('dockerization', 17), ('containerization (docker kubernetes)', 14), ('container orchestration (docker kubernetes)', 12)]
aws       8,292 variants · top: [('aws', 12738), ('labor laws', 1394), ('tax laws', 1228), ('laws', 679), ('aws certified solutions architect', 547), ('employment laws', 545), ('fair housing laws', 487), ('state laws', 443)]
power bi    469 variants · top: [('power bi', 5429), ('microsoft power bi', 423), ('ms power bi', 68), ('power bi dashboards', 22), ('power bi service', 16), ('power bi desktop', 14), ('power bi reporting', 10), ('power bi development', 9)]
```

**Fortolkning:** De 8.292 strenge med delstrengen `aws` inkluderer fx `laws` og `labor laws`. Det er et demonstrationseksempel på hvor galt naiv substring matching kan gå.

### Hvorfor denne metode?

Synliggør hvor mange forskellige varianter og kontekststrenge der gemmer sig bag enkelte teknologinavne.

### Hvilke alternativer havde vi?

Ordgrænser/regex, aliasdictionary, tokeniseret søgning, manuel annotering eller semantisk mapping. Delstreng 'aws' matcher også 'laws', 'SQL' indgår i 'NoSQL': de viste varianttal er IKKE antal gyldige synonymer.

## Celle 26 — Markdown

**Celletype:** `markdown`.

### Original Markdown

This is the output we actually want for the tool, the share of postings per skill *for one role*:

### Hvad sker der i denne celle?

Definerer det praktiske mål: procent af stillingsopslag i en bestemt rolle, der kræver en skill.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 27 — Kode

**Celletype:** `code`.

### Original kode

```python
role_skills = v2[["job_link", "role", "search_country"]].merge(skills[["job_link", "skill_list"]], on="job_link")

def skill_share(df, role, top=25):
    sub = df[df["role"] == role]
    counts = Counter(sk for lst in sub["skill_list"] for sk in set(lst))
    return (pd.Series(counts) / len(sub) * 100).sort_values(ascending=False).head(top).round(1).rename(
        f"% of {len(sub):,} '{role}' postings")

skill_share(role_skills, "data scientist")
```

### Hvad sker der?

Inner join knytter skill-lister til v2 med job_link. For valgt rolle bruges set(lst) for at tælle hver skill højst én gang pr. posting. Dividerer antallet af postings med skill med antallet af rolle-postings med skill-række og viser top 25 i procent.

### Output — hvad betyder det?

**Output 1 (`execute_result`):**

```text
python                         78.8
machine learning               70.2
data science                   68.5
sql                            55.8
r                              46.1
data visualization             36.8
statistics                     34.9
data analysis                  30.5
communication                  25.5
data mining                    21.4
spark                          21.0
tableau                        21.0
computer science               18.2
aws                            17.4
artificial intelligence        17.1
data analytics                 15.9
tensorflow                     15.8
statistical analysis           14.7
mathematics                    14.5
deep learning                  14.4
hadoop                         14.2
pytorch                        13.8
collaboration                  13.0
natural language processing    12.8
statistical modeling           12.7
Name: % of 1,027 'data scientist' postings, dtype: float64
```

**Fortolkning:** For de 1.027 data-scientist-opslag med tilknyttede skill-lister har 78,8% label `python`, 70,2% `machine learning` og 55,8% `sql`. Det er ikke procent af samtlige 1.107 DS-opslag.

### Hvorfor denne metode?

Dette nærmer sig projektets centrale demand-mål: hvor stor en andel af relevante opslag nævner en given skill.

### Hvilke alternativer havde vi?

groupby+explode+nunique eller binær job×skill-matrix; vægtning efter land/senioritet; denominator kan være alle relevante job i stedet for kun matchende skill-rækker. Kanonisering af synonymer bør ske før procentberegning.

## Celle 28 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Section 3 | `job_summary.csv` the text**

The biggest file. We stream it in chunks: count rows and text lengths for everything, but only keep the full text for postings in our target roles (that is what sections 4 and 5 need).

### Hvad sker der i denne celle?

Begrunder at læse store tekster i bidder og kun beholde relevante roller.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 29 — Kode

**Celletype:** `code`.

### Original kode

```python
role_links = set(v2.loc[v2["role"].notna(), "job_link"])
all_links = set(v2["job_link"])
n_rows, n_matched, lengths, kept, random_pool = 0, 0, [], [], []

# loop over chunks
for i, chunk in enumerate(pd.read_csv(FILES["v2_summary"], chunksize=100_000)):
    n_rows += len(chunk)
    n_matched += chunk["job_link"].isin(all_links).sum()
    lengths.append(chunk["job_summary"].str.len().to_numpy())
    kept.append(chunk[chunk["job_link"].isin(role_links)])                   # full text, target roles
    random_pool.append(chunk.sample(min(300, len(chunk)), random_state=i))   # random text, ALL roles

lengths = np.concatenate(lengths)
summaries = pd.concat(kept, ignore_index=True)
random_summaries = pd.concat(random_pool, ignore_index=True)
print(f"summary rows: {n_rows:,} · match a posting: {n_matched:,} ({n_matched / len(v2):.1%} of postings have text)")
print(f"kept for target roles: {len(summaries):,} · random sample of all roles: {len(random_summaries):,}")
pd.Series(lengths).describe().round(0)
```

### Hvad sker der?

Konstruerer sets med alle joblinks og links for udvalgte roller. Læser 5,1 GB tekstfil i chunks af 100.000, optæller rows/nøglematch, lagrer tekstlængder, gemmer kun relevante fuldtekster og op til 300 tilfældige rækker pr. chunk; samler til sidst.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
summary rows: 1,297,332 · match a posting: 1,297,332 (96.2% of postings have text)
kept for target roles: 15,113 · random sample of all roles: 3,900
```

**Output 2 (`execute_result`):**

```text
count    1297332.0
mean        3819.0
std         2303.0
min           21.0
25%         2211.0
50%         3382.0
75%         4927.0
max        23748.0
dtype: float64
```

**Fortolkning:** 1.297.332 tekst-rækker matcher v2-links: 96,2% af alle v2-opslag. Der beholdes 15.113 beskrivelser for målroller og 3.900 samplede beskrivelser. Median tekstlængde 3.382 tegn.

### Hvorfor denne metode?

Undgår at holde alle store beskrivelser i RAM og bevarer tilstrækkelige data til matcher-test.

### Hvilke alternativer havde vi?

DuckDB SQL JOIN direkte på CSV, Polars lazy scan, reservoir sampling, Parquet efter præfiltrering. 300 pr. chunk er ikke en uniform stikprøve hvis sidste chunk har anden størrelse; de gemte længde-arrays bruger stadig hukommelse.

## Celle 30 — Kode

**Celletype:** `code`.

### Original kode

```python
# is it the full posting or a short summary? read one
print(summaries["job_summary"].iloc[0][:1500])
```

### Hvad sker der?

Printer de første 1.500 tegn fra første målrolle-tekst og søger visuelt tegn på fuld jobbeskrivelse, fx 'Job Description' og ansvarsområder.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
Company Description
Jobs for Humanity is partnering with Capital One to build an inclusive and just employment ecosystem. Therefore, we prioritize individuals coming from the following communities: Refugee, Neurodivergent, Single Parent, Blind or Low Vision, Deaf or Hard of Hearing, Black, Hispanic, Asian, Military Veterans, the Elderly, the LGBTQ, and Justice Impacted individuals. This position is open to candidates who reside in and have the legal right to work in the country where the job is located.
Company Name: Capital One
Job Description
Locations: VA - McLean, United States of America, McLean, Virginia
Lead Machine Learning Engineer
Lead Machine Learning Engineer
As a Capital One Machine Learning Engineer (MLE), you'll be part of an Agile team dedicated to productionizing machine learning applications and systems at scale. You’ll participate in the detailed technical design, development, and implementation of machine learning applications using existing and emerging technology platforms. You’ll focus on machine learning architectural design, develop and review model and application code, and ensure high availability and performance of our machine learning applications. You'll have the opportunity to continuously learn and apply the latest innovations and best practices in machine learning engineering.
What you’ll do in the role:
The MLE role overlaps with many disciplines, such as Ops, Modeling, and Data Engineering. In this role, you'll be expected to perform many ML
```

**Fortolkning:** Eksemplet indeholder overskrifter og opgaver fra en Lead ML Engineer-stilling og ligner en fuld annonce. Konklusionen gælder dette eksempel, ikke automatisk alle poster.

### Hvorfor denne metode?

En praktisk sanity check på om feltet er fuldtekst frem for kort resume.

### Hvilke alternativer havde vi?

Se tilfældige og stratificerede eksempler, automatisk sektiongenkendelse og længdefordeling. Én jobtekst kan ikke dokumentere hele datasættets kvalitet.

## Celle 31 — Markdown

**Celletype:** `markdown`.

### Original Markdown

# **O*NET**

### Hvad sker der i denne celle?

Markerer overgang til O*NET og matching.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 32 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Section 4 | O*NET keyword matcher vs the dataset's own skills**

Same matcher as in `data_inspection.ipynb` (hot / in-demand O*NET tools only). We run it twice on the same postings:

1. on the **text** (`job_summary`), this is our own pipeline
2. on the dataset's **skill list** (`job_skills`), this maps their messy skill strings onto the same O*NET names

If both give roughly the same % per tool, that is a good sign for both. Where they disagree, one of them is missing things, worth looking at.

### Hvad sker der i denne celle?

Sætter forsøget op med to metoder på samme job: fuldtekst og metadata-labels.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 33 — Kode

**Celletype:** `code`.

### Original kode

```python
software = pd.read_csv(FILES["software_skills"])
popularity = software["Workplace Example"].value_counts()
```

### Hvad sker der?

Indlæser O*NET software_skills.csv og tæller frekvensen af Workplace Example. Popularity er her oprettet, men bruges ikke senere i denne notebook.

### Output — hvad betyder det?

**Intet lagret output.** Cellen definerer import, indstillinger eller funktioner, men udskriver ikke noget på dette tidspunkt.

### Hvorfor denne metode?

Klargør et kontrolleret værktøjsvokabular til fælles udtræk fra tekst og labels.

### Hvilke alternativer havde vi?

Brug ESCO, en kombineret kurateret liste eller alias-katalog fra annoterede jobs. Frekvensen i O*NET-filen er ikke et mål for aktuel LinkedIn-efterspørgsel.

## Celle 34 — Kode

**Celletype:** `code`.

### Original kode

```python
from skillradar.matcher import KeywordMatcher

m = KeywordMatcher(software)          # same vocabulary, aliases and MANUAL_DROP as the app
print(m)
print("aliases firing in >10% of all postings (review, real skill or English word?):")
print(m.suggest_drops(random_summaries["job_summary"].dropna()))

extract_tools = m.extract_tools       # keeps the name, so later cells work unchanged
```

### Hvad sker der?

Importerer projektets KeywordMatcher og instantierer med O*NET-softwaretabellen. Udskriver antal værktøjer/aliases/drops, tjekker aliases der matcher >10% af random-sample-tekster og laver extract_tools som genvej til instansmetoden.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
KeywordMatcher(301 tools, 450 aliases, 0 dropped)
aliases firing in >10% of all postings (review, real skill or English word?):
Empty DataFrame
Columns: [tool, share]
Index: []
```

**Fortolkning:** Matcher rapporterer 301 værktøjer, 450 aliases, 0 droppede. Ingen alias matcher >10% af samplet. Det er kun en heuristisk outlier-kontrol.

### Hvorfor denne metode?

Genbruger samme matchinglogik som produktet, så analyse og app ikke divergerer. Automatisk flag af meget hyppige aliases er en kvalitetskontrol, ikke en selvstændig accuracy-test.

### Hvilke alternativer havde vi?

spaCy PhraseMatcher, FlashText, Aho–Corasick eller embeddings/NER; evaluér mod manuelt mærkede positive/negative eksempler. Intet flag ved 10% garanterer ikke fravær af falske positiver.

## Celle 35 — Markdown

**Celletype:** `markdown`.

### Original Markdown

NOTE: the safety net only *prints* aliases that fire in more than 10% of all postings. Look at them: a real skill (Excel) stays, a plain English word goes into `MANUAL_DROP` and we rerun the cell.

### Hvad sker der i denne celle?

Foreslår manuel gennemgang af meget hyppige aliases; advarselsgrænsen er en heuristik.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 36 — Kode

**Celletype:** `code`.

### Original kode

```python
# run the matcher on text and on the dataset's skill list, for the same postings
both = summaries.merge(role_skills[["job_link", "role", "search_country", "skill_list"]], on="job_link", how="left")
both["tools_text"]  = both["job_summary"].map(extract_tools)
both = both.merge(skills[["job_link", "job_skills"]], on="job_link", how="left")
both["tools_label"] = both["job_skills"].map(lambda s: m.extract_tools_from_labels(s.split(",")) if isinstance(s, str) else set())

print(f"≥1 tool from text:  {(both['tools_text'].map(len) > 0).mean():.1%}")
print(f"≥1 tool from label: {(both['tools_label'].map(len) > 0).mean():.1%}")
```

### Hvad sker der?

Left join målgruppetekst med metadata/skilllister; kører matcher på beskrivelser og på datasetets komma-splittede labels. Beregner andel rows med mindst én fundet tool for hver kilde.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
≥1 tool from text:  90.5%
≥1 tool from label: 90.8%
```

**Fortolkning:** 90,5% af målrolle-opslagene gav mindst ét værktøj fra teksten, mens 90,8% gav mindst ét fra labels. Disse procentsatser kan være næsten ens, selv om de konkrete værktøjer er forskellige.

### Hvorfor denne metode?

Sammenligner to uafhængige repræsentationer af de samme opslag og tester om vores matcher finder praktisk brugbare signaler.

### Hvilke alternativer havde vi?

Beregn Jaccard, precision/recall med manuelt benchmark, confusion matrices og per-værktøj uenigheder. Næsten identisk coverage på aggregatniveau betyder ikke, at præcis de samme skills findes i hvert job.

## Celle 37 — Kode

**Celletype:** `code`.

### Original kode

```python
def tool_share(df, col, role):
    sub = df[df["role"] == role]
    return pd.Series(Counter(t for s in sub[col] for t in s), dtype=float) / max(len(sub), 1) * 100

ROLE = "data scientist"
compare = pd.DataFrame({
    "% from text":  tool_share(both, "tools_text", ROLE),
    "% from label": tool_share(both, "tools_label", ROLE),
}).fillna(0).round(1)
compare["diff"] = (compare["% from text"] - compare["% from label"]).round(1)
compare.sort_values("% from text", ascending=False).head(25)
```

### Hvad sker der?

Definerer tool_share, der for hver rolle optæller matchede værktøjer i hver jobs set/liste, dividerer med antallet af jobs og ganger med 100. Samler procent fra tekst og labels, udfylder manglende med 0, beregner forskel i procentpoint og sorterer efter tekstforekomst.

### Output — hvad betyder det?

**Output 1 (`execute_result`):**

```text
% from text  % from label  diff
Python                                   79.0          81.1  -2.1
Structured query language SQL            55.1          57.6  -2.5
R                                        49.7          49.5   0.2
Amazon Web Services AWS software         24.5          23.2   1.3
Apache Spark                             21.2          24.2  -3.0
Tableau                                  21.0          21.9  -0.9
TensorFlow                               16.6          16.4   0.2
Oracle Java                              13.4          13.5  -0.1
PyTorch                                  13.3          14.2  -0.9
Apache Hadoop                            11.1          15.6  -4.5
Scala                                     9.9           9.2   0.7
Google                                    9.0           5.9   3.1
SAS                                       8.7           9.1  -0.4
Scikit-learn                              8.2           9.6  -1.4
pandas                                    7.9           7.4   0.5
C++                                       7.2           7.3  -0.1
Microsoft Power BI                        6.8          12.8  -6.0
Apache Hive                               6.7           7.5  -0.8
NumPy                                     6.7           6.4   0.3
Git                                       6.4           7.2  -0.8
The MathWorks MATLAB                      6.3           6.3   0.0
PySpark                                   4.8           4.4   0.4
NoSQL                                     4.7           6.7  -2.0
Microsoft Excel                           4.6           3.9   0.7
Docker                                    4.6           5.1  -0.5
```

**Fortolkning:** For DS ligger Python på 79,0% fra tekst og 81,1% fra labels (−2,1 pp). Power BI er 6,8% vs 12,8% (−6,0 pp), Google 9,0% vs 5,9% (+3,1 pp). Særligt generiske aliaser bør manuelt inspiceres.

### Hvorfor denne metode?

En let forståelig ablation-/kilde-sammenligning per værktøj med en fælles O*NET-navneliste.

### Hvilke alternativer havde vi?

Brug parret per-job sammenligning, bootstrap-konfidensintervaller, manuelt golden set, McNemar test på binære par eller Cohen kappa. Forskelle i marginalsandsynlighed er ikke målt ground-truth fejl.

## Celle 38 — Markdown

**Celletype:** `markdown`.

### Original Markdown

> **Things to note:** big positive `diff` = our text matcher finds the tool but the dataset's labels miss it (or our matcher has a false positive, check a posting!). Big negative `diff` = the labels have it but the text does not say it literally, that is where synonym matching (weeks 6-8) could help.

### Hvad sker der i denne celle?

Forklarer fortegnet på tekst-minus-label og risikoen for både manglende labels og falske teksthits.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 39 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Section 5 | Two snapshots? January vs April (`postings.csv`)**

If section 1 shows the two datasets were scraped at different times, this is the cheapest possible trend: the same role, the same matcher, two points in time. We use US postings only (the first dataset is US) and drop postings that appear in **both** datasets (same LinkedIn id).

> Big caveat for the report: two different scrapers with different search strategies. A difference can be the scraper, not the market. So we treat this as a *first test* of a trend definition, not as a finding yet.

### Hvad sker der i denne celle?

Kvalificerer to snapshots som en svag baseline, fordi scraperne har forskellig udvælgelse.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 40 — Kode

**Celletype:** `code`.

### Original kode

```python
old = pd.read_csv(FILES["postings"], usecols=["job_id", "title", "description", "listed_time"])
old["role"] = tag_role(old["title"])
old = old[old["role"].notna()].copy()

# overlap between the datasets (same linkedin posting)
overlap = set(old["job_id"]) & set(v2["linkedin_id"].dropna().astype(int))
print(f"postings in both datasets: {len(overlap):,}")

new = both[both["search_country"].eq("United States")].copy()
new = new[~new["job_link"].map(linkedin_id).isin(overlap)]
old = old[~old["job_id"].isin(overlap)]
old["tools_text"] = old["description"].map(extract_tools)

print(pd.DataFrame({"jan (v2, US)": new["role"].value_counts(), "apr (postings.csv)": old["role"].value_counts()}))
```

### Hvad sker der?

Læser kun nødvendige felter i v1, klassificerer titler med samme tag_role, fjerner andre roller, kontrollerer overlap på LinkedIn-id og vælger amerikanske v2-job. Finder O*NET-værktøjer i v1-beskrivelser og viser rollestørrelser.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
postings in both datasets: 0
                   jan (v2, US)  apr (postings.csv)
role                                               
software engineer          9356                1573
data analyst               1752                 463
data scientist              884                 351
ux designer                 689                 161
ml engineer                 457                  99
```

**Fortolkning:** Ingen overlappende parsede LinkedIn-ID-er. Januar/April for US: software engineer 9.356/1.573, data scientist 884/351, ML engineer 457/99. Forskellige sample-størrelser og scrapers giver betydelig usikkerhed.

### Hvorfor denne metode?

Forsøger at gøre januar/april-sammenligningen mere rimelig ved fælles geografi, ens titelklassifikation og samme matcher.

### Hvilke alternativer havde vi?

Match også på senioritet, branche, lokation og firma (propensity/reweighting); brug et enkelt longitudinalt datasæt eller reelt gentagne scrapes for stærkere trendbevis. 0 overlap er ikke garanti når ID-parse fejler.

## Celle 41 — Kode

**Celletype:** `code`.

### Original kode

```python
# share per tool in jan vs apr + a two-proportion z-test as a first testable "trend" definition
def snapshot_compare(role, top=20):
    a, b = new[new["role"] == role], old[old["role"] == role]
    pa, pb = tool_share(a, "tools_text", role) / 100, tool_share(b, "tools_text", role) / 100
    df = pd.DataFrame({"jan_%": pa, "apr_%": pb}).fillna(0).astype(float)
    p = (df["jan_%"] * len(a) + df["apr_%"] * len(b)) / (len(a) + len(b))
    se = np.sqrt(p * (1 - p) * (1 / len(a) + 1 / len(b)))
    df["change_pp"] = (df["apr_%"] - df["jan_%"]) * 100
    df["z"] = (df["apr_%"] - df["jan_%"]) / se.replace(0, np.nan)
    df["signal"] = np.where(df["z"] > 1.96, "↑", np.where(df["z"] < -1.96, "↓", "–"))
    df[["jan_%", "apr_%"]] *= 100
    print(f"{role}: n_jan={len(a):,}  n_apr={len(b):,}")
    return df.sort_values("apr_%", ascending=False).head(top).round(1)

snapshot_compare("data scientist")
```

### Hvad sker der?

Definerer snapshot_compare: job-andel pr. værktøj i januar og april; pooled proportion p, standardfejl for to andele, z-score og symbol ved |z|>1.96. Ændring i procentpoint; top 20 sorteret efter aprilandel. Kaldes for data scientist.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
data scientist: n_jan=884  n_apr=351
```

**Output 2 (`execute_result`):**

```text
jan_%  apr_%  change_pp    z signal
Python                             79.6   79.8        0.1  0.1      –
Structured query language SQL      57.6   55.3       -2.3 -0.7      –
R                                  51.4   50.7       -0.6 -0.2      –
Amazon Web Services AWS software   25.1   23.6       -1.5 -0.5      –
Apache Spark                       21.7   17.7       -4.1 -1.6      –
Tableau                            22.4   16.0       -6.4 -2.5      ↓
SAS                                 9.2   15.1        5.9  3.0      ↑
Scala                              10.5   14.0        3.4  1.7      –
PyTorch                            13.3   13.4        0.0  0.0      –
TensorFlow                         16.3   11.1       -5.2 -2.3      ↓
Google                              9.3   10.3        1.0  0.5      –
Apache Hadoop                      11.5    9.1       -2.4 -1.2      –
Docker                              4.1    7.7        3.6  2.6      ↑
Oracle Java                        14.5    7.7       -6.8 -3.2      ↓
Microsoft Excel                     4.9    7.4        2.5  1.8      –
Scikit-learn                        8.0    6.6       -1.5 -0.9      –
pandas                              8.1    6.6       -1.6 -0.9      –
Microsoft Power BI                  7.0    6.3       -0.7 -0.5      –
NoSQL                               5.2    5.7        0.5  0.3      –
C++                                 7.4    5.7       -1.7 -1.0      –
```

**Fortolkning:** DS-sample: n=884 vs 351. Blandt de viste top-20 markerer z-test Tableau, TensorFlow og Java ned samt SAS og Docker op. Det er ukorrigerede tests med mulig samplingbias, ikke en dokumenteret markedsudvikling.

### Hvorfor denne metode?

Gør ordet 'trend' operationelt og testbart med en gennemskuelig statistisk baseline.

### Hvilke alternativer havde vi?

Konfidensintervaller, Fisher exact ved små tal, bootstrap, logistisk regression med kontrollvariable og korrektion for multiple tests (Benjamini-Hochberg). Z-test forudsætter sammenlignelige/uafhængige stikprøver; dette er ikke opfyldt sikkert af to scrapers.

## Celle 42 — Kode

**Celletype:** `code`.

### Original kode

```python
snapshot_compare("software engineer")
```

### Hvad sker der?

Kalder præcis samme snapshot_compare for rollen software engineer og viser sammenligningen af januar/april.

### Output — hvad betyder det?

**Output 1 (`stream`):**

```text
software engineer: n_jan=9,356  n_apr=1,573
```

**Output 2 (`execute_result`):**

```text
jan_%  apr_%  change_pp    z signal
Oracle Java                        45.5   40.4       -5.2 -3.8      ↓
Python                             43.9   38.9       -5.0 -3.7      ↓
Structured query language SQL      32.9   32.7       -0.2 -0.1      –
JavaScript                         27.8   29.8        2.0  1.7      –
Amazon Web Services AWS software   38.5   27.7      -10.9 -8.3      ↓
C++                                27.3   25.1       -2.2 -1.8      –
C#                                 13.0   19.4        6.4  6.8      ↑
Docker                             24.3   17.2       -7.1 -6.2      ↓
Kubernetes                         24.1   17.2       -7.0 -6.1      ↓
Hypertext markup language HTML     15.3   16.5        1.1  1.1      –
React                              14.1   15.1        1.0  1.0      –
TypeScript                         16.4   14.4       -2.0 -2.0      ↓
Git                                13.1   14.2        1.0  1.1      –
Linux                              20.8   12.7       -8.1 -7.5      ↓
NoSQL                              17.9   12.7       -5.3 -5.1      ↓
C                                  17.7   12.3       -5.4 -5.3      ↓
Cascading style sheets CSS         14.6   11.6       -3.1 -3.2      ↓
Go                                 20.8   10.8      -10.0 -9.3      ↓
Google Angular                     12.0   10.2       -1.8 -2.1      ↓
Google                             14.9    9.9       -5.0 -5.3      ↓
```

**Fortolkning:** SE-sample: n=9.356 vs 1.573. Mange tools falder samtidigt (fx AWS 38,5%→27,7%, Docker 24,3%→17,2%); det kan afspejle forskellige scraper/populationsmix, ikke nødvendigvis en ægte trend.

### Hvorfor denne metode?

Tester om mønstret generaliserer til en større jobgruppe og kan afsløre systematiske scraperforskelle.

### Hvilke alternativer havde vi?

Kør på alle fem roller og brug ens sampling/stratificering; visualisér effektstørrelser med interval og sammenlign retning på tværs af roller.

## Celle 43 — Markdown

**Celletype:** `markdown`.

### Original Markdown

> **Things to note:** how many tools get an ↑/↓ at all? If almost everything is "–", three months is too short to see much (also a finding). If *everything* moves in the same direction, that smells like a scraper difference, not a trend.

### Hvad sker der i denne celle?

Opfordrer til at læse brede retningsskift som mulig måle-/samplingartefakt.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 44 — Markdown

**Celletype:** `markdown`.

### Original Markdown

### **Findings towards decisions**

### Hvad sker der i denne celle?

Overskrift for afsluttende beslutningstabel.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Celle 45 — Markdown

**Celletype:** `markdown`.

### Original Markdown

| Question | Finding | Decision / next step |
|---|---|---|
| When was v2 scraped, how many days? | Jan 12–17 2024, 6 days, 79% in the first week | Single snapshot, like dataset 1 |
| Different time from `postings.csv`? (two snapshots possible?) | Yes, about 3 months apart, with 0 overlapping postings | Technically two snapshots, but confounded by different scrapers and level mix. Use for a stability test, not trend claims |
| Postings per target role (US / all countries) | SE 9,782 / 11,089 · DA 1,797 / 2,183 · DS 951 / 1,107 · UX 700 / 849 · ML 501 / 534 | Primary dataset. US-only for comparisons with dataset 1 |
| `job_skills.csv` tool-level? how messy? | Yes: ~21 skills per posting, 96% coverage, DS top skills Python 79%, ML 70%, SQL 56%. Very messy: 2.77M variants, hyphens stripped | Use as benchmark and synonym source, not as ground truth |
| `job_summary.csv` full text? | Yes, full postings, 96% coverage, same length profile as dataset 1 | Run our matcher on this text as the main pipeline |
| Text matcher vs dataset labels agree? | Yes, within ~3 points for most DS tools (Python, SQL, AWS, Tableau, TensorFlow, PyTorch, Java). The big gaps (R, Spark, Scala, scikit-learn, Excel = 0% from labels) are **our bug**, not real disagreement: we lowercased the labels, so case-sensitive aliases like "R" never match, and the dataset writes "scikitlearn" | Fix the label-side matching (below), rerun, then report agreement |
| Jan vs Apr: how many tools with a significant change? | DS: 5 of 20, mixed directions (≈ noise). SE: 14 of 20, 13 of them down (≈ sample difference) | No trend claims. Reframe Goal 2: O*NET flags + stability test |
| Which dataset(s) do we build on? | v2 is larger with validated skills; v1 replicates the results and has entry-level postings | v2 primary, v1 for replication and entry level. Check v2's license |

### Hvad sker der i denne celle?

Opsummerer beslutninger om datasæt, O*NET, sammenligning og begrænsninger; indeholder også en konkret historisk note om en label-matching-fejl, som skal holdes adskilt fra de viste nyere tal.

### Output

**Ingen beregnet output.** Markdown vises blot som formateret forklaring, overskrift, note eller tabel.

### Hvorfor er den med?

Den dokumenterer antagelser, formål eller konklusioner, så senere kode og output ikke bliver læst uden sammenhæng.

### Alternative måder

Dette kunne også være et kommentarfelt i Python-kode, en separat README, et dokumentationsafsnit eller en kort tabel med metodiske forbehold. Markdown inde i notebooken ligger tættest på det konkrete eksperiment.

## Særligt vigtige metodiske faldgruber

1. **Ikke en egentlig tidsserie.** Januar v2 er kun seks observationsdage, mens april v1 bruger et andet tidsfelt og en anden scraper. Undgå at skrive, at markedsefterspørgslen *er* steget/faldet på dette grundlag.
2. **Et skill i teksten er ikke nødvendigvis et krav.** Et ord kan stå i virksomhedsbeskrivelsen, som eksempel, som negation eller i en irrelevant kontekst. Vurdér precision/recall med manuelt mærkede opslag.
3. **Kaggle-labels er ikke facit.** De kan være maskinelt udledt og indeholde fejl; overensstemmelse mellem metoder kan ikke alene validere korrektheden.
4. **Eksakte andele kræver konsekvent nævner.** `skill_share` bruger kun job med skill-liste; andre dele bruger kun job med tekst; sammenlign derfor ikke procenter uden at angive population.
5. **Taksonomi-normalisering kan gå galt.** SQL, NoSQL og SQL Server er beslægtede, men ikke altid udskiftelige; `aws` er ikke det samme som delstrengen i `laws`. Case-sensitive aliases og transformationer skal testes systematisk.
6. **Multiple testing.** Grænsen ±1,96 svarer til en omtrentlig 5%-test for ét værktøj; når mange værktøjer testes, opstår falske signaler oftere.
7. **Markdown-konklusioner kan være forældede.** Celle 45 omtaler en tidligere bug med 0% label-matches, mens celle 37 i denne gemte kørsel faktisk viser positive label-anddele. Behandl celle 37 som de viste resultater og ret celle 45 før rapportering.
8. **Rolleklassifikation på titel er en baseline.** Man kan overse title-varianter og inkludere falske matches; evaluer på annoteret udvalg.

## Konkrete spørgsmål I kan blive stillet til projektpræsentationen

**Hvorfor tæller vi `set(lst)`?** Fordi demand er procent af opslag, hvor en skill nævnes mindst én gang, ikke det samlede antal gentagelser.

**Hvorfor bruger vi `job_link`?** Det er den fælles join-nøgle mellem metadata, skill-lister og beskrivelser.

**Hvorfor ikke indlæse alle 5,1 GB?** Fordi en CSV kan fylde langt mere i RAM end på disk, især som Python-strengobjekter.

**Hvad viser 90,5% vs 90,8%?** Andelen af opslag, hvor de to kilder giver mindst ét værktøj — ikke match-accuracy.

**Hvad betyder z=2,6 ved Docker?** Under standardtestens forudsætninger er den observerede forskel relativt stor i forhold til standardfejlen; det beviser ikke en kausal eller tidslig markedsændring.

**Hvad er næste fornuftige validering?** Et stratificeret manuelt evalueringssæt, ens population mellem sammenligninger, precision/recall for værktøjsudtræk og usikkerhedsintervaller.

## Relevante kilder

- [Projektets GitHub-repository](https://github.com/Lucialululu/SkillRadar)
- [Projektets keyword matcher](https://github.com/Lucialululu/SkillRadar/blob/main/skillradar/matcher.py)
- [Kaggle: 1.3M LinkedIn Jobs & Skills 2024](https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024)
- [O*NET Resource Center](https://www.onetcenter.org/)
- [pandas dokumentation](https://pandas.pydata.org/docs/)
- [SciPy statistikdocumentation](https://docs.scipy.org/doc/scipy/reference/stats.html)
