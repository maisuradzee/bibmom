# NOEMA — დამოუკიდებელი კვლევითი პლატფორმა\n\n[![NOEMA quality checks](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml)

NOEMA აერთიანებს ცოდნის მოძიებას, წყაროების გადამოწმებას, ჰიპოთეზების ჩამოყალიბებას, კვლევების არქივირებასა და შედეგების გამოქვეყნებას.

## პრინციპები

- მტკიცებულებები, ინტერპრეტაციები და ჰიპოთეზები მკაფიოდ გამოიყოფა.
- არსებით მტკიცებებს ახლავს გადამოწმებადი წყაროები.
- კვლევის მეთოდი, შეზღუდვები და გაურკვევლობები დოკუმენტირდება.
- გამოქვეყნებამდე მასალა გადის სარედაქციო და ტექნიკურ შემოწმებას.
- ავტომატიზაცია არ ნიშნავს დაუდასტურებელი შედეგების ავტომატურ გამოქვეყნებას.

## სტრუქტურა

- `index.html` — მთავარი გვერდი.
- `assets/styles.css` და `assets/articles.css` — მთავარი გვერდისა და კვლევითი სტატიების ვიზუალური სტილები.
- `data/research.json` — საჯარო კვლევების ინდექსი.
- `data/noema-003/` — NOAA-ს ფიქსირებული მონაცემთა ამონარიდი, NASA/HadCRUT5/NOAA snapshot-ები, provenance metadata და გამეორებადი შედეგები.
- `research/drafts/` — სამუშაო ჩანაწერები; Pages არტეფაქტში არ შედის, თუმცა საჯარო GitHub საცავში იკითხება.
- `research/published/` — მხოლოდ შემოწმებული და გამოსაქვეყნებლად დამტკიცებული კვლევების გვერდები.
- `research/TEMPLATE.md` — კვლევის დოკუმენტის შაბლონი.
- `.github/workflows/ci.yml` — საბაზისო შემოწმებები.
- `scripts/build_site.py` — Markdown კვლევების უსაფრთხო HTML-გვერდებად გარდაქმნა და საჯარო არტეფაქტის აწყობა.
- `scripts/validate_drafts.py` — დრაფტების მინიმალური სარედაქციო სისრულის ავტომატური შემოწმება.
- `requirements-site.txt` — ფიქსირებული Markdown renderer ვერსია.
- `.github/workflows/deploy.yml` — საჯარო ფაილების შერჩევა და Pages deployment.

## მიმდინარე კვლევა

- [NOEMA-2026-001](research/drafts/2026-11-23-paleolithic-sign-systems.md) — პალეოლითური ნიშნები; მეთოდოლოგიური გადახედვა: [დამატება A](research/drafts/2026-11-23-methodological-reassessment.md).
- [NOEMA-2026-002](research/drafts/2026-11-23-signbase-coding-audit.md) — SignBase 2.0-ის ტექსტური კოდირების აუდიტი და საბაზისო heuristic-ის ტესტი.
- [NOEMA-2026-003](research/drafts/2026-11-23-noaa-globaltemp-trend-sensitivity.md) — NOAA GlobalTemp-ის ტენდენციის საწყისი წლის მგრძნობელობა და NASA GISTEMP/HadCRUT5-თან cross-dataset გამეორება.
- აუდიტის გამეორებადი სკრიპტი: `scripts/audit_signbase.py`; შედეგები: `data/audits/signbase-v2-audit-2026-11-23.json`.
- მოკლე მიმდევრობების ენტროპიის სიმულაცია: `scripts/short_sequence_bias_simulation.py`.
- NOEMA-003-ის NOAA ანალიზი: `scripts/analyze_noema003.py`; cross-dataset შედარება: `scripts/compare_noema003_datasets.py`; მონაცემთა snapshot-ები, metadata და შედეგები: `data/noema-003/`.

## პროექტის მდგომარეობა

იხილე [მიმდინარე სტატუსი და დადასტურებული შემოწმებები](docs/PROJECT_STATUS.md).

## კვლევის სტანდარტები

- [კვლევითი და სარედაქციო სტანდარტი](docs/RESEARCH_STANDARD.md)
- [NOEMA-002 ბრმა კოდირების პროტოკოლი](research/protocols/NOEMA-002-blind-coding-protocol.md)

## კვლევის სტატუსები

- `draft` — სამუშაო ვერსია.
- `review` — წყაროებისა და არგუმენტების გადამოწმება.
- `published` — შემოწმებული და გამოსაქვეყნებლად გამზადებული მასალა.

## გამოქვეყნების უსაფრთხო წესი

GitHub Pages-ის არტეფაქტში შედის მხოლოდ `index.html`, `assets/`, `data/research.json` და `research/published/`. `research/drafts/` არასოდეს უნდა დაკოპირდეს საჯარო არტეფაქტში. კვლევა საჯარო ინდექსში ემატება მხოლოდ სტატუსით `published`.

## ლოკალური გაშვება

გაუშვი `python -m pip install -r requirements-site.txt`, შემდეგ `python scripts/build_site.py --output _site` და `python -m http.server 8000 --directory _site`. ბრაუზერში გახსენი `http://localhost:8000`.

## გამოქვეყნება

პროექტი მომზადებულია GitHub Pages-ზე განსათავსებლად. ერთჯერადი პარამეტრი და პირველი გაშვების ნაბიჯები აღწერილია [DEPLOYMENT.md](docs/DEPLOYMENT.md). რეალური deployment მხოლოდ წარმატებული Actions გაშვების შემდეგ ჩაითვლება დასრულებულად.

## მონაცემთა ბაზა

Supabase საწყის ეტაპზე გადადებულია. კვლევების ინდექსი ამჟამად ვერსიაკონტროლირებად JSON ფაილშია. მონაცემთა ბაზა დაემატება დინამიკური ფუნქციების საჭიროებისას.
