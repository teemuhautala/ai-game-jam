# Pelikehityksen tilanneraportti

Päivitetty: 2026-11-20

## Nykyinen peliversio (toiminnassa)
- Ylhäältä kuvattu jatkuvasti rullaava tieajopeli [main.py](C:/Users/LocalUser/ai-game-jam/main.py)-tiedostossa.
- Aloitusvalikko:
  - Ajoneuvon valinta: moottoripyörä, ralliauto, bussi.
  - Maan/kentän valinta: Argentiina (kaupunkikenttä), Suomi (metsäkenttä), Ruotsi (vesimaisemakenttä), Englanti (rantakenttä).
- Perusohjaus:
  - Nuolet/WASD ohjaus ja nopeuden säätö.
  - SPACE-hyppy.
  - R reset.
- Rata:
  - Kaksi rinnakkaista tietä (vasen + oikea).
  - Välillä yhdistyskohdat, joissa voi vaihtaa tietä.
  - Välillä suoria turvaosuuksia ilman esteitä.
- Esteet:
  - Karhut, laatikot, kaatuneet puut, pienet puut.
  - Tien levyisiä puuesteitä, joiden yli on käytännössä hypättävä.
- Vastustaja:
  - Tietokoneohjattu vastustaja ajaa mukana ja reagoi esteisiin.
- Tausta:
  - Maisema vaihtuu valitun maan mukaan.
  - Suomen kentässä puut ja discovalot.
- Pistemekanismi:
  - Ennätyslista (Top 5) näkyy ruudulla.
  - Ennätykset tallentuvat [highscores.json](C:/Users/LocalUser/ai-game-jam/highscores.json)-tiedostoon paikallisesti.

## Julkaisuturvallisuus
- [highscores.json](C:/Users/LocalUser/ai-game-jam/highscores.json) poistettu git-trackingistä ja lisätty ignoreen, jotta paikallinen data ei päädy ulkoiseen repositorioon.
- Copilotin cache-/venv-tiedostoja ei versionhallita.

## Seuraavat luontevat kehitysaskeleet
- Vaikeustasot (helppo/normaali/vaikea) esteiden määrälle ja nopeudelle.
- Äänet (moottori, törmäys, hyppy) ilman ulkoisia assetteja.
- Selkeämpi “pelin loppu” -näkymä ja “uusi peli” -paluu valikkoon.
