import streamlit as st
import streamlit.components.v1 as components
import html
import os
import tempfile
import threading
from datetime import datetime

st.set_page_config(
    page_title="ウボンゴ3D オンライン",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CSS =====
st.markdown("""
<style>
  .main .block-container { padding: 0.5rem 1rem; }
  h1 { font-size: 1.4rem; margin-bottom: 0.3rem; }
  .ranking-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .ranking-table th { background: #ede0ff; color: #5c3d9e; padding: 6px 10px; }
  .ranking-table td { padding: 5px 10px; border-bottom: 1px solid #e8d7f7; }
  .ranking-table tr:nth-child(1) td { background: #fff9e6; font-weight: bold; }
  .ranking-table tr:nth-child(2) td { background: #f5f5f5; }
  .ranking-table tr:nth-child(3) td { background: #fff3e0; }
  .medal { font-size: 1.2em; }
</style>
""", unsafe_allow_html=True)

GAME_HEIGHT = 700
MAX_SCORES = 1000

# ===== ゲームをStreamlitコンポーネントとして読み込み =====
# components.html() はゲームから値を受け取れないため、declare_component を使う。
# ubongo3.html を一時フォルダに index.html としてコピーし、そこをコンポーネントにする。
def load_game_component():
    html_path = os.path.join(os.path.dirname(__file__), "ubongo3.html")
    if not os.path.exists(html_path):
        return None
    with open(html_path, "r", encoding="utf-8") as f:
        game_html = f.read()

    component_dir = os.path.join(tempfile.gettempdir(), "ubongo3d_component")
    os.makedirs(component_dir, exist_ok=True)
    index_path = os.path.join(component_dir, "index.html")
    current = None
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            current = f.read()
    if current != game_html:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(game_html)

    return components.declare_component("ubongo3d_game", path=component_dir)

# ===== 全プレイヤー共通のランキング（サーバー起動中のみ保持） =====
@st.cache_resource
def get_ranking_store():
    return {"lock": threading.Lock(), "scores": []}

def add_score(entry):
    store = get_ranking_store()
    with store["lock"]:
        store["scores"].append(entry)
        if len(store["scores"]) > MAX_SCORES:
            store["scores"].sort(key=lambda x: -x["score"])
            del store["scores"][MAX_SCORES:]

def get_scores():
    store = get_ranking_store()
    with store["lock"]:
        return list(store["scores"])

def level_label(s):
    return f"Lv{s['level']}{'★' if s.get('is_star_level') else ''}"

# ===== セッション初期化 =====
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "last_score" not in st.session_state:
    st.session_state.last_score = None
if "seen_score_ids" not in st.session_state:
    st.session_state.seen_score_ids = set()

# ===== サイドバー：プレイヤー名入力 =====
with st.sidebar:
    st.markdown("### 👤 プレイヤー名")
    name_input = st.text_input(
        "名前を入力してスタート",
        value=st.session_state.player_name,
        max_chars=16,
        placeholder="例: たろう"
    )
    if name_input:
        st.session_state.player_name = name_input
        st.success(f"こんにちは、{name_input}さん！")

    st.divider()
    st.markdown("### 📋 操作方法")
    st.markdown("""
- **WASD / QE** : ブロック移動
- **IJKL / UO** : ブロック回転
- **1〜7** : ブロック選択
- **Tab** : 次のブロックへ
- **↑↓←→** : カメラ移動
""")

# ===== メインエリア =====
col_game, col_rank = st.columns([3, 1])

with col_game:
    if not st.session_state.player_name:
        st.info("👈 左のサイドバーにプレイヤー名を入力するとランキングに名前が載ります。")

    game_component = load_game_component()
    if game_component is None:
        st.error("ubongo3.html が見つかりません。同じフォルダに配置してください。")
    else:
        result = game_component(
            player_name=st.session_state.player_name,
            height=GAME_HEIGHT,
            key="ubongo3d_game",
            default=None
        )
        # ゲームクリア時にスコアが届く。再実行のたびに同じ値が返るので id で重複を除く
        if isinstance(result, dict) and result.get("id") not in st.session_state.seen_score_ids:
            st.session_state.seen_score_ids.add(result.get("id"))
            try:
                entry = {
                    "name": st.session_state.player_name or "名無し",
                    "level": int(result["level"]),
                    "time": float(result["time"]),
                    "score": int(result["score"]),
                    "stars": str(result["stars"])[:5],
                    "is_star_level": bool(result.get("isStarLevel")),
                    "ts": datetime.now().strftime("%H:%M")
                }
            except (KeyError, TypeError, ValueError):
                entry = None
            if entry:
                add_score(entry)
                st.session_state.last_score = entry

with col_rank:
    st.markdown("### 🏆 ランキング")

    all_scores = get_scores()
    if not all_scores:
        st.markdown("*まだ記録がありません*")
    else:
        # レベル別フィルター（通常 → ★ の順）
        labels = sorted(
            set(level_label(s) for s in all_scores),
            key=lambda l: (int(l[2:].rstrip("★")), l.endswith("★"))
        )
        level_filter = st.selectbox("レベル", ["全て"] + labels, key="level_filter")

        scores = all_scores
        if level_filter != "全て":
            scores = [s for s in scores if level_label(s) == level_filter]

        # スコア上位順にソート
        scores_sorted = sorted(scores, key=lambda x: -x["score"])[:10]

        medals = ["🥇", "🥈", "🥉"]
        rows = ""
        for i, s in enumerate(scores_sorted):
            medal = medals[i] if i < 3 else f"{i+1}"
            time_text = f"残り{s['time']:.1f}秒" if s.get("is_star_level") else f"{s['time']:.1f}秒"
            rows += f"""<tr>
              <td>{medal}</td>
              <td><b>{html.escape(s['name'])}</b></td>
              <td>{level_label(s)}</td>
              <td>{s['score']}点</td>
              <td>{time_text}</td>
              <td>{html.escape(s['stars'])}</td>
            </tr>"""

        st.markdown(f"""
        <table class="ranking-table">
          <tr><th></th><th>名前</th><th>Lv</th><th>スコア</th><th>タイム</th><th>評価</th></tr>
          {rows}
        </table>
        """, unsafe_allow_html=True)

    # 最新クリア情報
    if st.session_state.last_score:
        s = st.session_state.last_score
        st.divider()
        st.markdown("**最新クリア**")
        st.markdown(f"{level_label(s)} / {s['score']}点 / {s['stars']}")
