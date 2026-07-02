# ServiceNow CSA 学習システム

> 作成: 2026-07-02
> 目的: ServiceNow Certified System Administrator (CSA) 試験合格

---

## 1. 試験概要

| 項目 | 内容 |
|------|------|
| 正式名称 | ServiceNow Certified System Administrator (CSA) |
| 問題数 | 60問(採点対象外のパイロット問題が含まれる場合あり) |
| 試験時間 | 90分 |
| 形式 | 選択式(単一選択・複数選択) |
| 合格ライン | 非公開(一般に70%前後と言われる) |
| 受験方法 | オンライン監督付き(Kryterion Webassessor)または試験センター |
| 前提 | ServiceNow Administration Fundamentals 受講推奨(Now Learning) |
| 再受験 | 不合格時は待機期間あり・受験料は都度必要 |

### 出題分野と配点(Exam Blueprint)

| # | 分野 | 配点 | 学習ノート |
|---|------|------|----------|
| 1 | Platform Overview and Navigation | 7% | [notes/01_platform_overview.md](notes/01_platform_overview.md) |
| 2 | Instance Configuration | 11% | [notes/02_instance_configuration.md](notes/02_instance_configuration.md) |
| 3 | Configuring Applications for Collaboration | 20% | [notes/03_collaboration.md](notes/03_collaboration.md) |
| 4 | Self-Service & Automation | 20% | [notes/04_self_service_automation.md](notes/04_self_service_automation.md) |
| 5 | Database Management | 27% | [notes/05_database_management.md](notes/05_database_management.md) |
| 6 | Data Migration and Integration | 15% | [notes/06_data_migration.md](notes/06_data_migration.md) |

**配点の重心はデータベース管理(27%)**。テーブル構造・ACL・辞書まわりを最優先で固める。

---

## 2. 学習システムの使い方

### 問題演習アプリ

`app/index.html` をブラウザで開くだけで動く(サーバー不要・オフラインOK)。

```
open app/index.html
```

**4つのモード:**

| モード | 内容 |
|--------|------|
| 分野別練習 | 分野を選んで1問ずつ演習。即時に正誤+解説表示 |
| 模擬試験 | 本番と同じ60問・90分タイマー。終了後に分野別スコア表示 |
| 弱点復習 | 過去に間違えた問題だけを出題 |
| 全問ブラウズ | 問題+解答+解説を一覧で読む(直前の総復習用) |

進捗・正答率は localStorage に自動保存され、トップのダッシュボードに分野別で表示される。

### 学習ノート

`notes/` 配下に分野ごとの要点整理。アプリで間違えた分野のノートを読み直すループを回す。

---

## 3. 学習計画(2週間モデル)

| 日 | 内容 |
|----|------|
| Day 1-2 | ノート1〜3を通読 + 分野別練習(分野1〜3) |
| Day 3-4 | ノート4〜6を通読 + 分野別練習(分野4〜6) |
| Day 5 | 分野5(Database Management)を重点復習。ACL評価順序・テーブル継承を確実に |
| Day 6 | 模擬試験1回目 → 弱点復習モードで間違いを潰す |
| Day 7 | 間違えた分野のノート再読 + 分野別練習 |
| Day 8-10 | PDI(Personal Developer Instance)で実機操作(下記) |
| Day 11 | 模擬試験2回目 → 弱点復習 |
| Day 12 | 全問ブラウズで総復習 |
| Day 13 | 模擬試験3回目(85%以上で受験判断) |
| Day 14 | 予備日・受験 |

### 実機で必ず触ること(PDI: developer.servicenow.com で無料取得)

- ユーザー/グループ/ロール作成、impersonate(ユーザー切替)
- テーブル作成・フィールド追加・辞書オーバーライド、スキーママップ確認
- ACL作成(elevate to security_admin)
- Flow Designer で簡単なフロー作成
- カタログアイテム・レコードプロデューサー作成
- Import Set + Transform Map で CSV 取り込み(coalesce の挙動確認)
- Update Set 作成→取得→プレビュー→コミットの流れ

---

## 4. 公式リソース

- **Now Learning**: ServiceNow Administration Fundamentals(受講推奨コース)
- **CSA Exam Blueprint**: ServiceNow公式サイトで最新版を確認(リリースごとにDelta試験あり)
- **Product Docs**: docs.servicenow.com
- **PDI**: developer.servicenow.com(無料の個人開発インスタンス)

---

## 5. 運用メモ

- 問題追加は `app/questions.js` に追記(フォーマットはファイル冒頭コメント参照)
- 進捗リセットはアプリ内「進捗リセット」ボタン
- 模擬試験で **2回連続85%以上** になったら受験を予約する
