import streamlit as st
import streamlit.components.v1 as components
import json
import os
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

# ===== ゲームHTML読み込み =====
def load_game_html():
    html_path = os.path.join(os.path.dirname(__file__), "ubongo3.html")
    if not os.path.exists(html_path):
        return None
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# ===== セッション初期化 =====
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "scores" not in st.session_state:
    st.session_state.scores = []  # {name, level, time, score, stars, ts}
if "last_score" not in st.session_state:
    st.session_state.last_score = None

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
        st.info("👈 左のサイドバーにプレイヤー名を入力するとゲームを始められます。")

    game_html = load_game_html()
    if game_html is None:
        st.error("ubongo3.html が見つかりません。同じフォルダに配置してください。")
    else:
        # postMessageでスコアを受け取るためのラッパーを追加
        wrapper = f"""
        <div id="game-wrapper">
          {game_html}
        </div>
        <script>
        // Streamlitへスコアを送信
        window.addEventListener('message', function(e) {{
          if (e.data && e.data.type === 'ubongo_score') {{
            window.parent.postMessage({{
              type: 'streamlit:setComponentValue',
              value: e.data
            }}, '*');
          }}
        }});
        </script>
        """
        components.html(wrapper, height=700, scrolling=False)

with col_rank:
    st.markdown("### 🏆 ランキング")

    if not st.session_state.scores:
        st.markdown("*まだ記録がありません*")
    else:
        # レベル別フィルター
        levels = sorted(set(s["level"] for s in st.session_state.scores))
        level_filter = st.selectbox(
            "レベル",
            ["全て"] + [f"Lv{l}" for l in levels],
            key="level_filter"
        )

        scores = st.session_state.scores
        if level_filter != "全て":
            lv = int(level_filter.replace("Lv", ""))
            scores = [s for s in scores if s["level"] == lv]

        # スコア上位順にソート
        scores_sorted = sorted(scores, key=lambda x: -x["score"])[:10]

        medals = ["🥇", "🥈", "🥉"]
        rows = ""
        for i, s in enumerate(scores_sorted):
            medal = medals[i] if i < 3 else f"{i+1}"
            rows += f"""<tr>
              <td>{medal}</td>
              <td><b>{s['name']}</b></td>
              <td>Lv{s['level']}</td>
              <td>{s['score']}点</td>
              <td>{s['time']:.1f}秒</td>
              <td>{s['stars']}</td>
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
        st.markdown(f"**最新クリア**")
        st.markdown(f"Lv{s['level']} / {s['score']}点 / {s['stars']}")

# ===== スコア受信処理 =====
# ゲームからpostMessageで受け取ったスコアを登録するボタン（開発用）
with st.expander("🔧 スコアを手動登録（テスト用）", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        test_level = st.number_input("レベル", 1, 10, 1)
        test_time = st.number_input("タイム(秒)", 1.0, 999.0, 30.0)
    with col2:
        test_score = st.number_input("スコア", 0, 1000, 700)
        test_stars = st.selectbox("星", ["★★★", "★★☆", "★☆☆"])
    with col3:
        st.markdown("&nbsp;")
        if st.button("登録", use_container_width=True):
            if st.session_state.player_name:
                entry = {
                    "name": st.session_state.player_name,
                    "level": test_level,
                    "time": test_time,
                    "score": test_score,
                    "stars": test_stars,
                    "ts": datetime.now().strftime("%H:%M")
                }
                st.session_state.scores.append(entry)
                st.session_state.last_score = entry
                st.success("登録しました！")
                st.rerun()
            else:
                st.warning("プレイヤー名を入力してください")
