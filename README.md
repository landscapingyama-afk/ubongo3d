# ウボンゴ3D オンライン - Streamlit版

## ファイル構成
```
.
├── app.py                   ← Streamlitアプリ本体
├── ubongo3.html             ← ゲームファイル（Streamlitコンポーネントとして読み込み）
├── tools/check_patterns.py  ← 問題データの検証（python3 tools/check_patterns.py）
├── requirements.txt
└── README.md
```

## ランキングの仕組み
- ゲームをクリアするとスコアが自動でStreamlitに送られ、右側のランキングに登録されます
- ランキングは全プレイヤー共通ですが、サーバーのメモリ上に保持しているため再起動で消えます
  （永続化するには下記のSupabase連携が必要です）

## ローカルで起動する方法
```bash
pip install streamlit
streamlit run app.py
```

## Streamlit Cloudへのデプロイ手順

1. GitHubリポジトリを作成
2. このフォルダの中身を全てpush
3. https://share.streamlit.io にログイン
4. 「New app」→ リポジトリ・ブランチ・app.pyを選択
5. 「Deploy」ボタンを押すだけ

## 次のステップ：Supabaseでオンラインランキング

1. https://supabase.com でプロジェクト作成（無料）
2. 以下のテーブルを作成：
   ```sql
   create table scores (
     id serial primary key,
     name text not null,
     level int not null,
     time float not null,
     score int not null,
     stars text,
     is_star_level boolean default false,
     created_at timestamp default now()
   );
   ```
3. app.pyの `add_score` / `get_scores` をSupabaseへの保存・取得に置き換える
4. Streamlit CloudのSecretsに以下を追加：
   ```toml
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```
