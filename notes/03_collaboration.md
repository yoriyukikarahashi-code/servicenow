# 分野3: Configuring Applications for Collaboration(配点 20%)

## 1. ユーザー・グループ・ロール

ユーザー(sys_user)、グループ(sys_user_group)、ロール(sys_user_role)の3層構造。ロールはグループに付与してユーザーはグループに所属させるのがベストプラクティス。security_adminはelevate roleで一時昇格して使う。

## 2. タスクテーブル(Task Table)

taskテーブルが親で、Incident/Problem/Change/Requestなどが拡張。共通フィールドを継承。

## 3. Visual Task Board(VTB)

Flexible(自由レーン)、Guided(フィールド連動)、Freeform(自由追加)の3種類。

## 4. 通知(Notifications)

3要素: When to send / Who will receive / What it will contain。イベント駆動(gs.eventQueue())も可。

## 5. レポートとダッシュボード

レポートは「今」のデータ、Performance Analytics(PA)は「経時変化」のトレンド分析。

## 6. ナレッジ管理(Knowledge Management)

KB > Category > Article の階層。Draft → Review → Published → Retired のライフサイクル。User Criteria で Can Read / Can Contribute を制御。

## 7. Connect / チャット

Work notes(内部) / Additional comments(顧客向け)の使い分け。

## 全体構造マップ

```
【ユーザー管理の3層構造】

  sys_user (ユーザー)
    └─ 所属 ──→ sys_user_group (グループ)
                    └─ 付与 ──→ sys_user_role (ロール)
                                    └─ 制御 ──→ ACL / Application Access

  ※ security_admin ロール: Elevate Role → 一時昇格 → セッション終了で失効

【タスク継承ツリー】

  task (親テーブル: 共通フィールドを定義)
    ├── incident          (インシデント管理)
    ├── problem           (問題管理)
    ├── change_request    (変更管理)
    └── sc_request        (サービスリクエスト)
              └── sc_req_item (カタログアイテム)

  ※ sys_dictionary にフィールド定義が格納される

【通知フロー】

  トリガー条件(レコード変更 / イベント)
    └─→ Notification レコード
              ├── When to send  (条件: フィルター / イベント名)
              ├── Who receives  (ユーザー / グループ / フィールド値)
              └── What contains (件名 / 本文 / 変数テンプレート)

  gs.eventQueue("event.name", record) ──→ Event Queue ──→ 通知 or Script Action

【ナレッジ管理の階層と公開フロー】

  Knowledge Base (kb_knowledge_base)
    └── Category (kb_category)
              └── Article (kb_knowledge)
                      ライフサイクル:
                      Draft ──→ Review ──→ Published ──→ Retired

  アクセス制御:
  User Criteria ──→ Can Read / Can Contribute を KB または Category 単位で適用

【VTBの種類と用途】

  Visual Task Board
    ├── Flexible   : レーンを手動で自由に作成、タスクを自由配置
    ├── Guided     : フィールド値(例: State)にレーンが連動、移動で値が変わる
    └── Freeform   : ボードに直接カード(レコード外)を自由追加可能

【レポート vs Performance Analytics】

  Report (レポート)
    └── 現時点のデータをスナップショット表示
          → テーブル / 棒グラフ / 円グラフ など

  Performance Analytics (PA)
    └── スコアを定期収集(Job) → 時系列でトレンド分析
          → Scorecard / Breakdown で経時変化を可視化
```

## PDI 操作ガイド

### タスク1: ユーザー・グループ・ロールの付与を体験する

1. **All → User Administration → Users** を開く
2. 「New」をクリックし、テスト用ユーザーを作成する（User ID: `test.csa`、First name、Last name を入力して Save）
3. **All → User Administration → Groups** を開き、「New」でテスト用グループを作成する（Name: `CSA Test Group`）
4. グループレコードの「Roles」タブを開き、「Edit」から `itil` ロールを追加する
5. グループレコードの「Members」タブを開き、先ほど作成した `test.csa` ユーザーを追加する
6. **確認**: test.csa でログインし直し、Incident モジュールが表示されることを確認する（itil ロールの効果）

