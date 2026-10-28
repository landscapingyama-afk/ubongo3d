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
- ランキングは全プレイヤー共通です
- Supabaseを設定すると記録はデータベースに保存され、アプリが再起動しても消えません
- Supabaseを設定していない場合はサーバーのメモリ上に保持するため、再起動
  （GitHubへのpush・スリープ・Reboot など）で消えます

## ローカルで起動する方法
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloudへのデプロイ手順

1. GitHubリポジトリを作成
2. このフォルダの中身を全てpush
3. https://share.streamlit.io にログイン
4. 「New app」→ リポジトリ・ブランチ・app.pyを選択
5. 「Deploy」ボタンを押すだけ

## Supabaseでランキングを保存する

1. https://supabase.com でプロジェクト作成（無料）
2. 左メニューの「SQL Editor」で以下を実行してテーブルを作成：
   ```sql
   create table scores (
     id bigserial primary key,
     name text not null check (char_length(name) between 1 and 16),
     level int not null check (level between 1 and 10),
     time real not null check (time >= 0 and time <= 3600),
     score int not null check (score between 0 and 1000),
     stars text not null check (char_length(stars) <= 5),
     is_star_level boolean not null default false,
     created_at timestamptz not null default now()
   );
   create index scores_rank_idx on scores (level, is_star_level, score desc);

   -- アプリ（anon / publishable キー）からは「読む」と「追加する」だけを許可する
   alter table scores enable row level security;
   create policy "scores are readable" on scores for select to anon using (true);
   create policy "scores can be added" on scores for insert to anon with check (true);
   ```
   ※ 以前のREADMEの手順で `scores` テーブルを作成済みの場合は、
   最後の `alter table` と `create policy` の3行だけ実行すれば使えます
3. 「Project Settings」→「API Keys」で、Project URL と anon（または publishable）キーを確認
4. Streamlit Cloud のアプリ画面「Settings」→「Secrets」に以下を貼り付けて保存：
   ```toml
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```
   ローカルで試す場合は同じ内容を `.streamlit/secrets.toml` に書きます（gitには含めません）。
   service_role / secret キーは全権限を持つので使わないでください。

設定すると `app.py` の `add_score` / `get_scores` が自動的にSupabaseを使うようになります。

## Supabaseの自動停止を防ぐ（GitHub Actions）

Supabaseの無料プランは7日間アクセスがないとプロジェクトが一時停止します。
`.github/workflows/supabase-keepalive.yml` が毎週月・木にランキングを1件読み込んで停止を防ぎます。

1. GitHubのリポジトリ画面「Settings」→「Secrets and variables」→「Actions」→「New repository secret」で
   `SUPABASE_URL` と `SUPABASE_KEY` を登録（Streamlit の Secrets と同じ値）
2. 「Actions」タブ →「Supabase keep-alive」→「Run workflow」で手動実行し、緑のチェックになることを確認

※ 定期実行はデフォルトブランチ（main）にこのファイルがあるときだけ動きます。
※ リポジトリに長期間（約60日）更新がないと、GitHubが定期実行を自動で止めることがあります。
  その場合は届いたメールか「Actions」タブから再度有効にしてください。
