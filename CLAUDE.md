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

- `scraper.py`: hakee tilanteen ja lisää rivin `data/queue.csv`:hen vain, jos tilanne on muuttunut. Aukioloajan ulkopuolella API:a ei kutsuta, vaan kirjataan yksi `Suljettu`-rivi. Vain standardikirjasto.
- `.github/workflows/scrape.yml`: vain `workflow_dispatch`. Ajastus tulee ulkoisesta cron-palvelusta, joka kutsuu GitHubin API:a (`POST /repos/entsukki/gr-trendi/actions/workflows/scrape.yml/dispatches`, body `{"ref":"main"}`) 5 min välein fine-grained tokenilla (Actions: write, vanhenee 31.12.2026). Commitoi `data/queue.csv`:n, jos se muuttui.

- `index.html`: yksittäinen staattinen sivu (ei build-vaihetta, ei riippuvuuksia), joka lukee `data/queue.csv`:n selaimessa. Näyttää nykytilan, lämpökartan (viikonpäivä × kellonaika), kiireisimmät ja rauhallisimmat ajat ja 3 vrk aikajanan. Julkaistavissa GitHub Pagesilla repon juuresta.

## Aukioloaika

Grillroom.fi:n etusivun mukaan avoinna **joka päivä 11–20** (Suomen aikaa; muita aikoja tai poikkeuksia ei sivustolla ole). Vakiot: `OPEN_HOUR`/`CLOSE_HOUR` sekä `scraper.py`:ssä että `index.html`:ssä. Muuta molemmat, jos ajat muuttuvat.

- Scraper: suljettuna ei API-kutsua. Ensimmäinen suljettu-ajo kirjaa rivin `closed=True, time=Suljettu`, jotta avautuessa ensimmäinen havainto kirjautuu aina uutena rivinä (CSV sisältää vain muutokset).
- Sivu: havainnot rajataan aukioloon myös lukuhetkellä, joten vanhat tai virheelliset yörivit eivät vaikuta tuloksiin. Lämpökartassa on vain tunnit 11–20. Nykytila näyttää suljettuna "Suljettu" ja avautumisajan.

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

## Konventiot

- Keskustelu käyttäjän kanssa suomeksi.
