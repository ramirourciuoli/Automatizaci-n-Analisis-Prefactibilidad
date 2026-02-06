from playwright.sync_api import sync_playwright

URL = "https://ciudad3d.buenosaires.gob.ar/"
ADDRESS = "Dávila 1172, CABA"

def find_search_input(page):
    # Estrategias comunes (probamos varias)
    candidates = [
        'input[placeholder*="Buscar" i]',
        'input[placeholder*="Dirección" i]',
        'input[type="search"]',
        'input[type="text"]',
        '[role="search"] input',
    ]
    for sel in candidates:
        loc = page.locator(sel).first
        if loc.count() > 0:
            try:
                if loc.is_visible():
                    return loc
            except:
                pass
    return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    search = find_search_input(page)
    if not search:
        print("No encontré el buscador automáticamente. Vamos a necesitar el selector exacto.")
        browser.close()
        raise SystemExit(1)

    search.click()
    search.fill(ADDRESS)
    page.keyboard.press("Enter")
    page.wait_for_timeout(5000)

    print("Listo: envié la dirección. Ahora deberías ver el mapa moverse.")
    page.wait_for_timeout(15000)
    browser.close()
