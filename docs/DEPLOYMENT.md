# NOEMA — გამოქვეყნების პროცედურა

## რა არის უკვე მომზადებული?

- სტატიკური საიტი: `index.html` და `assets/styles.css`.
- Pages deployment workflow: `.github/workflows/deploy.yml`.
- Workflow იღებს საიტის HTML/CSS-ს, კვლევების JSON ინდექსს და მხოლოდ `research/published/` დირექტორიაში მოთავსებულ კვლევებს.
- `research/drafts/` არ კოპირდება საჯარო Pages არტეფაქტში.
- `workflow_dispatch` ჩართულია ხელით გაშვებისათვის.

## ერთჯერადი GitHub პარამეტრი

1. გახსენით [NOEMA repository Settings → Pages](https://github.com/maisuradzee/bibmom/settings/pages).
2. განყოფილებაში **Build and deployment** ველში **Source** აირჩიეთ **GitHub Actions**.
3. შეინახეთ პარამეტრი, თუ GitHub ცალკე შენახვას ითხოვს.

GitHub Pages-ის ოფიციალური წესით, custom Actions workflow-ის გამოყენებამდე საცავში Pages წყაროდ უნდა იყოს არჩეული **GitHub Actions**.

## პირველი გაშვება

1. გახსენით [Actions → Deploy NOEMA website](https://github.com/maisuradzee/bibmom/actions/workflows/deploy.yml).
2. აირჩიეთ **Run workflow** და Branch: `main`.
3. დაელოდეთ ორივე ეტაპის წარმატებულ დასრულებას: Build/Upload და Deploy.
4. Pages-ის პარამეტრებში შეამოწმეთ გამოქვეყნებული URL და გახსენით საიტი.

## გამოქვეყნების სარედაქციო წესი

კვლევა საჯარო საიტზე მხოლოდ მაშინ გამოჩნდება, როცა:
- მისი სტატუსი `published` გახდება;
- შესაბამისი Markdown ფაილი მოთავსდება `research/published/` დირექტორიაში;
- მისი metadata დაემატება `data/research.json`-ში;
- CI ვალიდაცია წარმატებით დასრულდება.

ყველა ახალი კვლევა თავდაპირველად ინახება `research/drafts/`-ში. GitHub repository public-ია, ამიტომ დრაფტები საჯაროდ წაკითხვადია GitHub-ზე, თუმცა არ შედის Pages-ის გამოქვეყნებულ საიტში.

## შეზღუდვა

NOEMA-ს ამჟამინდელი ინსტრუმენტული კავშირი ფაილებისა და commit-ების მართვას იძლევა, მაგრამ GitHub Pages-ის Source პარამეტრის შეცვლის ან Actions-ის ხელით გაშვების უფლებამოსილი ოპერაცია ამ სამუშაო პროცესში ხელმისაწვდომი არ არის. ამ ერთჯერად პარამეტრს საცავის მფლობელი ასრულებს.
