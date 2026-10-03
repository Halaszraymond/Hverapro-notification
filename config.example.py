SEARCH_URL = "https://hardverapro.hu/aprok/notebook/pc/index.html"   # non-Apple laptops
MIN_PRICE_HUF = 100_000
MAX_PRICE_HUF = 150_000
MIN_RAM_GB = 16
MIN_STORAGE_GB = 512
MIN_I5_GENERATION = 12  # i7 is accepted at any generation
ALLOWED_CONDITIONS = ("új",)
LIKE_NEW_TITLE_PATTERN = r"[uú]jszer[uű]"  # sellers mark like-new listings as "használt" in the condition field
PICKUP_TOWNS = [
    "Budapest",
    "Érd", "Budaörs", "Budakeszi", "Budajenő", "Biatorbágy", "Törökbálint",
    "Diósd", "Sóskút", "Tárnok", "Páty", "Zsámbék", "Tök", "Perbál",
    "Nagykovácsi", "Telki", "Solymár", "Pilisvörösvár", "Piliscsaba", "Üröm",
    "Pomáz", "Csobánka", "Pilisborosjenő", "Szentendre", "Tahitótfalu", "Leányfalu",
    "Dunakeszi", "Göd", "Fót", "Mogyoród", "Csömör", "Kerepes", "Kistarcsa",
    "Veresegyház", "Szada", "Gödöllő", "Őrbottyán", "Vácrátót", "Vác", "Sződliget",
    "Pécel", "Isaszeg", "Gyömrő", "Maglód", "Üllő", "Ecser", "Monor", "Péceli",
    "Vecsés", "Gyál", "Dunaharaszti", "Halásztelek", "Szigetszentmiklós",
    "Szigethalom", "Taksony", "Alsónémedi", "Dunavarsány", "Ráckeve", "Soroksár",
    "Dabas", "Ócsa", "Inárcs", "Ballószög", "Kiskunlacháza", "Cegléd", "Nagykőrös",
    "Abony", "Tóalmás", "Csomád", "Tápiószele",
]
EXCLUDE_TITLE_PATTERNS = [
    r"hib[aá]s",
    r"t[oö]r[oö]tt",
    r"s[eé]r[uü]lt",
    r"bontott",
    r"alkatr[eé]sz",
    r"dokkol",
    r"docking station",
    r"t[oö]lt[oő]",
    r"tápegys[eé]g",
    r"billenty[uű]z",
    r"kijelz[oő]",
    r"ventil[aá]tor",
    r"h[oő]cs[oő]",
    r"\bakku\b",
    r"akkumul[aá]tor",
    r"keresem",
    r"felv[aá]s[aá]rl",
    r"tablet",
    r"nem m[uű]k",
    r"bios (z[aá]r|jelsz)",
]
MIN_SELLER_POSITIVE_RATING = 10  # skip sellers with fewer positive ratings (or none at all)
CHECK_INTERVAL_MINUTES = 15

# Email (SMTP) — works with any provider, not just Gmail
SMTP_HOST = "smtp.yourprovider.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@example.com"
SMTP_PASSWORD = "your-app-password-or-account-password"
EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "your-email@example.com"        # <-- put your real address here locally, never commit it
