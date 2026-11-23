# NOEMA — გამოქვეყნების პროცედურა

## მიმდინარე ტექნიკური მდგომარეობა

- CI-ის ბოლო შემოწმებული გაშვება წარმატებით დასრულდა: [NOEMA quality checks](https://github.com/maisuradzee/bibmom/actions).
- Pages-ის Build/Upload ეტაპმა წარმატებით ააწყო საჯარო არტეფაქტი.
- Pages-ის Deploy ეტაპი შეჩერდა `Configure GitHub Pages` ეტაპზე: GitHub-მა დააბრუნა `Get Pages site failed — 404`, რადგან საცავში Pages ჯერ არ არის გააქტიურებული.
- Deployment workflow დროებით არის მხოლოდ ხელით გასაშვები (`workflow_dispatch`), რათა ყოველი commit-ი წარუმატებელ deployment-ს არ იწვევდეს.
- რეალური საჯარო საიტი ჯერ არ არის დადასტურებული.

## ერთჯერადი GitHub პარამეტრი

1. გახსენით [NOEMA repository Settings → Pages](https://github.com/maisuradzee/bibmom/settings/pages).
2. განყოფილებაში **Build and deployment** ველში **Source** აირჩიეთ **GitHub Actions**.
3. შეინახეთ პარამეტრი.

GitHub-ის ოფიციალური ინსტრუქცია: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

**რატომ არ ვრთავთ workflow-დან ავტომატურ enablement-ს:** `actions/configure-pages`-ის `enablement` პარამეტრი Pages საიტის შესაქმნელად მოითხოვს `GITHUB_TOKEN`-ზე უფრო ფართო უფლებების მქონე token-ს. ამ პროექტში ასეთი საიდუმლო token არ გვაქვს და მის დამატებას არ ვთხოვთ მხოლოდ ერთჯერადი პარამეტრის შესაცვლელად. ოფიციალური input-ის აღწერა: https://github.com/actions/configure-pages/blob/main/action.yml

## პირველი გაშვება

1. გახსენით [Actions → Deploy NOEMA website](https://github.com/maisuradzee/bibmom/actions/workflows/deploy.yml).
2. აირჩიეთ **Run workflow** და Branch: `main`.
3. დაელოდეთ Build, Upload და Deploy სამუშაოების წარმატებით დასრულებას.
4. Pages-ის პარამეტრებში შეამოწმეთ გამოქვეყნებული URL და გახსენით საიტი.

როცა პირველი deployment წარმატებით დასრულდება, deployment workflow-ში შეიძლება დაბრუნდეს `push` trigger, რათა დამტკიცებული ცვლილებები ავტომატურად გამოქვეყნდეს.

## საიტის build და კვლევების გვერდები

- `scripts/build_site.py` კითხულობს `data/research.json`-ს და მხოლოდ სტატუსის შესაბამის უსაფრთხო საქაღალდეებს: `preliminary` → `research/preprints/*.md`; `published` → `research/published/*.md`.
- Markdown გარდაიქმნება HTML სტატიებად `research/articles/`-ში.
- საჯარო JSON ინდექსში ჩაიწერება მხოლოდ გენერირებული HTML URL; წყარო Markdown ფაილის გზა საჯარო ინდექსში არ რჩება.
- `research/drafts/` და `research/review` მასალები Pages არტეფაქტში არ კოპირდება. `preliminary` ფაილები მხოლოდ ცალკე აშკარა სტატუსით იწარმოება HTML სტატიებად.
- CI ამოწმებს builder-ს, Markdown sanitization-ს, ტესტებსა და დრაფტების გამორიცხვას.

## გამოქვეყნების სარედაქციო წესი

კვლევა საჯარო საიტზე შეიძლება გამოჩნდეს ორ რეჟიმში:
- `preliminary`: წინასწარი ანგარიში მოთავსებულია `research/preprints/`-ში და გვერდზე ჩანს გაფრთხილება, რომ ის დამოუკიდებლად რეცენზირებული არ არის;
- `published`: სრული გამოქვეყნების საკონტროლო სია დასრულებულია და ფაილი მოთავსებულია `research/published/` დირექტორიაში;
- მისი metadata დაემატება `data/research.json`-ში, ხოლო კატალოგი და ბმულები ვალიდაციას გაივლის;
- CI ვალიდაცია წარმატებით დასრულდება.

ყველა ახალი კვლევა თავდაპირველად ინახება `research/drafts/`-ში. GitHub repository public-ია, ამიტომ დრაფტები საჯაროდ წაკითხვადია GitHub-ზე, თუმცა არ შედის Pages-ის გამოქვეყნებულ საიტში. საჯარო JSON კატალოგი არის Git-ით ვერსიაკონტროლირებადი სტატიკური მონაცემთა წყარო და არა სერვერული მონაცემთა ბაზა.

## შეზღუდვა

GitHub კავშირი კოდის, ფაილებისა და Actions შედეგების მართვას იძლევა, მაგრამ Pages Source პარამეტრის შეცვლა ან workflow-ის ხელით გაშვება ამ სამუშაო პროცესში ხელმისაწვდომი არ არის. ამ ერთჯერად Pages პარამეტრს საცავის მფლობელი ასრულებს.
