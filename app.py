"""
GlowMatch — A BeautyTech Product Recommendation System
Run with: streamlit run app.py
"""
import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from recommender import GlowMatchRecommender, SKIN_TYPES

st.set_page_config(page_title="GlowMatch", page_icon="✨", layout="wide")

# ----------------------------------------------------------------------
# CURRENCY: India-based product, India-format currency (Indian digit
# grouping, e.g. ₹1,00,000 not ₹100,000) rather than just a symbol swap.
# ----------------------------------------------------------------------
USD_TO_INR = 83

def to_inr(usd_amount):
    return round(usd_amount * USD_TO_INR)

def format_inr(amount):
    n = int(amount)
    s = str(n)
    if len(s) <= 3:
        return s
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last3

# ----------------------------------------------------------------------
# THEME SYSTEM — light + dark, both built from the same design language
# (warm editorial beauty-magazine feel) so switching never looks like a
# different product, just a different lighting condition.
# ----------------------------------------------------------------------
THEMES = {
    "light": {
        "bg1": "#F7E9E4", "bg2": "#F0EAE0", "base": "#FBF6F1",
        "card": "#FFFFFF", "card_border": "#EFE5DA", "card_border_hover": "#E3D2C4",
        "ink": "#2B2320", "muted": "#6B5D53", "muted2": "#9C8C7E",
        "wine": "#6E2A3E", "wine_hover": "#55202F", "wine_light": "#FBF0F2",
        "sidebar": "#F5EDE4", "border": "#E8DDD3", "track": "#F0E6DB",
        "shadow": "rgba(110,42,62,0.14)", "badge_text": "#FFFFFF",
    },
    "dark": {
        "bg1": "#241A1E", "bg2": "#1D1614", "base": "#181211",
        "card": "#241C1A", "card_border": "#3A2E29", "card_border_hover": "#54423A",
        "ink": "#F3E9E1", "muted": "#C4B3A6", "muted2": "#9C8C7E",
        "wine": "#E8A0B4", "wine_hover": "#F0B7C6", "wine_light": "#3A222A",
        "sidebar": "#1F1715", "border": "#3A2E29", "track": "#3A2E29",
        "shadow": "rgba(232,160,180,0.12)", "badge_text": "#1D1614",
    },
}
CATEGORY_COLORS = {
    "Moisturizer": "#2E7D6B", "Cleanser": "#3B6FA0", "Face Mask": "#B8467A",
    "Treatment": "#B08A1E", "Eye cream": "#7B5EA7", "Sun protect": "#C9772E",
}
CATEGORY_ICONS = {
    "Moisturizer": "💧", "Cleanser": "🫧", "Face Mask": "🎭",
    "Treatment": "✨", "Eye cream": "👁", "Sun protect": "☀️",
}

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = set()