### タスク2: 通知(Notification)の3要素を確認する

1. **All → System Notification → Email → Notifications** を開く
2. 既存の通知（例: `Incident opened for user`）をクリックして開く
3. 以下の3タブを順に確認する:
   - **When to send** タブ: 送信条件（テーブル名・条件フィルター・イベント）
   - **Who will receive** タブ: 受信者（Users / Groups / フィールド値）
   - **What it will contain** タブ: 件名と本文テンプレート（`${field_name}` 変数）
4. **確認**: 「Send to event creator」チェックボックスの位置と意味を把握する

### タスク3: ナレッジベースの記事を作成し公開フローを体験する

1. **All → Knowledge → Knowledge Bases** を開き、「New」でナレッジベースを作成する（Title: `CSA Practice KB`）
2. **All → Knowledge → Articles** を開き、「New」をクリック
3. Knowledge Base に `CSA Practice KB` を指定し、Title と本文を入力して **Save** する（状態: Draft）
4. レコード上部の **Submit for Review** ボタンをクリック → 状態が `Review` に変わることを確認
5. **Publish** ボタンをクリック → 状態が `Published` になることを確認
6. **All → Knowledge → Administration → User Criteria** を開き、「New」で閲覧制限を設定してみる（Roles に `itil` を指定）。KB の「Can Read」タブに適用して動作を確認する

### タスク4: Visual Task Boardを3種類作成して違いを体験する

1. **All → Visual Task Board** を開き、「New Board」をクリック
2. **Guided** を選択し、テーブルに `incident`、レーンフィールドに `State` を指定して作成する
3. カードを別レーンにドラッグし、インシデントの State フィールドが自動変更されることを確認する
4. 再度「New Board」→ **Freeform** を選択し、ボード上で直接カードを追加してみる（テーブルレコードと紐づかない点を確認）

### タスク5: レポートとダッシュボードを作成する

1. **All → Reports → Create New** を開く
2. Source に `Incident [incident]` を選択し、Type に `Bar` を選ぶ
3. Group by に `Priority` を指定して **Run** → 現時点の件数が棒グラフで表示されることを確認
4. 「Add to Dashboard」ボタンでホームページダッシュボードに追加する
5. **All → Self-Service → Dashboards** を開き、追加されたウィジェットを確認する

## 試験との接続

「ロールをユーザーに直接付与するのとグループ経由で付与するのはどちらが推奨か」→ PDI でユーザーレコードの Roles タブとグループの Roles タブの両方を開くと、グループ経由では「1か所の変更が全メンバーに波及する」構造が視覚的に明確になり、グループ付与がベストプラクティスである理由を直感的に理解できる。

「通知の受信者をフィールド値（例: Assigned to）で指定するにはどこで設定するか」→ PDI で既存の Notification を開き「Who will receive」タブの「Fields」欄を確認すると、テーブルのユーザー型フィールドが受信者として直接指定できる仕組みが一目でわかり、「イベント送信者に送る」オプションとの違いも把握できる。

「ナレッジ記事の Can Read と Can Contribute は何で制御するか」→ PDI でナレッジベースレコードの「Can Read」「Can Contribute」タブを開き User Criteria を追加・削除すると、ロールや部署単位でのアクセス制御がテーブルACLとは独立した仕組みで動いていることがわかり、「User Criteria」という正しい用語を選択肢から選べるようになる。

「Guided VTBでカードを移動すると何が起きるか」→ PDI で Guided ボードのカードをドラッグすると背後のレコードの State フィールドが即座に変わることが確認でき、「レーン移動がフィールド値を更新する」という Guided の定義を選択肢と直結させて記憶できる。

「ReportとPerformance Analyticsの用途の違いは何か」→ PDI でレポートを実行して現時点の棒グラフを見た後、PA の Scorecard を開くと時系列グラフが表示され「Reportはスナップショット／PAはトレンド」という対比が視覚として定着し、"どちらを使うべきか"を問う設問で迷わなくなる。
