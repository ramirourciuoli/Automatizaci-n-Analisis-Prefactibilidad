import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

URL = "https://ciudad3d.buenosaires.gob.ar/"
SEARCH_INPUT = "#usig-autocomplete-input"
OUT_DIR = Path("salida_json")


def close_legal_modal_if_present(page, timeout_ms=12000):
    dialog = page.locator("div[role='dialog']").first

    try:
        dialog.wait_for(state="visible", timeout=timeout_ms)
    except PWTimeoutError:
        return False

    # Intento 1: ESC
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        if not dialog.is_visible():
            return True
    except:
        pass

    # Intento 2: algún botón de cierre dentro del diálogo
    candidates = [
        "div[role='dialog'] button[aria-label*='cerrar' i]",
        "div[role='dialog'] button[aria-label*='close' i]",
        "button[aria-label*='cerrar' i]",
        "button[aria-label*='close' i]",
        "div[role='dialog'] button",
    ]
    for sel in candidates:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible():
                btn.click()
                page.wait_for_timeout(500)
                if not dialog.is_visible():
                    return True
        except:
            pass

    # Intento 3: click arriba a la derecha del diálogo (zona típica de la X)
    try:
        box = dialog.bounding_box()
        if box:
            page.mouse.click(box["x"] + box["width"] - 15, box["y"] + 15)
            page.wait_for_timeout(500)
            if not dialog.is_visible():
                return True
    except:
        pass

    return False


def is_json_response(resp) -> bool:
    try:
        ct = (resp.headers.get("content-type") or "").lower()
        url = resp.url.lower()

        # filtramos cosas que no sirven
        if "mbtiles" in url or url.endswith(".png") or url.endswith(".jpg") or url.endswith(".webp"):
            return False

        return ("json" in ct) or ("geo+json" in ct) or url.endswith(".json")
    except:
        return False


def safe_name(url: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url)
    return name[:180] + ".json"


def run(address: str):
    OUT_DIR.mkdir(exist_ok=True)
    captured = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=30)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        def handle_response(resp):
            if not is_json_response(resp):
                return
            try:
                data = resp.json()
            except:
                return

            fn = safe_name(resp.url)
            (OUT_DIR / fn).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            captured.append(resp.url)
            print("JSON capturado:", resp.url)

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        # 1) Cerrar aviso legal
        close_legal_modal_if_present(page, timeout_ms=12000)

        # 2) Buscar dirección y confirmar con Enter DIRECTO al input
        page.wait_for_selector(SEARCH_INPUT, timeout=30000)
        search = page.locator(SEARCH_INPUT)
        search.click()
        search.fill(address)
        page.wait_for_timeout(200)
        search.press("Enter")

        # 3) Esperar posicionamiento
        page.wait_for_timeout(6000)

        # 5) Esperar que lleguen responses
        page.wait_for_timeout(6000)

        browser.close()

    (OUT_DIR / "_urls_capturadas.txt").write_text("\n".join(captured), encoding="utf-8")
    print(f"\nListo. Guardé {len(captured)} JSON en: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    run("Dávila 1172")
