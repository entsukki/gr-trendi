# Grillroom

Seuraa Grill Room Hankasalmen (grillroom.fi) keittiön jonotilannetta. Python-skripti hakee tilanteen GitHub Actionsilla 5 minuutin välein ja tallentaa muutokset CSV:hen.

## Miten data löytyy

grillroom.fi on Wix-sivu. Etusivun "Keittiön jonotustilanne" on iframe (`https://grillroom.sami-c0d.workers.dev/queue`), joka hakee JSONin osoitteesta `/api/status`:

```json
{"closed":false,"available":true,"status":{"time":"25–45 min","label":"🟡 Keltainen","color":"yellow","hint":"muutama pöytä vapaana"},"updatedAt":"..."}
```

Skripti lukee tämän endpointin suoraan (ei HTML-scrapetusta). Endpoint on dokumentoimaton, joten rakenne voi muuttua. Jos skripti alkaa kaatua, tarkista ensin endpoint ja iframen osoite etusivulta.

Widgetissä on myös henkilökunnan ylläpitonäkymä. Sitä ei käytetä eikä siihen kosketa.

## Tiedostot

- `scraper.py`: hakee tilanteen ja lisää rivin `data/queue.csv`:hen vain, jos tilanne on muuttunut. Vain standardikirjasto.
- `.github/workflows/scrape.yml`: vain `workflow_dispatch`. Ajastus tulee ulkoisesta cron-palvelusta, joka kutsuu GitHubin API:a (`POST /repos/entsukki/gr-trendi/actions/workflows/scrape.yml/dispatches`, body `{"ref":"main"}`) 5 min välein fine-grained tokenilla (Actions: write, vanhenee 31.12.2026). Commitoi `data/queue.csv`:n, jos se muuttui.

- `index.html`: yksittäinen staattinen sivu (ei build-vaihetta, ei riippuvuuksia), joka lukee `data/queue.csv`:n selaimessa. Näyttää nykytilan, lämpökartan (viikonpäivä × kellonaika), kiireisimmät ja rauhallisimmat ajat ja 3 vrk aikajanan. Julkaistavissa GitHub Pagesilla repon juuresta.

## Sivun laskentalogiikka

- CSV sisältää vain muutokset, joten sivu rakentaa siitä 5 min välein otetut havainnot (viimeisin tila pätee seuraavaan muutokseen asti, enintään 6 h).
- Arvo on `time`-kentän lukujen keskiarvo minuutteina (`25–45 min` → 35). Jos lukuja ei löydy, käytetään värin mukaista arviota (`COLOR_FALLBACK`).
- Suljettu (`closed`) ja ei saatavilla (`available`) jätetään pois. Viikonpäivä ja tunti lasketaan Suomen ajassa.
- Solu lasketaan vasta, kun siitä on vähintään 6 havaintoa (`MIN_SAMPLES`, ~30 min).

## Komennot

```bash
python3 scraper.py
python3 -m http.server 8000   # sivun esikatselu: http://localhost:8000
```

Sivu ei toimi avattuna suoraan levyltä (`file://`), koska se hakee CSV:n `fetch`illä.

macOS:n python.org-Pythonilla voi tulla `CERTIFICATE_VERIFY_FAILED`. Korjaus paikallisesti: `export SSL_CERT_FILE=/etc/ssl/cert.pem`. Älä poista varmenteen tarkistusta koodista.

## Huomioita

- Jos data lakkaa kertymästä, tarkista ensin cron-palvelun ajot ja tokenin voimassaolo (vanhenee 31.12.2026, API palauttaa silloin 401).
- Sivusto on auki joka päivä 11–20. Suljettuna `closed` on true.

## Konventiot

- Keskustelu käyttäjän kanssa suomeksi.
