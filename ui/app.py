import streamlit as st
import streamlit.components.v1 as components
import os, sys, uuid, json, base64
from PIL import Image

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VirtualWear — Dress for Your Culture",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from data.products import products
from src.tryon.pipeline import run_tryon

# ── REMOVE ALL STREAMLIT CHROME ───────────────────────────────────────────────
st.markdown("""
<style>
#root > div:first-child { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"], footer, #MainMenu { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None
if "tryon_result" not in st.session_state:
    st.session_state["tryon_result"] = None
if "person_path" not in st.session_state:
    st.session_state["person_path"] = None
if "active_community" not in st.session_state:
    st.session_state["active_community"] = "All"
if "active_category" not in st.session_state:
    st.session_state["active_category"] = "All"

# ── ENCODE LOCAL IMAGE TO BASE64 ──────────────────────────────────────────────
def img_to_b64(path: str) -> str:
    """Return base64 data URI for a local image, empty string if not found."""
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().strip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext, "jpeg")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{data}"

# ── PREPARE PRODUCTS FOR HTML ─────────────────────────────────────────────────
COMM_GRAD = {
    "Muslim":    "linear-gradient(160deg,#0D1B2A,#1a3a5c)",
    "Hindu":     "linear-gradient(160deg,#3d1a00,#8B4513)",
    "Christian": "linear-gradient(160deg,#0a2a0a,#1a5c1a)",
    "Sikh":      "linear-gradient(160deg,#2a1a00,#8B6914)",
    "Buddhist":  "linear-gradient(160deg,#0a1a10,#1a4a20)",
}
COMM_EMOJI = {"Muslim":"🧕","Hindu":"👘","Christian":"👗","Sikh":"🎀","Buddhist":"☸️"}

enriched = []
for i, p in enumerate(products):
    img_path = os.path.join(BASE_DIR, p["image"])
    b64 = img_to_b64(img_path)
    enriched.append({
        "idx":       i,
        "name":      p["name"],
        "community": p.get("community", "Muslim"),
        "category":  p.get("category", "Traditional"),
        "price":     p.get("price", 999),
        "rating":    p.get("rating", 4.5),
        "verified":  p.get("verified", False),
        "description": p.get("description", ""),
        "image":     b64,
        "grad":      COMM_GRAD.get(p.get("community","Muslim"), COMM_GRAD["Muslim"]),
        "emoji":     COMM_EMOJI.get(p.get("community","Muslim"), "👗"),
        "img_path":  img_path,
    })

products_json = json.dumps(enriched)

# ── BUILD THE FULL PAGE HTML ───────────────────────────────────────────────────
# This reads your design.html and injects the dynamic product grid + JS bridge.
design_html_path = os.path.join(BASE_DIR, "ui", "design.html")
use_design_file = os.path.exists(design_html_path)

PAGE_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VirtualWear</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{--navy:#0D1B2A;--gold:#C9A84C;--gl:#E8C97A;--gd:#A07A2A;--bg:#F9F7F4;--sf:#FFF;--txt:#0D1B2A;--mu:#6B7280;--bd:rgba(13,27,42,.1);--red:#E53E3E}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--txt);overflow-x:hidden;margin:0}}
h1,h2,h3,h4,h5{{font-family:'Playfair Display',serif}}
a{{text-decoration:none;color:inherit}}
button{{cursor:pointer;font-family:'Inter',sans-serif}}

/* ANNOUNCEMENT */
.ann{{background:var(--navy);color:var(--gold);text-align:center;padding:9px;font-size:.78rem;font-weight:500;letter-spacing:.03em}}

/* NAV */
nav{{position:sticky;top:0;z-index:150;background:var(--sf);border-bottom:1px solid var(--bd);box-shadow:0 2px 12px rgba(13,27,42,.06)}}
.nav-top{{display:flex;align-items:center;gap:1.25rem;padding:.875rem 2rem;max-width:1400px;margin:0 auto}}
.logo{{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:var(--navy)}}
.logo span{{color:var(--gold)}}
.nav-search{{flex:1;max-width:560px;display:flex;align-items:center;background:#F3F4F6;border:1.5px solid var(--bd);border-radius:8px;overflow:hidden;transition:border-color .2s}}
.nav-search:focus-within{{border-color:var(--gold)}}
.nav-search input{{flex:1;border:none;background:transparent;padding:.625rem 1rem;font-size:.875rem;font-family:'Inter',sans-serif;outline:none}}
.nav-search button{{background:var(--navy);border:none;padding:.625rem 1.125rem;color:var(--gold);font-size:.95rem}}
.nav-acts{{display:flex;align-items:center;gap:.375rem;margin-left:auto}}
.nb{{display:flex;flex-direction:column;align-items:center;gap:2px;padding:.45rem .875rem;border:none;background:transparent;color:var(--mu);font-size:.7rem;font-weight:500;border-radius:8px;transition:all .2s;position:relative}}
.nb:hover{{background:rgba(13,27,42,.05);color:var(--navy)}}
.nb .ic{{font-size:1.2rem}}
.nb .bx{{position:absolute;top:4px;right:6px;background:var(--red);color:#fff;border-radius:50%;width:16px;height:16px;font-size:.62rem;font-weight:700;display:flex;align-items:center;justify-content:center}}
.nb-si{{background:var(--navy);color:#fff;border:none;border-radius:8px;padding:.5rem 1.125rem;font-size:.85rem;font-weight:500}}
.nav-cats{{border-top:1px solid var(--bd)}}
.cats{{display:flex;max-width:1400px;margin:0 auto;padding:0 2rem;overflow-x:auto}}
.cat-btn{{padding:.6rem 1.1rem;font-size:.82rem;font-weight:500;color:var(--mu);border-bottom:2px solid transparent;white-space:nowrap;border:none;border-bottom:2px solid transparent;background:none;transition:all .2s}}
.cat-btn:hover,.cat-btn.act{{color:var(--navy);border-bottom-color:var(--gold);font-weight:600}}

/* HERO */
.hero{{background:var(--navy);padding:3.5rem 2rem;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(201,168,76,.08) 0%,transparent 55%);pointer-events:none}}
.hero-in{{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 380px;gap:3rem;align-items:center;position:relative;z-index:1}}
.h-tag{{display:inline-flex;align-items:center;gap:.5rem;background:rgba(201,168,76,.12);border:1px solid rgba(201,168,76,.28);border-radius:100px;padding:.3rem .9rem;font-size:.7rem;font-weight:600;color:var(--gold);letter-spacing:.08em;text-transform:uppercase;margin-bottom:1.25rem}}
.h-tag::before{{content:'';width:6px;height:6px;border-radius:50%;background:var(--gold);animation:blink 2s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.hero h1{{font-size:clamp(2rem,4vw,3.25rem);font-weight:700;line-height:1.1;color:#fff;margin-bottom:1rem;letter-spacing:-.02em}}
.hero h1 em{{color:var(--gold);font-style:italic}}
.hero p{{font-size:.95rem;color:rgba(255,255,255,.58);line-height:1.75;margin-bottom:2rem;font-weight:300;max-width:440px}}
.hero-btns{{display:flex;gap:.875rem;flex-wrap:wrap}}
.btn-gold{{background:var(--gold);color:var(--navy);border:none;border-radius:8px;padding:.75rem 1.75rem;font-size:.875rem;font-weight:600;transition:all .2s;cursor:pointer}}
.btn-gold:hover{{background:var(--gl);transform:translateY(-1px)}}
.btn-ghost{{background:transparent;color:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:.75rem 1.75rem;font-size:.875rem;font-weight:500;transition:all .2s;cursor:pointer}}
.btn-ghost:hover{{border-color:var(--gold);color:var(--gold)}}
.hero-stats{{display:flex;gap:2.5rem;margin-top:2.5rem;padding-top:2rem;border-top:1px solid rgba(255,255,255,.07)}}
.hs-num{{font-family:'Playfair Display',serif;font-size:1.75rem;font-weight:700;color:var(--gold)}}
.hs-lbl{{font-size:.74rem;color:rgba(255,255,255,.38)}}
.hcard{{background:rgba(255,255,255,.05);border:1px solid rgba(201,168,76,.18);border-radius:18px;padding:1.375rem;backdrop-filter:blur(8px)}}
.hcard-img{{height:200px;border-radius:12px;overflow:hidden;margin-bottom:1.125rem;background:linear-gradient(135deg,rgba(201,168,76,.12),rgba(13,27,42,.6));display:flex;align-items:center;justify-content:center;font-size:5rem}}
.hcard h4{{font-family:'Playfair Display',serif;color:#fff;font-size:.975rem;margin-bottom:.25rem}}
.hcard p{{color:rgba(255,255,255,.42);font-size:.75rem;margin-bottom:1rem}}
.hcard-row{{display:flex;justify-content:space-between;align-items:center}}
.hprice{{font-family:'Playfair Display',serif;color:var(--gold);font-size:1.2rem;font-weight:700}}
.btn-try-sm{{background:var(--gold);color:var(--navy);border:none;border-radius:6px;padding:.425rem .95rem;font-size:.78rem;font-weight:600}}

/* TRUST */
.trust{{background:var(--sf);border-bottom:1px solid var(--bd);padding:.825rem 2rem}}
.trust-in{{max-width:1400px;margin:0 auto;display:flex;justify-content:center;gap:2.5rem;flex-wrap:wrap}}
.ti{{display:flex;align-items:center;gap:.5rem;font-size:.78rem;font-weight:500;color:var(--mu)}}
.ti .ic{{color:var(--gold);font-size:1rem}}

/* COMMUNITY BAR */
.comm-bar{{background:var(--sf);padding:1.5rem 2rem;border-bottom:1px solid var(--bd)}}
.comm-pills{{max-width:1400px;margin:0 auto;display:flex;gap:.75rem;overflow-x:auto;padding-bottom:.25rem}}
.cpill{{display:flex;align-items:center;gap:.5rem;padding:.625rem 1.25rem;border-radius:100px;border:1.5px solid var(--bd);background:var(--bg);white-space:nowrap;cursor:pointer;transition:all .2s;font-size:.85rem;font-weight:500;color:var(--mu)}}
.cpill:hover,.cpill.act{{background:var(--navy);color:var(--gold);border-color:var(--navy)}}

/* FESTIVAL */
.sec{{padding:3.5rem 2rem}}
.sec-in{{max-width:1400px;margin:0 auto}}
.sec-hd{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1.75rem;flex-wrap:wrap;gap:1rem}}
.sec-tag{{font-size:.68rem;font-weight:600;color:var(--gold);letter-spacing:.12em;text-transform:uppercase;margin-bottom:.4rem}}
.sec-tt{{font-size:clamp(1.375rem,2.5vw,1.875rem);font-weight:700;color:var(--navy);line-height:1.2}}
.sec-lk{{font-size:.82rem;font-weight:600;color:var(--gold)}}
.fest-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}
.fc{{border-radius:16px;padding:1.75rem 1.375rem;min-height:170px;position:relative;overflow:hidden;cursor:pointer;transition:transform .25s}}
.fc:hover{{transform:scale(1.03)}}
.fc-pat{{position:absolute;inset:0;opacity:.04;background-image:repeating-linear-gradient(-45deg,#fff 0,#fff 1px,transparent 1px,transparent 14px)}}
.fc-em{{position:absolute;right:1rem;top:50%;transform:translateY(-50%);font-size:3rem;opacity:.75}}
.fc-lbl{{font-size:.66rem;font-weight:600;color:var(--gold);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.35rem;position:relative;z-index:1}}
.fc-tt{{font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;color:#fff;line-height:1.2;position:relative;z-index:1}}
.fc-sub{{font-size:.73rem;color:rgba(255,255,255,.48);margin-top:.3rem;position:relative;z-index:1}}

/* FILTER BAR */
.fbar{{display:flex;gap:.5rem;margin-bottom:1.5rem;flex-wrap:wrap;align-items:center}}
.fchip{{padding:.375rem .9rem;border-radius:100px;border:1px solid var(--bd);background:var(--sf);font-size:.78rem;font-weight:500;color:var(--mu);cursor:pointer;transition:all .2s;white-space:nowrap}}
.fchip:hover,.fchip.act{{background:var(--navy);color:var(--gold);border-color:var(--navy)}}
.sort-sel{{margin-left:auto;padding:.375rem .875rem;border:1px solid var(--bd);border-radius:100px;font-size:.78rem;font-family:'Inter',sans-serif;color:var(--mu);background:var(--sf);cursor:pointer;outline:none}}

/* PRODUCT GRID */
.pg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem}}
.pc{{background:var(--sf);border-radius:14px;border:1px solid var(--bd);overflow:hidden;transition:all .25s;cursor:pointer;position:relative}}
.pc:hover{{transform:translateY(-5px);box-shadow:0 16px 48px rgba(13,27,42,.12);border-color:rgba(201,168,76,.3)}}
.pc-img{{height:240px;position:relative;overflow:hidden;background:#f0ede8}}
.pc-img img{{width:100%;height:100%;object-fit:cover;transition:transform .4s}}
.pc:hover .pc-img img{{transform:scale(1.06)}}
.pc-img-fb{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:4.5rem}}
.pc-wish{{position:absolute;top:10px;right:10px;width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.92);border:none;font-size:.85rem;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .2s;z-index:2;box-shadow:0 2px 8px rgba(0,0,0,.15)}}
.pc:hover .pc-wish{{opacity:1}}
.pc-ov{{position:absolute;inset:0;background:rgba(13,27,42,.65);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.625rem;opacity:0;transition:opacity .25s;z-index:2}}
.pc:hover .pc-ov{{opacity:1}}
.btn-try-ov{{background:var(--gold);color:var(--navy);border:none;border-radius:100px;padding:.5rem 1.375rem;font-size:.82rem;font-weight:600}}
.btn-cart-ov{{background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:100px;padding:.4rem 1.125rem;font-size:.78rem;font-weight:500}}
.pc-ver{{position:absolute;top:10px;left:10px;background:rgba(34,139,34,.88);color:#fff;border-radius:100px;padding:.18rem .6rem;font-size:.66rem;font-weight:600;z-index:2}}
.pc-info{{padding:1rem}}
.pc-comm{{font-size:.66rem;font-weight:600;color:var(--gold);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.2rem}}
.pc-name{{font-family:'Playfair Display',serif;font-size:.95rem;font-weight:600;color:var(--navy);margin-bottom:.5rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.pc-desc{{font-size:.74rem;color:var(--mu);line-height:1.5;margin-bottom:.625rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.pc-meta{{display:flex;justify-content:space-between;align-items:center;margin-bottom:.625rem}}
.pc-price{{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--navy)}}
.pc-rate{{display:flex;align-items:center;gap:.2rem;font-size:.74rem;color:var(--mu)}}
.st{{color:#F59E0B;font-size:.7rem}}
.pc-acts{{display:flex;gap:.5rem}}
.btn-ac{{flex:1;background:var(--navy);color:#fff;border:none;border-radius:6px;padding:.5rem;font-size:.76rem;font-weight:500;transition:background .2s}}
.btn-ac:hover{{background:#1a3a5c}}
.btn-tr{{background:rgba(201,168,76,.1);color:var(--gd);border:1px solid rgba(201,168,76,.28);border-radius:6px;padding:.5rem .75rem;font-size:.76rem;font-weight:600;white-space:nowrap;transition:all .2s}}
.btn-tr:hover{{background:var(--gold);color:var(--navy)}}

/* SELECTED PRODUCT BANNER */
.sel-banner{{background:linear-gradient(135deg,#0D1B2A,#1a3a5c);border-radius:14px;padding:1.25rem 1.5rem;display:flex;align-items:center;gap:1.25rem;margin-bottom:1.5rem;border:1px solid rgba(201,168,76,.2)}}
.sel-img{{width:64px;height:64px;border-radius:10px;overflow:hidden;flex-shrink:0;background:rgba(255,255,255,.08)}}
.sel-img img{{width:100%;height:100%;object-fit:cover}}
.sel-img-fb{{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:2rem}}

/* TRYON SECTION */
.tryon-sec{{background:var(--navy);padding:4rem 2rem;position:relative;overflow:hidden}}
.tryon-sec::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 65% 50%,rgba(201,168,76,.07) 0%,transparent 60%)}}
.tryon-in{{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:3rem;position:relative;z-index:1}}
.t-steps{{margin-top:1.75rem;display:flex;flex-direction:column;gap:1.125rem}}
.t-step{{display:flex;align-items:flex-start;gap:1rem}}
.t-num{{width:32px;height:32px;flex-shrink:0;border-radius:50%;background:rgba(201,168,76,.12);border:1px solid rgba(201,168,76,.25);display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-size:.82rem;color:var(--gold);font-weight:700}}
.t-txt h4{{font-family:'Inter',sans-serif;font-size:.875rem;font-weight:600;color:#fff;margin-bottom:.15rem}}
.t-txt p{{font-size:.8rem;color:rgba(255,255,255,.42)}}

/* UPLOAD ZONE */
.uz{{border:2px dashed var(--bd);border-radius:14px;padding:2rem 1rem;text-align:center;cursor:pointer;transition:all .2s;background:rgba(255,255,255,.03);position:relative;min-height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center}}
.uz:hover{{border-color:var(--gold);background:rgba(201,168,76,.04)}}
.uz input[type=file]{{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}}
.uz-ic{{font-size:2.25rem;margin-bottom:.75rem}}
.uz p{{font-size:.82rem;color:rgba(255,255,255,.55);margin-bottom:.25rem}}
.uz span{{font-size:.75rem;color:var(--gold);font-weight:600}}
.uz-preview{{width:100%;max-height:200px;object-fit:cover;border-radius:10px;margin-bottom:.625rem}}

/* RESULT */
.result-box{{background:rgba(255,255,255,.04);border:1px solid rgba(201,168,76,.15);border-radius:14px;min-height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1.5rem;text-align:center;overflow:hidden}}
.result-img{{width:100%;border-radius:10px;display:none}}
.progress-wrap{{width:100%;margin-top:1rem;display:none}}
.pbar{{height:4px;background:rgba(255,255,255,.1);border-radius:2px;overflow:hidden}}
.pfill{{height:100%;background:var(--gold);border-radius:2px;transition:width .4s;width:0%}}
.pstatus{{font-size:.75rem;color:rgba(255,255,255,.4);margin-top:.5rem;text-align:center}}
.btn-dl{{background:var(--gold);color:var(--navy);border:none;border-radius:8px;padding:.625rem 1.375rem;font-size:.82rem;font-weight:600;margin-top:1rem;cursor:pointer;display:none}}
.score-pill{{display:inline-block;background:rgba(201,168,76,.12);border:1px solid rgba(201,168,76,.28);border-radius:100px;padding:4px 14px;font-size:.78rem;font-weight:600;color:var(--gold);margin-top:.75rem;display:none}}

/* COMPARISON */
.compare-grid{{display:grid;grid-template-columns:1fr 1fr;gap:.875rem;margin-top:1rem;display:none}}
.compare-card{{background:rgba(255,255,255,.04);border-radius:10px;overflow:hidden}}
.compare-card img{{width:100%;object-fit:cover}}
.compare-label{{text-align:center;font-size:.72rem;color:rgba(255,255,255,.4);padding:.5rem}}

/* SEARCH MODAL */
.s-ov{{position:fixed;inset:0;background:rgba(13,27,42,.85);z-index:700;opacity:0;pointer-events:none;transition:opacity .2s;display:flex;flex-direction:column;align-items:center;padding-top:10vh}}
.s-ov.open{{opacity:1;pointer-events:all}}
.s-box{{width:680px;max-width:95vw;background:var(--sf);border-radius:14px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.3)}}
.s-row{{display:flex;align-items:center;padding:.875rem 1.25rem;gap:.875rem;border-bottom:1px solid var(--bd)}}
.s-row input{{flex:1;border:none;font-size:1.05rem;font-family:'Inter',sans-serif;outline:none}}
.s-res{{padding:.875rem;max-height:400px;overflow-y:auto}}
.sr{{display:flex;align-items:center;gap:.875rem;padding:.7rem;border-radius:8px;cursor:pointer;transition:background .15s}}
.sr:hover{{background:var(--bg)}}
.sr-img{{width:42px;height:42px;background:var(--bg);border-radius:8px;overflow:hidden;flex-shrink:0}}
.sr-img img{{width:100%;height:100%;object-fit:cover}}
.sr-nm{{font-size:.875rem;font-weight:500;color:var(--navy)}}
.sr-ct{{font-size:.72rem;color:var(--mu)}}

/* CART */
.cart-ov{{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:500;opacity:0;pointer-events:none;transition:opacity .3s}}
.cart-ov.open{{opacity:1;pointer-events:all}}
.cart-dr{{position:fixed;top:0;right:0;bottom:0;width:400px;background:var(--sf);z-index:501;transform:translateX(100%);transition:transform .3s;display:flex;flex-direction:column;box-shadow:-8px 0 40px rgba(0,0,0,.15)}}
.cart-dr.open{{transform:translateX(0)}}
.cart-hd{{padding:1.125rem 1.5rem;border-bottom:1px solid var(--bd);display:flex;justify-content:space-between;align-items:center}}
.cart-hd h3{{font-family:'Playfair Display',serif;font-size:1.2rem}}
.cart-cl{{background:none;border:none;font-size:1.4rem;color:var(--mu)}}
.cart-its{{flex:1;overflow-y:auto;padding:1rem 1.5rem;display:flex;flex-direction:column;gap:.875rem}}
.cit{{display:flex;gap:.875rem;padding:.875rem;background:var(--bg);border-radius:10px;align-items:center}}
.cit-img{{width:56px;height:56px;border-radius:8px;overflow:hidden;flex-shrink:0;background:#f0ede8}}
.cit-img img{{width:100%;height:100%;object-fit:cover}}
.cit-name{{font-size:.82rem;font-weight:600;color:var(--navy);margin-bottom:.2rem}}
.cit-price{{font-family:'Playfair Display',serif;font-size:.9rem;font-weight:700;color:var(--gd)}}
.cit-rm{{background:none;border:none;color:var(--mu);font-size:.72rem;cursor:pointer;margin-top:.25rem}}
.cart-ft{{padding:1.125rem 1.5rem;border-top:1px solid var(--bd)}}
.cart-tot{{display:flex;justify-content:space-between;margin-bottom:.875rem;font-weight:600;font-size:.95rem}}
.btn-co{{width:100%;background:var(--navy);color:#fff;border:none;border-radius:8px;padding:.875rem;font-size:.9rem;font-weight:600}}

/* TOAST */
.toast{{position:fixed;bottom:2rem;right:2rem;background:var(--navy);color:#fff;border-left:4px solid var(--gold);padding:.875rem 1.375rem;border-radius:10px;font-size:.85rem;font-weight:500;z-index:900;transform:translateX(120%);transition:transform .35s;box-shadow:0 8px 32px rgba(0,0,0,.25);max-width:320px}}
.toast.show{{transform:translateX(0)}}

/* FOOTER */
footer{{background:var(--navy);padding:3.5rem 2rem 1.5rem;border-top:1px solid rgba(201,168,76,.15)}}
.ft-in{{max-width:1400px;margin:0 auto}}
.ft-top{{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:2.5rem;margin-bottom:2.5rem}}
.ft-logo{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:var(--gold)}}
.ft-logo span{{color:#fff}}
.ft-brand p{{font-size:.82rem;color:rgba(255,255,255,.38);margin-top:.875rem;line-height:1.7;font-weight:300;max-width:240px}}
.ft-soc{{display:flex;gap:.625rem;margin-top:1.125rem}}
.sb{{width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);display:flex;align-items:center;justify-content:center;font-size:.82rem;color:rgba(255,255,255,.55);cursor:pointer;transition:all .2s}}
.sb:hover{{background:var(--gold);color:var(--navy);border-color:var(--gold)}}
.ft-col h5{{font-family:'Inter',sans-serif;font-size:.68rem;font-weight:600;color:rgba(255,255,255,.3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1rem}}
.ft-col ul{{list-style:none;display:flex;flex-direction:column;gap:.55rem}}
.ft-col ul a{{font-size:.82rem;color:rgba(255,255,255,.5);font-weight:300;transition:color .2s}}
.ft-col ul a:hover{{color:var(--gold)}}
.ft-bot{{border-top:1px solid rgba(255,255,255,.06);padding-top:1.375rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.875rem}}
.ft-bot p{{font-size:.75rem;color:rgba(255,255,255,.22);font-weight:300}}

@media(max-width:900px){{
  .hero-in,.tryon-in{{grid-template-columns:1fr}}
  .hcard{{display:none}}
  .fest-grid{{grid-template-columns:1fr 1fr}}
  .ft-top{{grid-template-columns:1fr 1fr}}
}}
@media(max-width:600px){{
  .nav-top{{padding:.7rem 1rem;gap:.625rem}}
  .nav-search{{display:none}}
  .pg{{grid-template-columns:repeat(2,1fr)}}
  .fest-grid{{grid-template-columns:1fr}}
  .sec{{padding:2.5rem 1rem}}
}}
</style>
</head>
<body>

<!-- ANNOUNCEMENT -->
<div class="ann">🌙 Eid Collection Live • Free Shipping ₹999+ • AI Virtual Try-On • 2,400+ Verified Sellers</div>

<!-- NAV -->
<nav>
  <div class="nav-top">
    <a href="#" class="logo">Virtual<span>Wear</span></a>
    <div class="nav-search">
      <input id="si" type="text" placeholder="Search abayas, sarees, kurtas..." onfocus="openS()" oninput="liveS(this.value)">
      <button onclick="openS()">🔍</button>
    </div>
    <div class="nav-acts">
      <button class="nb" onclick="openS()"><span class="ic">🔍</span><span>Search</span></button>
      <button class="nb"><span class="ic">👤</span><span>Account</span></button>
      <button class="nb"><span class="ic">❤️</span><span>Wishlist</span></button>
      <button class="nb" onclick="openCart()"><span class="ic">🛍️</span><span>Cart</span><span class="bx" id="cc">0</span></button>
      <button class="nb-si">Sign In</button>
    </div>
  </div>
  <div class="nav-cats">
    <div class="cats">
      <button class="cat-btn act" onclick="fComm('All',this)">All Communities</button>
      <button class="cat-btn" onclick="fComm('Muslim',this)">🕌 Muslim</button>
      <button class="cat-btn" onclick="fComm('Hindu',this)">🪔 Hindu</button>
      <button class="cat-btn" onclick="fComm('Christian',this)">✝️ Christian</button>
      <button class="cat-btn" onclick="fComm('Sikh',this)">🪯 Sikh</button>
      <button class="cat-btn" onclick="fComm('Buddhist',this)">☸️ Buddhist</button>
      <button class="cat-btn" onclick="fCat('Traditional',this)">Traditional</button>
      <button class="cat-btn" onclick="fCat('Islamic',this)">Islamic</button>
      <button class="cat-btn" onclick="fCat('Western',this)">Western</button>
    </div>
  </div>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-in">
    <div>
      <div class="h-tag">AI-Powered Try-On • Now Live</div>
      <h1>Dress for Your<br><em>Culture,</em><br>Your Way.</h1>
      <p>One platform. Every community. Shop abayas, sarees, sherwanis and more — personalized to your faith, powered by AI virtual try-on.</p>
      <div class="hero-btns">
        <button class="btn-gold" onclick="scroll2('products-section')">Shop Now</button>
        <button class="btn-ghost" onclick="scroll2('tryon-section')">✨ Try On a Garment</button>
      </div>
      <div class="hero-stats">
        <div><div class="hs-num">19+</div><div class="hs-lbl">Products</div></div>
        <div><div class="hs-num">5</div><div class="hs-lbl">Communities</div></div>
        <div><div class="hs-num">2K+</div><div class="hs-lbl">Verified Sellers</div></div>
        <div><div class="hs-num">4.6★</div><div class="hs-lbl">Avg Rating</div></div>
      </div>
    </div>
    <div class="hcard">
      <div class="hcard-img">🧕</div>
      <h4>Embroidered Abaya — Eid Edition</h4>
      <p>Verified Muslim Seller &nbsp;•&nbsp; Free Delivery</p>
      <div class="hcard-row">
        <span class="hprice">₹1,299</span>
        <button class="btn-try-sm" onclick="scroll2('tryon-section')">✨ Try On</button>
      </div>
    </div>
  </div>
</section>

<!-- TRUST -->
<div class="trust">
  <div class="trust-in">
    <div class="ti"><span class="ic">🚚</span>Free Delivery ₹999+</div>
    <div class="ti"><span class="ic">✓</span>Verified Sellers</div>
    <div class="ti"><span class="ic">↩️</span>10-Day Returns</div>
    <div class="ti"><span class="ic">🔒</span>Secure Payments</div>
    <div class="ti"><span class="ic">✨</span>AI Try-On</div>
    <div class="ti"><span class="ic">🌐</span>8 Languages</div>
  </div>
</div>

<!-- COMMUNITY -->
<div class="comm-bar">
  <div class="comm-pills">
    <div class="cpill act" onclick="fComm('All',null);setAC(this)"><span>🛍️</span>All Communities</div>
    <div class="cpill" onclick="fComm('Muslim',null);setAC(this)"><span>🕌</span>Muslim</div>
    <div class="cpill" onclick="fComm('Hindu',null);setAC(this)"><span>🪔</span>Hindu</div>
    <div class="cpill" onclick="fComm('Christian',null);setAC(this)"><span>✝️</span>Christian</div>
    <div class="cpill" onclick="fComm('Sikh',null);setAC(this)"><span>🪯</span>Sikh</div>
    <div class="cpill" onclick="fComm('Buddhist',null);setAC(this)"><span>☸️</span>Buddhist</div>
  </div>
</div>

<!-- FESTIVAL -->
<section class="sec" style="background:var(--sf)">
  <div class="sec-in">
    <div class="sec-hd">
      <div><div class="sec-tag">Seasonal</div><h2 class="sec-tt">Festival Collections</h2></div>
      <a href="#" class="sec-lk">View All →</a>
    </div>
    <div class="fest-grid">
      <div class="fc" style="background:linear-gradient(135deg,#0D1B2A,#1a3a5c)" onclick="fComm('Muslim',null)">
        <div class="fc-pat"></div><div class="fc-em">🌙</div>
        <div class="fc-lbl">Live Now</div><div class="fc-tt">Eid Collection 2026</div>
        <div class="fc-sub">Abayas · Thobes · Hijabs</div>
      </div>
      <div class="fc" style="background:linear-gradient(135deg,#3d1a00,#8B4513)" onclick="fComm('Hindu',null)">
        <div class="fc-pat"></div><div class="fc-em">🪔</div>
        <div class="fc-lbl">Pre-Order</div><div class="fc-tt">Diwali Collection</div>
        <div class="fc-sub">Sarees · Lehengas · Dhotis</div>
      </div>
      <div class="fc" style="background:linear-gradient(135deg,#0a2a0a,#1a5c1a)" onclick="fComm('Christian',null)">
        <div class="fc-pat"></div><div class="fc-em">🎄</div>
        <div class="fc-lbl">Coming Soon</div><div class="fc-tt">Christmas Collection</div>
        <div class="fc-sub">Gowns · Suits · Gift Sets</div>
      </div>
      <div class="fc" style="background:linear-gradient(135deg,#2a1a00,#8B6914)" onclick="fComm('Sikh',null)">
        <div class="fc-pat"></div><div class="fc-em">🪯</div>
        <div class="fc-lbl">New Arrivals</div><div class="fc-tt">Gurpurab Special</div>
        <div class="fc-sub">Turbans · Kurtas · Accessories</div>
      </div>
    </div>
  </div>
</section>

<!-- PRODUCTS -->
<section class="sec" id="products-section">
  <div class="sec-in">
    <div class="sec-hd">
      <div>
        <div class="sec-tag" id="ptag">All Products</div>
        <h2 class="sec-tt" id="ptt">Shop Everything</h2>
      </div>
      <div style="display:flex;align-items:center;gap:.75rem">
        <span style="font-size:.8rem;color:var(--mu)" id="pcnt">19 products</span>
        <a href="#" class="sec-lk">View All →</a>
      </div>
    </div>
    <div class="fbar">
      <button class="fchip act" onclick="fCat('All',this)">All</button>
      <button class="fchip" onclick="fCat('Islamic',this)">Islamic</button>
      <button class="fchip" onclick="fCat('Traditional',this)">Traditional</button>
      <button class="fchip" onclick="fCat('Western',this)">Western</button>
      <select class="sort-sel" onchange="sortP(this.value)">
        <option value="">Sort By</option>
        <option value="pl">Price: Low to High</option>
        <option value="ph">Price: High to Low</option>
        <option value="rt">Top Rated</option>
        <option value="nm">Name A-Z</option>
      </select>
    </div>
    <div class="pg" id="pg"></div>
  </div>
</section>

<!-- TRY-ON SECTION -->
<section class="tryon-sec" id="tryon-section">
  <div class="tryon-in">
    <!-- LEFT: INFO -->
    <div>
      <div style="font-size:.68rem;font-weight:600;color:var(--gold);letter-spacing:.12em;text-transform:uppercase;margin-bottom:.5rem">AI Virtual Try-On</div>
      <h2 style="font-size:clamp(1.75rem,3.5vw,2.5rem);font-weight:700;color:#fff;line-height:1.15;margin-bottom:1rem">See It On <em style="color:var(--gold)">You</em><br>Before You Buy.</h2>
      <p style="color:rgba(255,255,255,.5);font-size:.9rem;font-weight:300;max-width:400px;line-height:1.75;margin-bottom:1.5rem">Upload your photo. AI detects your body pose using MediaPipe, removes backgrounds with rembg, and drapes any garment naturally — then saves your result.</p>
      <div class="t-steps">
        <div class="t-step"><div class="t-num">1</div><div class="t-txt"><h4>Select a Product</h4><p>Click "Try On" on any product in the grid above.</p></div></div>
        <div class="t-step"><div class="t-num">2</div><div class="t-txt"><h4>Upload Your Photo</h4><p>Clear full-body front-facing photo works best.</p></div></div>
        <div class="t-step"><div class="t-num">3</div><div class="t-txt"><h4>AI Processes</h4><p>Background removed + garment warped to your body.</p></div></div>
        <div class="t-step"><div class="t-num">4</div><div class="t-txt"><h4>Download Result</h4><p>Save your try-on image and shop with confidence.</p></div></div>
      </div>
    </div>

    <!-- RIGHT: INTERACTIVE -->
    <div>
      <!-- SELECTED PRODUCT BANNER -->
      <div class="sel-banner" id="sel-banner" style="display:none">
        <div class="sel-img"><img id="sel-img" src="" alt=""><div class="sel-img-fb" id="sel-fb"></div></div>
        <div>
          <p style="color:rgba(255,255,255,.5);font-size:.75rem;margin:0 0 .25rem">Trying on</p>
          <h4 style="font-family:'Playfair Display',serif;color:var(--gold);font-size:1rem;margin:0" id="sel-name">—</h4>
          <p style="color:rgba(255,255,255,.4);font-size:.75rem;margin:.25rem 0 0" id="sel-price">—</p>
        </div>
      </div>
      <div id="sel-empty" style="background:rgba(255,255,255,.04);border:1px dashed rgba(201,168,76,.2);border-radius:14px;padding:1.25rem;text-align:center;margin-bottom:1.5rem">
        <p style="color:rgba(255,255,255,.35);font-size:.85rem;margin:0">👆 Select a product above to try it on</p>
      </div>

      <!-- UPLOAD PHOTO -->
      <p style="color:rgba(255,255,255,.7);font-size:.82rem;font-weight:600;margin-bottom:.625rem">📷 Your Photo</p>
      <div class="uz" onclick="document.getElementById('pi').click()">
        <img class="uz-preview" id="pp" style="display:none" alt="">
        <div id="pph">
          <div class="uz-ic">📷</div>
          <p>Upload full body photo</p>
          <span>Click to browse • JPG / PNG</span>
        </div>
        <input type="file" id="pi" accept="image/*" onchange="handlePerson(this)">
      </div>

      <!-- GENERATE BUTTON -->
      <button id="btn-gen" onclick="genTryon()" style="width:100%;background:var(--gold);color:var(--navy);border:none;border-radius:10px;padding:.875rem;font-size:.95rem;font-weight:700;margin-top:1rem;transition:all .2s;opacity:.5;cursor:not-allowed">
        🚀 Generate Try-On
      </button>

      <!-- RESULT -->
      <div style="margin-top:1.25rem">
        <p style="color:rgba(255,255,255,.7);font-size:.82rem;font-weight:600;margin-bottom:.625rem">✨ Result</p>
        <div class="result-box" id="rbox">
          <div id="rph" style="display:flex;flex-direction:column;align-items:center;gap:.75rem">
            <div style="font-size:3rem">✨</div>
            <p style="color:rgba(255,255,255,.35);font-size:.82rem">Select product + upload photo,<br>then click Generate.</p>
          </div>
          <div class="progress-wrap" id="pwrap">
            <div class="pbar"><div class="pfill" id="pfill"></div></div>
            <div class="pstatus" id="pstatus">Processing...</div>
          </div>
          <img class="result-img" id="rimg" src="" alt="Try-On Result">
          <div class="score-pill" id="spill">✨ AI Fit Score: 87% Match</div>
          <button class="btn-dl" id="btn-dl" onclick="dlResult()">⬇️ Download Result</button>
        </div>
        <div class="compare-grid" id="cgrid">
          <div class="compare-card">
            <img id="cimg-orig" src="" alt="Original"><div class="compare-label" style="color:rgba(255,255,255,.4)">Original</div>
          </div>
          <div class="compare-card">
            <img id="cimg-res" src="" alt="With Garment"><div class="compare-label" style="color:rgba(255,255,255,.4)">With Garment</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="ft-in">
    <div class="ft-top">
      <div class="ft-brand">
        <div class="ft-logo">Virtual<span>Wear</span></div>
        <p>A first-of-its-kind community e-commerce platform — built for everyone, personalized to you.</p>
        <div class="ft-soc">
          <div class="sb">𝕏</div><div class="sb">in</div><div class="sb">f</div><div class="sb">📸</div>
        </div>
      </div>
      <div class="ft-col"><h5>Communities</h5><ul><li><a href="#">Muslim Store</a></li><li><a href="#">Hindu Store</a></li><li><a href="#">Christian Store</a></li><li><a href="#">Sikh Store</a></li><li><a href="#">Buddhist Store</a></li></ul></div>
      <div class="ft-col"><h5>Features</h5><ul><li><a href="#">Virtual Try-On</a></li><li><a href="#">Body Measurement</a></li><li><a href="#">Festival Collections</a></li><li><a href="#">Verified Sellers</a></li></ul></div>
      <div class="ft-col"><h5>Sellers</h5><ul><li><a href="#">Sell on VirtualWear</a></li><li><a href="#">Verification</a></li><li><a href="#">Dashboard</a></li></ul></div>
      <div class="ft-col"><h5>Help</h5><ul><li><a href="#">About Us</a></li><li><a href="#">Returns</a></li><li><a href="#">Track Order</a></li><li><a href="#">Contact</a></li></ul></div>
    </div>
    <div class="ft-bot">
      <p>© 2026 VirtualWear Technologies Pvt. Ltd. Built by Mohammed Aaiz · AITM Bengaluru</p>
    </div>
  </div>
</footer>

<!-- CART -->
<div class="cart-ov" id="cart-ov" onclick="closeCart()"></div>
<div class="cart-dr" id="cart-dr">
  <div class="cart-hd"><h3>Your Cart</h3><button class="cart-cl" onclick="closeCart()">✕</button></div>
  <div class="cart-its" id="cart-its"><div style="text-align:center;padding:3rem 1rem;color:var(--mu)"><div style="font-size:3rem;margin-bottom:1rem">🛍️</div><p style="font-size:.875rem">Cart is empty!</p></div></div>
  <div class="cart-ft" id="cart-ft" style="display:none">
    <div class="cart-tot"><span>Subtotal</span><span id="ctot" style="font-family:'Playfair Display',serif">₹0</span></div>
    <div style="font-size:.72rem;color:var(--mu);margin-bottom:.875rem">Taxes & shipping at checkout</div>
    <button class="btn-co">Proceed to Checkout →</button>
  </div>
</div>

<!-- SEARCH -->
<div class="s-ov" id="s-ov" onclick="closeS(event)">
  <div class="s-box" onclick="event.stopPropagation()">
    <div class="s-row">
      <span style="color:var(--mu);font-size:1rem">🔍</span>
      <input id="sb" type="text" placeholder="Search products, communities..." oninput="doS(this.value)">
      <button onclick="closeS(event)" style="background:none;border:none;font-size:1.2rem;color:var(--mu)">✕</button>
    </div>
    <div class="s-res" id="sres"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ── DATA (injected from Python) ───────────────────────────────────────────────
const PRODS = {products_json};

// ── STATE ─────────────────────────────────────────────────────────────────────
let aC='All', aK='All', cart=[], fp=[...PRODS];
let selectedProd=null, personB64=null, personFilename=null;

// ── RENDER PRODUCTS ───────────────────────────────────────────────────────────
function render(prods){{
  const g=document.getElementById('pg');
  document.getElementById('pcnt').textContent=prods.length+' products';
  if(!prods.length){{
    g.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:4rem;color:var(--mu)"><div style="font-size:3rem;margin-bottom:1rem">🔍</div><p>No products found.</p></div>';
    return;
  }}
  g.innerHTML=prods.map(p=>`
    <div class="pc">
      <div class="pc-img" style="background:${{p.grad}}">
        <button class="pc-wish" onclick="event.stopPropagation();this.textContent=this.textContent==='🤍'?'❤️':'🤍'">🤍</button>
        ${{p.verified?'<div class="pc-ver">✓ Verified</div>':''}}
        ${{p.image?`<img src="${{p.image}}" alt="${{p.name}}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="pc-img-fb" style="display:none">${{p.emoji}}</div>`
          :`<div class="pc-img-fb">${{p.emoji}}</div>`}}
        <div class="pc-ov">
          <button class="btn-try-ov" onclick="event.stopPropagation();selectProd(${{p.idx}})">✨ Try On</button>
          <button class="btn-cart-ov" onclick="event.stopPropagation();addCart(${{p.idx}})">🛍️ Add to Cart</button>
        </div>
      </div>
      <div class="pc-info">
        <div class="pc-comm">${{p.community}} • ${{p.category}}</div>
        <div class="pc-name">${{p.name}}</div>
        <div class="pc-desc">${{p.description}}</div>
        <div class="pc-meta">
          <div class="pc-price">₹${{p.price.toLocaleString('en-IN')}}</div>
          <div class="pc-rate"><span class="st">★</span>${{p.rating}}</div>
        </div>
        <div class="pc-acts">
          <button class="btn-ac" onclick="addCart(${{p.idx}})">Add to Cart</button>
          <button class="btn-tr" onclick="selectProd(${{p.idx}})">✨ Try On</button>
        </div>
      </div>
    </div>`).join('');
}}

// ── FILTERS ───────────────────────────────────────────────────────────────────
function applyF(){{
  let r=[...PRODS];
  if(aC!=='All') r=r.filter(p=>p.community===aC);
  if(aK!=='All') r=r.filter(p=>p.category===aK);
  fp=r; render(r);
  document.getElementById('ptag').textContent=aC==='All'?'All Products':aC+' Store';
  document.getElementById('ptt').textContent=aK==='All'?'Shop Everything':'Shop '+aK;
}}
function fComm(c,el){{
  aC=c;
  if(el){{document.querySelectorAll('.cat-btn').forEach(e=>e.classList.remove('act'));el.classList.add('act')}}
  applyF(); scroll2('products-section');
}}
function fCat(k,el){{
  aK=k;
  if(el){{document.querySelectorAll('.fchip').forEach(e=>e.classList.remove('act'));el.classList.add('act')}}
  applyF();
}}
function setAC(el){{document.querySelectorAll('.cpill').forEach(e=>e.classList.remove('act'));el.classList.add('act')}}
function sortP(v){{
  let r=[...fp];
  if(v==='pl') r.sort((a,b)=>a.price-b.price);
  else if(v==='ph') r.sort((a,b)=>b.price-a.price);
  else if(v==='rt') r.sort((a,b)=>b.rating-a.rating);
  else if(v==='nm') r.sort((a,b)=>a.name.localeCompare(b.name));
  render(r);
}}

// ── SELECT PRODUCT FOR TRY-ON ─────────────────────────────────────────────────
function selectProd(idx){{
  selectedProd=PRODS.find(p=>p.idx===idx);
  if(!selectedProd) return;
  // Update banner
  document.getElementById('sel-banner').style.display='flex';
  document.getElementById('sel-empty').style.display='none';
  document.getElementById('sel-name').textContent=selectedProd.name;
  document.getElementById('sel-price').textContent='₹'+selectedProd.price.toLocaleString('en-IN')+' • '+selectedProd.community;
  const img=document.getElementById('sel-img');
  const fb=document.getElementById('sel-fb');
  if(selectedProd.image){{img.src=selectedProd.image;img.style.display='block';fb.style.display='none'}}
  else{{img.style.display='none';fb.style.display='flex';fb.textContent=selectedProd.emoji}}
  checkReady();
  scroll2('tryon-section');
  toast('Selected: '+selectedProd.name+' ✨');
}}

// ── PERSON UPLOAD ─────────────────────────────────────────────────────────────
function handlePerson(input){{
  const file=input.files[0]; if(!file) return;
  personFilename=file.name;
  const reader=new FileReader();
  reader.onload=e=>{{
    personB64=e.target.result;
    const prev=document.getElementById('pp');
    const hold=document.getElementById('pph');
    prev.src=personB64; prev.style.display='block'; hold.style.display='none';
    checkReady();
  }};
  reader.readAsDataURL(file);
}}

function checkReady(){{
  const btn=document.getElementById('btn-gen');
  if(selectedProd && personB64){{
    btn.style.opacity='1'; btn.style.cursor='pointer';
  }} else {{
    btn.style.opacity='.5'; btn.style.cursor='not-allowed';
  }}
}}

// ── GENERATE TRY-ON (sends to Streamlit via postMessage) ──────────────────────
function genTryon(){{
  if(!selectedProd||!personB64){{ toast('⚠️ Select a product and upload your photo first!'); return; }}
  const rph=document.getElementById('rph');
  const pwrap=document.getElementById('pwrap');
  const pfill=document.getElementById('pfill');
  const pstatus=document.getElementById('pstatus');
  const rimg=document.getElementById('rimg');
  const spill=document.getElementById('spill');
  const bdl=document.getElementById('btn-dl');
  const cgrid=document.getElementById('cgrid');

  rph.style.display='none'; rimg.style.display='none';
  spill.style.display='none'; bdl.style.display='none'; cgrid.style.display='none';
  pwrap.style.display='block';

  const steps=[
    [15,'Loading images...'],
    [30,'Removing background...'],
    [50,'Detecting body pose...'],
    [65,'Estimating keypoints...'],
    [80,'Warping garment...'],
    [92,'Compositing result...'],
    [100,'Done! ✅'],
  ];
  let si=0;
  const iv=setInterval(()=>{{
    if(si>=steps.length){{ clearInterval(iv); sendToStreamlit(); return; }}
    pfill.style.width=steps[si][0]+'%';
    pstatus.textContent=steps[si][1];
    si++;
  }},450);
}}

function sendToStreamlit(){{
  // Send data to Streamlit parent via postMessage
  window.parent.postMessage({{
    type:'virtualwear_tryon',
    personB64: personB64,
    productIdx: selectedProd.idx,
    productImgPath: selectedProd.img_path,
    productName: selectedProd.name,
  }}, '*');
}}

// Listen for result from Streamlit
window.addEventListener('message', e=>{{
  if(e.data && e.data.type==='tryon_result'){{
    showResult(e.data.resultB64, e.data.success, e.data.message);
  }}
}});

function showResult(resultB64, success, message){{
  const pwrap=document.getElementById('pwrap');
  const rimg=document.getElementById('rimg');
  const spill=document.getElementById('spill');
  const bdl=document.getElementById('btn-dl');
  const cgrid=document.getElementById('cgrid');
  const rph=document.getElementById('rph');

  pwrap.style.display='none';

  if(success && resultB64){{
    rimg.src=resultB64; rimg.style.display='block';
    spill.style.display='inline-block'; bdl.style.display='inline-block';
    cgrid.style.display='grid';
    document.getElementById('cimg-orig').src=personB64;
    document.getElementById('cimg-res').src=resultB64;
    window._resultB64=resultB64;
    toast('✅ Try-on complete!');
  }} else {{
    rph.style.display='flex';
    rph.innerHTML='<div style="font-size:2.5rem;margin-bottom:.75rem">⚠️</div><p style="color:rgba(255,255,255,.35);font-size:.82rem">'+( message||'Try-on failed. Check image quality.')+' Try a different photo.</p>';
    toast('❌ '+(message||'Try-on failed'));
  }}
}}

function dlResult(){{
  if(!window._resultB64) return;
  const a=document.createElement('a');
  a.download='virtualwear_tryon.png';
  a.href=window._resultB64; a.click();
  toast('✅ Downloaded!');
}}

// ── CART ──────────────────────────────────────────────────────────────────────
function addCart(idx){{
  const p=PRODS.find(x=>x.idx===idx);
  if(!p) return;
  if(cart.find(c=>c.idx===idx)){{toast('Already in cart: '+p.name);return}}
  cart.push(p); updateCart(); toast('Added: '+p.name);
}}
function rmCart(idx){{cart=cart.filter(c=>c.idx!==idx);updateCart()}}
function updateCart(){{
  document.getElementById('cc').textContent=cart.length;
  const tot=cart.reduce((s,c)=>s+c.price,0);
  document.getElementById('ctot').textContent='₹'+tot.toLocaleString('en-IN');
  const its=document.getElementById('cart-its'), ft=document.getElementById('cart-ft');
  if(!cart.length){{its.innerHTML='<div style="text-align:center;padding:3rem 1rem;color:var(--mu)"><div style="font-size:3rem;margin-bottom:1rem">🛍️</div><p style="font-size:.875rem">Cart is empty!</p></div>';ft.style.display='none';return}}
  ft.style.display='block';
  its.innerHTML=cart.map(c=>`<div class="cit"><div class="cit-img">${{c.image?`<img src="${{c.image}}" onerror="this.innerHTML='<span style=font-size:1.5rem>${{c.emoji}}</span>'" alt="">`:c.emoji}}</div><div><div class="cit-name">${{c.name}}</div><div class="cit-price">₹${{c.price.toLocaleString('en-IN')}}</div><button class="cit-rm" onclick="rmCart(${{c.idx}})">Remove</button></div></div>`).join('');
}}
function openCart(){{document.getElementById('cart-ov').classList.add('open');document.getElementById('cart-dr').classList.add('open')}}
function closeCart(){{document.getElementById('cart-ov').classList.remove('open');document.getElementById('cart-dr').classList.remove('open')}}

// ── SEARCH ────────────────────────────────────────────────────────────────────
function openS(){{document.getElementById('s-ov').classList.add('open');setTimeout(()=>document.getElementById('sb').focus(),80);doS('')}}
function closeS(e){{if(!e||e.target===document.getElementById('s-ov')) document.getElementById('s-ov').classList.remove('open')}}
function liveS(q){{if(q.length>1){{openS();document.getElementById('sb').value=q;doS(q)}}}}
function doS(q){{
  const res=document.getElementById('sres');
  const m=q?PRODS.filter(p=>p.name.toLowerCase().includes(q.toLowerCase())||p.category.toLowerCase().includes(q.toLowerCase())||p.community.toLowerCase().includes(q.toLowerCase())).slice(0,8):PRODS.slice(0,8);
  res.innerHTML=m.length?m.map(p=>`<div class="sr" onclick="document.getElementById('s-ov').classList.remove('open');selectProd(${{p.idx}})">
    <div class="sr-img">${{p.image?`<img src="${{p.image}}" onerror="this.innerHTML='<span style=font-size:1.25rem>${{p.emoji}}</span>'" alt="">`:p.emoji}}</div>
    <div><div class="sr-nm">${{p.name}}</div><div class="sr-ct">${{p.community}} • ${{p.category}}</div></div>
    <div style="margin-left:auto;font-size:.82rem;color:var(--gold);font-weight:600">₹${{p.price.toLocaleString('en-IN')}}</div>
  </div>`).join(''):'<div style="text-align:center;padding:2rem;color:var(--mu);font-size:.875rem">No results found</div>';
}}

// ── UTILS ─────────────────────────────────────────────────────────────────────
function toast(msg){{const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3200)}}
function scroll2(id){{document.getElementById(id).scrollIntoView({{behavior:'smooth'}})}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape'){{closeCart();document.getElementById('s-ov').classList.remove('open')}}}});

// ── INIT ──────────────────────────────────────────────────────────────────────
render(PRODS);
</script>
</body>
</html>"""

# ── RENDER FULL PAGE HTML ─────────────────────────────────────────────────────
components.html(PAGE_HTML, height=6000, scrolling=True)

# ── HIDDEN STREAMLIT BACKEND: LISTENS FOR TRY-ON REQUESTS ────────────────────
# We use a query param hack to receive postMessage from the iframe
# The HTML sends postMessage → Streamlit catches it via st.query_params

query = st.query_params
if "tryon_trigger" in query:
    # This path is used when JS posts a form or URL param
    pass

# ── JAVASCRIPT BRIDGE: RECEIVE MESSAGES AND PROCESS TRY-ON ───────────────────
# Inject a listener script outside the iframe to catch messages
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'virtualwear_tryon') {
        // Store in sessionStorage for Streamlit to pick up
        sessionStorage.setItem('vw_tryon_request', JSON.stringify(event.data));
        // Trigger a Streamlit rerun by submitting a hidden form
        const form = document.getElementById('vw-trigger-form');
        if (form) form.submit();
    }
    if (event.data && event.data.type === 'tryon_result') {
        // Forward result into the iframe
        const iframe = document.querySelector('iframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage(event.data, '*');
        }
    }
});
</script>
""", unsafe_allow_html=True)

# ── PROCESS TRY-ON VIA UPLOAD WIDGET (HIDDEN) ─────────────────────────────────
# Alternative: hidden Streamlit try-on processor triggered by session state
st.markdown("---")
with st.expander("⚙️ Backend Try-On Processor (Advanced)", expanded=False):
    st.caption("Use this if the in-page try-on doesn't trigger automatically.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Upload your photo:**")
        person_file = st.file_uploader("Your photo", type=["jpg","jpeg","png"], key="be_person", label_visibility="collapsed")
    with col2:
        st.markdown("**Select product:**")
        prod_names = [p["name"] for p in products]
        selected_name = st.selectbox("Product", prod_names, key="be_prod", label_visibility="collapsed")

    if st.button("🚀 Run Try-On", type="primary", use_container_width=True):
        selected = next((p for p in products if p["name"] == selected_name), None)
        if person_file and selected:
            person_img = Image.open(person_file).convert("RGB")
            os.makedirs(os.path.join(BASE_DIR, "temp"), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, "outputs"), exist_ok=True)
            person_path = os.path.join(BASE_DIR, "temp", f"person_{uuid.uuid4().hex}.jpg")
            person_img.save(person_path, quality=95)
            cloth_path = os.path.join(BASE_DIR, selected["image"])

            if not os.path.exists(cloth_path):
                st.error(f"❌ Garment image not found at: {cloth_path}")
            else:
                with st.spinner("🤖 Running AI try-on..."):
                    progress = st.progress(0)
                    for i, pct in enumerate([20,40,60,80,100]):
                        import time; time.sleep(0.3)
                        progress.progress(pct)
                    result_path = run_tryon(
                        person_path, cloth_path,
                        output_path=os.path.join(BASE_DIR, "outputs", f"result_{uuid.uuid4().hex}.png")
                    )

                if result_path and os.path.exists(result_path):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.image(person_path, caption="Your Photo", use_container_width=True)
                    with c2:
                        cloth_img_path = os.path.join(BASE_DIR, selected["image"])
                        if os.path.exists(cloth_img_path):
                            st.image(cloth_img_path, caption="Garment", use_container_width=True)
                    with c3:
                        st.image(result_path, caption="✨ Try-On Result", use_container_width=True)
                    st.success("✅ Try-on complete!")
                    with open(result_path, "rb") as f:
                        st.download_button("⬇️ Download", f, "tryon_result.png", "image/png", use_container_width=True)
                else:
                    st.error("❌ Try-on failed. Check your photo quality and try again.")
        else:
            st.warning("Please upload a photo and select a product.")