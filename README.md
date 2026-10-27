# Umframdauði í Evrópu 2020–2025 — íslenskur gagnavefur

Vefur með gagnvirku línuriti yfir öll **lönd** (ekki samtölur svæða) sem eru til staðar í Eurostat `demo_r_mwk_05` og upplýsingamynd fyrir Ísland. Sjálfgefið er að sýna fimm Norðurlönd: Ísland, Noreg, Finnland, Danmörku og Svíþjóð.

## Byrja

1. Sæktu ZIP-skrána og afþjappaðu.
2. Keyrðu `python -m pip install requests` og `python fetch_data.py` úr möppunni. Skriptan hleður niður **óbreyttri** Eurostat TSV.gz skrá á slóðinni í verkefninu og vistar í `data/demo_r_mwk_05.tsv.gz`.
3. Keyrðu `python -m http.server 8000` úr verkefnismöppunni og opnaðu `http://localhost:8000`.
4. Fyrir birtingu: hýstu `index.html` ásamt `data/demo_r_mwk_05.tsv.gz` á sama vefþjóni. Þannig þarf vefurinn **ekki** að treysta á lifandi Eurostat-API í hverri heimsókn.

**Athugið:** Eurostat API var í fyrirhuguðu viðhaldi 26. október 2026 kl. 20:00–23:55 CET samkvæmt eigin upplýsingasíðu. Ef ekki tekst að sækja skrána strax má reyna síðar eða hlaða henni niður beint með tengli á vefnum og opna handvirkt. Þetta ZIP inniheldur ekki staðfest töluleg gögn, þar sem API niðurhalið var óaðgengilegt í vinnuumhverfinu; gögnin birtast aðeins eftir að raunveruleg Eurostat-skrá hefur verið lesin.

## Reikniregla

- Eurostat dataset: `demo_r_mwk_05` (vikuleg dauðsföll eftir kyni, 5 ára aldursbili, landi).
- Filter: `freq=W`, `unit=NR`, `sex=T`.
- Mælikvarði: hlutfallsleg frávik í fjölda dauðsfalla. Þetta er eigin útreikningur **ekki** opinber mánaðarleg Eurostat-vísitala `demo_mexrt`.
- Viðmið viku `w`: meðaltal dauðsfalla í ISO-viku `w` árin 2016–2019 (fjórar athuganir þurfa að vera til).
- Árshlutfall: `100 * (Σobs_w / Σexpected_w - 1)`, `w=1..52`. Að meðaltali yfir vikur (%) er **ekki** notað.
- Sérregla fyrir 2020: vika 53 er **ekki talin með**, því árin 2016–2019 voru án ISO-viku 53; þetta er gagnsætt birt á vefsíðunni. Ár = samanburður 52 vikna, ekki endilega öll dauðsföll á almanaksári.
- Ár með færri en 52 samanburðarhæfar vikur er **ekki birt** sem fullt ár. Engin ágiskun um eyður.
- Aldurshópar: 0–14, 15–64, 65–74, 75–84, 85+ úr óskörandi undirhópum; til að telja vikuna verður full samfelld aldursþekja að vera til staðar.
- Tölurnar eru ekki aldursstaðlaðar og taka ekki beint tillit til fólksfjölgunar eða breytinga í aldurssamsetningu.
- Bráðabirgðamerkingar frá Eurostat eru skráðar en útreikningar taka gildar tölur með þeim með.

## Áreiðanleiki og endurtakanleiki

Vefsíðan les hausinn á TSV-skránni til að finna rétta röð víddanna, frekar en að gera ráð fyrir fastri röð. Hver land/línuröð byggir á raunverulegum dánartölum. Viðmið og árleg hlutföll eru reiknuð í vafranum. Forritið forðast tvítalningu með því að nota heildaraldursbil beint, sé það til, en að öðrum kosti leggja saman **aðeins** samfelld, ósamfallandi aldursbil. Skorti gögn eru tölur ekki birtar.

Línuritið býður niðurhal sem SVG og niðurhal samtölutöflu sem CSV. CSV inniheldur fjölda dauðsfalla, væntanlegan fjölda, frávik, hlutfall og vikuþekju; auðir reitir þýða að ekkert fullgilt ársgildi var reiknað.

## Frumheimild

- [Eurostat demo_r_mwk_05](https://ec.europa.eu/eurostat/databrowser/view/demo_r_mwk_05/default/table?lang=en)
- [Beinn API-hlekkur á TSV.gz](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mwk_05?format=TSV&compressed=true)
- [Eurostat lýsigögn fyrir vikulegar dánartölur](https://ec.europa.eu/eurostat/cache/metadata/en/demomwk_esms.htm)

## Fyrir blaðabirtingu

Staðfestið að ISO-vikur, fullnægjandi gögn, skráarútgáfa og valdar tölur stemmi við Eurostat í útgáfu sem verður varðveitt þegar grein birtist. Birtið frekar nákvæma lýsingu „eigin útreikningar úr Eurostat“ en að kalla þetta opinbera Eurostat-vísitölu. Ekki túlka mun milli landa sem orsakatengsl án sérstakrar rannsóknar.

### Varðveisla heimildar við birtingu

`fetch_data.py` skrifar einnig `data/provenance.json` með upprunaslóð, niðurhalstíma (UTC), skrárstærð og SHA-256 gátsummu. Geymið bæði TSV.gz skrána og provenance.json við greinina til að gera niðurstöður endurtekningarhæfar jafnvel þótt Eurostat endurskoði síðar tölurnar.

### Þróunarpróf

`tests/test_site.py` notar eingöngu tilbúnar **prófunartölur** sem eru ekki raunveruleg Eurostat-gögn. Keyrt með `python tests/test_site.py` eftir að Playwright, Chromium og Python hafa verið uppsett.
