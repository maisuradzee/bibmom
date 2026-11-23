# NOEMA — გამოქვეყნების პროცედურა

## მიმდინარე ტექნიკური მდგომარეობა

- CI: [NOEMA quality checks](https://github.com/maisuradzee/bibmom/actions/workflows/ci.yml) — ბოლო შემოწმებულ commit-ზე წარმატებით დასრულდა.
- Pages deployment-ის ბოლო მცდელობა: [Deploy NOEMA website — run 33](https://github.com/maisuradzee/bibmom/actions/runs/45125973528) — ჩავარდა `Configure GitHub Pages` ეტაპზე.
- ზუსტი შეცდომა: `Get Pages site failed ... Not Found (404)`. ეს მიუთითებს, რომ GitHub Pages ჯერ არ არის შექმნილი/ჩართული ამ საცავისთვის.
- პროექტის კოდი და არტეფაქტის build მზადაა; რეალური საჯარო საიტი ჯერ არ არსებობს.

## ერთჯერადი GitHub პარამეტრი

1. გახსენით [NOEMA repository Settings → Pages](https://github.com/maisuradzee/bibmom/settings/pages).
2. განყოფილებაში **Build and deployment** ველში **Source** აირჩიეთ **GitHub Actions**.
3. შეინახეთ პარამეტრი, თუ GitHub ცალკე შენახვას ითხოვს.

GitHub-ის ოფიციალური ინსტრუქციით, custom Actions workflow-ის გამოყენებამდე საცავში Pages-ის წყაროდ უნდა იყოს არჩეული **GitHub Actions**: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

**რატომ არ ვრთავთ ავტომატურ enablement-ს:** `actions/configure-pages`-ის `enablement` პარამეტრი Pages საიტის შესაქმნელად მოითხოვს `GITHUB_TOKEN`-ზე უფრო ფართო უფლებების მქონე token-ს. NOEMA-ს workflow-ში ასეთი საიდუმლო token არ ინახება და არ გვჭირდება მისი დამატება მხოლოდ ერთჯერადი პარამეტრისთვის. იხილეთ action-ის ოფიციალური აღწერა: https://github.com/actions/configure-pages/blob/main/action.yml

## პირველი გაშვება

1. გახსენით [Actions → Deploy NOEMA website](https://github.com/maisuradzee/bibmom/actions/workflows/deploy.yml).
2. აირჩიეთ **Run workflow** და Branch: `main`.
3. დაელოდეთ **Build**, **Upload** და **Deploy** ეტაპების წარმატებით დასრულებას.
4. Pages-ის პარამეტრებში შეამოწმეთ გამოქვეყნებული URL და გახსენით საიტი.

## საიტის build და კვლევების გვერდები

- `scripts/build_site.py` კითხულობს მხოლოდ `data/research.json`-ს და მის მიერ მითითებულ `research/published/*.md` ფაილებს.
- Markdown გარდაიქმნება HTML სტატიებად `research/articles/`-ში.
- საჯარო JSON ინდექსში ჩაიწერება მხოლოდ გენერირებული HTML URL; წყარო Markdown ფაილის გზა საჯარო ინდექსში არ რჩება.
- `research/drafts/` და წყარო Markdown ფაილები Pages არტეფაქტში არ კოპირდება.
- CI ამოწმებს builder-ს, Markdown sanitization-ს, ტესტებს და დრაფტების გამორიცხვას.

## გამოქვეყნების სარედაქციო წესი

კვლევა საჯარო საიტზე მხოლოდ მაშინ გამოჩნდება, როცა:
- მისი სტატუსი `published` გახდება;
- შესაბამისი Markdown ფაილი მოთავსდება `research/published/` დირექტორიაში;
- მისი metadata დაემატება `data/research.json`-ში;
- CI ვალიდაცია წარმატებით დასრულდება.

ყველა ახალი კვლევა თავდაპირველად ინახება `research/drafts/`-ში. GitHub repository public-ია, ამიტომ დრაფტები საჯაროდ წაკითხვადია GitHub-ზე, თუმცა არ შედის Pages-ის გამოქვეყნებულ საიტში.

## შეზღუდვა

NOEMA-ს GitHub კავშირი ფაილებისა და commit-ების მართვას, ასევე Actions-ის შედეგების წაკითხვას იძლევა, მაგრამ Pages-ის Source პარამეტრის შეცვლის ან Actions-ის ხელით გაშვების უფლებამოსილი ოპერაცია ამ სამუშაო პროცესში ხელმისაწვდომი არ არის. ამ ერთჯერად პარამეტრს საცავის მფლობელი ასრულებს.
