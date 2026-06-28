# ウボンゴ3D オンライン - Streamlit版

## ファイル構成
```
streamlit_app/
├── app.py          ← Streamlitアプリ本体
├── ubongo2.html    ← ゲームファイル
├── requirements.txt
└── README.md
```

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
3. app.pyのSupabase接続コードを有効化
4. Streamlit CloudのSecretsに以下を追加：
   ```toml
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```