T = THEMES["dark"] if st.session_state["dark_mode"] else THEMES["light"]

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    html, body, .stApp {{
        background: radial-gradient(1200px 500px at 15% -10%, {T['bg1']} 0%, {T['base']} 45%),
                    radial-gradient(900px 500px at 100% 0%, {T['bg2']} 0%, {T['base']} 55%);
        font-family: 'Inter', sans-serif;
    }}
    * {{ color: {T['ink']}; }}
    .gm-cat-tag, .gm-cat-tag * {{ color: {T['badge_text']} !important; }}
    div.stButton > button, div.stButton > button * {{ color: #FFFFFF !important; }}

    @keyframes gm-fade-up {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    .gm-hero {{ padding: 8px 0 20px 0; border-bottom: 1px solid {T['border']}; margin-bottom: 24px;
        animation: gm-fade-up 0.5s ease-out; }}
    .gm-eyebrow {{ font-size: 12px; letter-spacing: 2px; text-transform: uppercase;
        color: {T['wine']}; font-weight: 700; margin-bottom: 6px; }}
    .gm-title {{ font-family: 'Fraunces', serif; font-size: 46px; font-weight: 700; margin: 0; line-height: 1.05;
        background: linear-gradient(100deg, {T['ink']} 45%, {T['wine']} 100%);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }}
    .gm-sub {{ font-size: 15px; color: {T['muted']}; margin-top: 10px; max-width: 640px; line-height: 1.5; }}

    .gm-stat-row {{ display: flex; gap: 28px; margin-top: 18px; flex-wrap: wrap; }}
    .gm-stat {{ display: flex; flex-direction: column; }}
    .gm-stat-num {{ font-family: 'Fraunces', serif; font-size: 26px; font-weight: 700; color: {T['wine']}; }}
    .gm-stat-label {{ font-size: 11px; color: {T['muted2']}; text-transform: uppercase; letter-spacing: 1px; }}

    .gm-card {{ background: {T['card']}; border-radius: 14px; padding: 16px 20px 16px 20px;
        margin-bottom: 16px; border: 1px solid {T['card_border']}; position: relative;
        transition: box-shadow 0.2s ease, transform 0.2s ease; height: 100%; animation: gm-fade-up 0.4s ease-out; }}
    .gm-card:hover {{ box-shadow: 0 10px 28px {T['shadow']}; transform: translateY(-3px); border-color: {T['card_border_hover']}; }}
    .gm-cat-tag {{ display: inline-block; font-size: 10.5px; font-weight: 700; letter-spacing: 0.5px;
        text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-bottom: 10px; }}
    .gm-name {{ font-family: 'Fraunces', serif; font-size: 17px; font-weight: 600; line-height: 1.25;
        margin-bottom: 2px; min-height: 44px; }}
    .gm-brand {{ font-size: 12.5px; color: {T['muted2']}; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.4px; margin-bottom: 10px; }}
    .gm-row {{ display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }}
    .gm-price {{ font-family: 'Fraunces', serif; font-size: 19px; font-weight: 700; color: {T['wine']}; }}
    .gm-stars {{ font-size: 14px; color: #D4A017; letter-spacing: 1px; }}
    .gm-stars-empty {{ color: {T['border']}; }}

    .gm-match-track {{ background: {T['track']}; border-radius: 6px; height: 6px; margin-top: 10px; overflow: hidden; }}
    .gm-match-fill {{ background: linear-gradient(90deg, {T['wine']}, #C97C93); height: 100%; border-radius: 6px; transition: width 0.6s ease; }}
    .gm-match-label {{ font-size: 11px; color: {T['muted2']}; margin-top: 4px; font-weight: 600; }}

    .gm-explain {{ background: {T['wine_light']}; border-left: 3px solid {T['wine']}; padding: 14px 18px;
        border-radius: 0 8px 8px 0; font-size: 14px; line-height: 1.6; margin-top: 8px; animation: gm-fade-up 0.4s ease-out; }}

    .gm-empty {{ text-align: center; padding: 50px 20px; color: {T['muted2']}; }}
    .gm-empty-title {{ font-family: 'Fraunces', serif; font-size: 20px; margin-bottom: 6px; }}

    .gm-fav-heart {{ position: absolute; top: 14px; right: 16px; font-size: 15px; }}

    section[data-testid="stSidebar"] {{ background-color: {T['sidebar']}; border-right: 1px solid {T['border']}; }}
    div.stButton > button {{ background-color: {T['wine']}; border: none; font-weight: 600;
        border-radius: 8px; padding: 9px 0; transition: background-color 0.15s ease, transform 0.1s ease; }}
    div.stButton > button:hover {{ background-color: {T['wine_hover']}; transform: translateY(-1px); }}
    div.stButton > button:active {{ transform: translateY(0); }}
    div.stButton > button[kind="secondary"] {{ background-color: transparent; border: 1px solid {T['border']}; }}
    div.stButton > button[kind="secondary"] * {{ color: {T['ink']} !important; }}

    div[data-baseweb="tab-list"] {{ gap: 4px; }}
    button[data-baseweb="tab"] {{ font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Mixing the formula — training TF-IDF, LSA embeddings, and KMeans personas...")
def load_engine():
    return GlowMatchRecommender()

rec = load_engine()

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    top = st.columns([3, 1])
    with top[0]:
        st.markdown("### 💧 Your skin profile")
    with top[1]:
        st.toggle("🌙", key="dark_mode", help="Dark mode")

    st.caption("First visit, no history needed — tell us about your skin. Updates live as you adjust filters.")
    skin_type = st.selectbox("Skin type", SKIN_TYPES)
    category_filter = st.selectbox("Category", ["All"] + sorted(rec.products["Label"].unique().tolist()))
    max_price_inr = st.slider("Budget (max ₹)", 0, 35000, 15000, step=500, format="₹%d")
    st.caption(f"Up to ₹{format_inr(max_price_inr)}")
    sort_by = st.radio("Sort by", ["Highest rated", "Price: low to high", "Price: high to low"], index=0)

    if st.session_state["favorites"]:
        st.divider()
        st.markdown(f"### ❤️ Favorites ({len(st.session_state['favorites'])})")
        if st.button("Clear favorites", use_container_width=True, type="secondary"):
            st.session_state["favorites"] = set()
            st.rerun()

# ----------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------
avg_rating = rec.products["Rank"].mean()
st.markdown(f"""
<div class="gm-hero">
    <div class="gm-eyebrow">BeautyTech recommendation engine</div>
    <div class="gm-title">Find your match, by formula</div>
    <div class="gm-sub">Hybrid recommendations built on real ingredient science — content-based
    matching, semantic vector search, and skin-type personalization across a 1,472-product catalog.</div>
    <div class="gm-stat-row">
        <div class="gm-stat"><span class="gm-stat-num">{len(rec.products):,}</span><span class="gm-stat-label">Products</span></div>
        <div class="gm-stat"><span class="gm-stat-num">{rec.products['Brand'].nunique()}</span><span class="gm-stat-label">Brands</span></div>
        <div class="gm-stat"><span class="gm-stat-num">{rec.products['Label'].nunique()}</span><span class="gm-stat-label">Categories</span></div>
        <div class="gm-stat"><span class="gm-stat-num">{avg_rating:.1f}</span><span class="gm-stat-label">Avg. rating</span></div>
    </div>
</div>
""", unsafe_allow_html=True)


def stars(rank, max_stars=5):
    filled = int(round(rank))
    return f'<span class="gm-stars">{"★" * filled}<span class="gm-stars-empty">{"★" * (max_stars - filled)}</span></span>'


def apply_sort(df, sort_by):
    if sort_by == "Price: low to high":
        return df.sort_values("Price", ascending=True)
    elif sort_by == "Price: high to low":
        return df.sort_values("Price", ascending=False)
    return df.sort_values("Rank", ascending=False)


def render_grid(df, match_col=None, explain_ids=None, key_prefix="grid"):
    if len(df) == 0:
        st.markdown("""
        <div class="gm-empty">
            <div class="gm-empty-title">Nothing matches these filters yet</div>
            <div>Try a higher budget or a different category — the catalog doesn't have a product for this exact combination.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, (_, row) in enumerate(df.iterrows()):
        color = CATEGORY_COLORS.get(row["Label"], T["wine"])
        icon = CATEGORY_ICONS.get(row["Label"], "•")
        pid = int(row["product_id"])
        match_html = ""
        if match_col and match_col in row:
            pct = int(round(row[match_col] * 100))
            match_html = f"""
            <div class="gm-match-track"><div class="gm-match-fill" style="width:{pct}%"></div></div>
            <div class="gm-match-label">{pct}% formula match</div>
            """
        is_fav = pid in st.session_state["favorites"]
        with cols[i % 3]:
            st.markdown(f"""
            <div class="gm-card">
                <span class="gm-fav-heart">{"❤️" if is_fav else "🤍"}</span>
                <span class="gm-cat-tag" style="background:{color}">{icon} {row['Label']}</span>
                <div class="gm-name">{row['Name']}</div>
                <div class="gm-brand">{row['Brand']}</div>
                {stars(row['Rank'])}
                <div class="gm-row">
                    <span class="gm-price">₹{format_inr(to_inr(row['Price']))}</span>
                </div>
                {match_html}
            </div>
            """, unsafe_allow_html=True)
            btn_label = "💔 Remove" if is_fav else "🤍 Save"
            if st.button(btn_label, key=f"{key_prefix}_fav_{pid}_{i}", use_container_width=True, type="secondary"):
                if is_fav:
                    st.session_state["favorites"].discard(pid)
                else:
                    st.session_state["favorites"].add(pid)
                st.rerun()

            if explain_ids is not None and i == 0:
                explanation = rec.explain_recommendation(explain_ids[0], pid)
                st.markdown(f'<div class="gm-explain">💬 {explanation}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------
# MAIN AREA
# ----------------------------------------------------------------------
tab_labels = ["✨ For You", "🔍 Similar Products", "🔥 Trending", "🧬 Ingredient Personas"]
if st.session_state["favorites"]:
    tab_labels.append(f"❤️ Favorites ({len(st.session_state['favorites'])})")
tabs = st.tabs(tab_labels)

# --- Tab: For You (fully reactive -- no stale-state bug: recomputes on
# every rerun from whatever the sidebar currently holds) ---
with tabs[0]:
    st.subheader(f"Picked for {skin_type.lower()} skin")
    results = rec.recommend_for_skin_profile(
        skin_type, category=None if category_filter == "All" else category_filter,
        max_price=max_price_inr / USD_TO_INR, n=9
    )
    results = apply_sort(results, sort_by)
    render_grid(results, key_prefix="foryou")

# --- Tab: Similar products ---
with tabs[1]:
    st.subheader("Because you liked...")
    st.caption("We blend ingredient-TF-IDF similarity with semantic vector search to find real formulation matches.")
    query = st.text_input("Search a product name", value="Facial Treatment Essence",
                           label_visibility="collapsed", placeholder="Search a product name...")
    matches = rec.products[rec.products["Name"].str.contains(query, case=False, na=False)] if query else rec.products.iloc[0:0]

    if query and len(matches) == 0:
        st.markdown('<div class="gm-empty"><div class="gm-empty-title">No product found</div>Try a shorter or different search term.</div>', unsafe_allow_html=True)
    elif len(matches) > 0:
        options = (matches["Brand"] + " — " + matches["Name"]).tolist()
        chosen = st.selectbox("Select the exact product", options, label_visibility="collapsed")
        chosen_id = int(matches.iloc[options.index(chosen)]["product_id"])
        similar = rec.recommend_similar_products(chosen_id, n=9)
        similar = apply_sort(similar, sort_by) if sort_by != "Highest rated" else similar
        render_grid(similar, match_col="match_score", explain_ids=[chosen_id], key_prefix="similar")

# --- Tab: Trending ---
with tabs[2]:
    st.subheader("Top-rated across the catalog")
    trending = rec.trending(n=9, category=None if category_filter == "All" else category_filter)
    trending = apply_sort(trending, sort_by)
    render_grid(trending, key_prefix="trend")

# --- Tab: Personas ---
with tabs[3]:
    st.subheader("Discovered by the algorithm, not hand-labeled")
    st.caption("KMeans clustering over the embedding space grouped the catalog into formulation personas from ingredient patterns alone — no manual tagging.")
    persona_cols = st.columns(3)
    for i, (p, name) in enumerate(rec.persona_names.items()):
        count = (rec.products["persona"] == p).sum()
        with persona_cols[i % 3]:
            with st.expander(f"{name}  ·  {count} products"):
                sample = rec.products[rec.products["persona"] == p][["Brand", "Name", "Label", "Rank"]].head(5)
                st.dataframe(sample, use_container_width=True, hide_index=True)

# --- Tab: Favorites (only shown when non-empty) ---
if st.session_state["favorites"]:
    with tabs[4]:
        st.subheader("Your saved products")
        fav_df = rec.products[rec.products["product_id"].isin(st.session_state["favorites"])]
        fav_df = apply_sort(fav_df, sort_by)
        render_grid(fav_df, key_prefix="favtab")

st.divider()
st.caption("Built for the GenAI Intern technical assignment. See DOCUMENTATION.md for architecture, methodology, metrics, and known limitations.")
