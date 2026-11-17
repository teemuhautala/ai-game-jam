# Ohjaajan muistilista

## Ennen tapahtumaa

1. Luo eristetty VM tai erillinen vieraskäyttäjä ilman admin-oikeuksia ja pääsyä työverkon sisäisiin palveluihin. Asenna Python 3, VS Code ja haluttu agentti etukäteen.
2. Avaa projektikansio VS Codessa. Varmista, että agentti tunnistaa projektin juuren `AGENTS.md`-tiedoston. Kaikki agentit eivät noudata tätä tiedostonimeä automaattisesti; tarvittaessa kopioi sen ohjeet agentin omaan ohjetiedostoon.
3. Luo ja päivitä virtuaaliympäristö projektin juureen:
	- Unix/macOS: `./setup_venv.sh`
	- Windows: `setup_venv.bat`
4. Testaa pelin käynnistyminen virtuaaliympäristön Pythonilla:
	- Unix/macOS: `.venv/bin/python main.py`
	- Windows: `.venv\Scripts\python.exe main.py` (tai `py -3 main.py`, jos venv on aktivoitu)
5. Laita agentin komentojen automaattinen suoritus pois päältä.
6. Suojaa `AGENTS.md` ja `README.md`: `chmod 444 AGENTS.md README.md` Unixissa. Huomaa, että kirjoitusoikeus kansioon voi silti sallia tiedoston korvaamisen, joten **vain-luku ei ole turvaraja**. Tarvittaessa pidä alkuperäinen kopio VM:n ulkopuolella tai käytä erillisiä käyttöoikeuksia.
7. Tee toimivasta versiosta Git-commit tai VM-snapshot palautusta varten. Testaa yksi agenttiprompti alusta loppuun.

## Esiasennus

Riippuvuudet asennetaan projektikohtaiseen `.venv`-ympäristöön skripteillä:

- Unix/macOS: `./setup_venv.sh`
- Windows: `setup_venv.bat`

Skriptit käyttävät `requirements.txt`-tiedostoa ja asentavat `pygame-ce` oikealla versiolla. Tee tämä **ennen** kuin nuoret saapuvat. Pelin suoritus ei tarvitse verkkoyhteyttä asennuksen jälkeen.

## Windows-pikatarkistus

1. Avaa `cmd` projektikansioon.
2. Suorita `setup_venv.bat`.
3. Käynnistä peli komennolla `.venv\Scripts\python.exe main.py`.
4. Varmista, että ikkuna aukeaa ja `Esc` sulkee pelin.

## Sisällön rajaukset

- Aloita `README.md`-tiedostosta; `AGENTS.md` on agentille tarkoitettu englanninkielinen ohje.
- Anna nuorten itse keksiä promptit. Näytä esimerkkejä vasta, jos alkuun pääsy tuntuu vaikealta.
- Vaihda rooleja: suunnittelija, promptaaja, testaaja, demon pitäjä.
- Kielivalinta on hyvä lisähaaste: toteuta ensin vasta kun perusajettavuus toimii.
- Peli on tarkoituksella keskeneräinen: se ei sisällä kierroslaskuria, törmäyksiä eikä kielivalikkoa.

## Turvallisuus

`AGENTS.md` ei korvaa eristystä. Käytä eristettyä laitetta tai VM:ää, rajoita verkkoliikenne vain agentin vaatimiin palveluihin, poista agentin automaattiset terminaalikomennot käytöstä ja valvo komentoja. Älä kirjaudu laitteella yrityksen sisäisiin järjestelmiin. Jos paikallinen agentti toimii ilman verkkoa, työpaja voidaan tehdä kokonaan offline-tilassa.
