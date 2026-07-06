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

## 8. Client Scripts

クライアントサイドで実行されるJavaScript。フォームの動的制御に使用。

**種類:**
- `onLoad`: フォーム読み込み時に実行
- `onChange`: フィールド値変更時に実行
- `onSubmit`: フォーム送信(保存)時に実行
- `onCellEdit`: リストのインライン編集時に実行

**g_form API (フォーム操作):**
- `g_form.getValue('field')`: フィールド値を取得
- `g_form.setValue('field', value)`: フィールド値をセット
- `g_form.setMandatory('field', true/false)`: 必須/任意を切替
- `g_form.setVisible('field', true/false)`: 表示/非表示を切替
- `g_form.setReadOnly('field', true/false)`: 読み取り専用を切替
- `g_form.addInfoMessage('msg')`: 情報メッセージを表示
- `g_form.clearMessages()`: メッセージをクリア

**g_user API (ユーザー情報):**
- `g_user.hasRole('role_name')`: ロール保持確認
- `g_user.getFullName()`: フルネーム取得
- `g_user.getUserID()`: sys_id取得

**UI Policy vs Client Script:**
- UI Policy: コードなしで表示/必須/読み取り専用を制御（推奨）
- Client Script: より複雑な条件ロジックやAPIコール時に使用

## 9. Performance Analytics (PA)

**PA Indicators (指標/KPI):**
- 測定対象を定義するKPI（例: 未解決インシデント数）
- `Automated` タイプ: データを自動収集するスクリプト
- `Manual` タイプ: 手動入力

**PA Breakdowns (分解):**
- Indicatorのデータを切り口で分解（例: Priority別、Assignment Group別）
- BreakdownとIndicatorをマッピングして多角分析

**PA Scheduled Jobs:**
- Indicatorのデータを定期収集するジョブ
- 収集頻度: 日次/週次/月次等

**Scores / Targets / Thresholds:**
- Score: 実測値
- Target: 目標値
- Threshold: アラート閾値

**PA Dashboards:** Scorecard(時系列グラフ)とWidgetで可視化

## 10. 通知詳細

**Notification Digest:** 複数の通知をまとめてバッチ送信（メール爆発防止）

**Notification Subscriptions:** ユーザーが通知のオン/オフを自分で設定できる仕組み

**Notification Devices:** Email / SMS / Push Notification の送信先デバイス

**通知トリガー条件:**
- レコードの Insert/Update 時
- 特定フィールドの変更時
- イベント発生時 (gs.eventQueue())

**通知テンプレート変数:** `${field_name}` でフィールド値を本文に挿入

## 11. グループ詳細

**グループタイプ:**
- Assignment Group: タスクの担当グループ
- Notification Group: 通知の送信先グループ
- 両方兼用も可

**ロール継承:** グループに付与したロールはメンバー全員に継承される

**Contains Roles:** ロールが別のロールを包含する（例: admin は itil を含む）

**Manager:** グループのマネージャーフィールド。承認フローで参照されることがある

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
              └── What contains (件名 / 本文 / 変数テンプレート ${field_name})

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

【Client Script の種類と g_form API】

  onLoad  ──→ フォーム読込時
  onChange ──→ フィールド変更時 (fieldName, newValue, oldValue)
  onSubmit ──→ 保存前
  onCellEdit ──→ リストのインライン編集時

  g_form.getValue / setValue / setMandatory / setVisible / setReadOnly

【Performance Analytics 構造】

  Indicator (KPI定義)
    └── Scheduled Job (データ収集)
          └── Score (実測値)
                ├── Target (目標値)
                └── Threshold (閾値)

  Breakdown ──→ Indicatorをセグメント分解
  Scorecard / Widget ──→ ダッシュボードに表示

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

### タスク2: Client Scriptを作成してg_form APIを試す

1. **All → System Definition → Client Scripts** を開く
2. 「New」をクリック。Table: `incident`、Type: `onChange`、Field name: `priority` を指定
3. Script 欄に以下を入力して保存:
   ```
   function onChange(control, oldValue, newValue, isLoading) {
     if (newValue == '1') {
       g_form.setMandatory('short_description', true);
       g_form.addInfoMessage('優先度1: 説明を必ず入力してください');
     } else {
       g_form.setMandatory('short_description', false);
       g_form.clearMessages();
     }
   }
   ```
4. Incidentフォームを開き、Priority を「1 - Critical」に変更して動作を確認する

### タスク3: 通知(Notification)の3要素を確認する

1. **All → System Notification → Email → Notifications** を開く
2. 既存の通知（例: `Incident opened for user`）をクリックして開く
3. 以下の3タブを順に確認する:
   - **When to send** タブ: 送信条件（テーブル名・条件フィルター・イベント）
   - **Who will receive** タブ: 受信者（Users / Groups / フィールド値）
   - **What it will contain** タブ: 件名と本文テンプレート（`${field_name}` 変数）
4. **確認**: 「Send to event creator」チェックボックスの位置と意味を把握する

### タスク4: ナレッジベースの記事を作成し公開フローを体験する

1. **All → Knowledge → Knowledge Bases** を開き、「New」でナレッジベースを作成する（Title: `CSA Practice KB`）
2. **All → Knowledge → Articles** を開き、「New」をクリック
3. Knowledge Base に `CSA Practice KB` を指定し、Title と本文を入力して **Save** する（状態: Draft）
4. レコード上部の **Submit for Review** ボタンをクリック → 状態が `Review` に変わることを確認
5. **Publish** ボタンをクリック → 状態が `Published` になることを確認

### タスク5: Visual Task Boardを3種類作成して違いを体験する

1. **All → Visual Task Board** を開き、「New Board」をクリック
2. **Guided** を選択し、テーブルに `incident`、レーンフィールドに `State` を指定して作成する
3. カードを別レーンにドラッグし、インシデントの State フィールドが自動変更されることを確認する
4. 再度「New Board」→ **Freeform** を選択し、ボード上で直接カードを追加してみる（テーブルレコードと紐づかない点を確認）

## 12. UI Actions

フォーム上のボタン・コンテキストメニュー・関連リンクをカスタマイズする仕組み（テーブル: sys_ui_action）。

**種類:**
- `Form button`: フォーム上部のボタン
- `Form context menu`: 右クリックメニュー
- `Form link`: フォーム下部の関連リンク
- `List banner button`: リスト上部のボタン
- `List context menu`: リストの右クリックメニュー

**UI ActionとACLの関係:**
- UI Actionの表示制御はACLの `execute` Operationで行う
- UI Policy / Client Script との違い: UI Actionはサーバーサイド処理のトリガー

**Client Script との使い分け:**
- Client Script: フォームの表示制御（フィールドの必須/表示/読み取り専用）
- UI Action: ボタンクリック時のサーバーサイド処理実行

## 13. Inbound Email Actions

受信メールをトリガーにレコードを作成・更新するルール（テーブル: sys_email_action）。

**動作フロー:**
受信メール → メールボックス → Inbound Email Action → レコード作成/更新

**主な設定:**
- `When to run`: 条件（新規メール / 既存チケットへの返信）
- `Action`: insert（新規作成）/ update（更新）/ ignore
- `Target table`: 操作対象テーブル（例: incident）
- `Reply separator`: 返信メールの本文区切り文字

**典型的な使用例:**
- ユーザーがメール送信 → Incidentが自動作成
- 担当者がメール返信 → Work Notesに自動追記

## 試験との接続

「ロールをユーザーに直接付与するのとグループ経由で付与するのはどちらが推奨か」→ グループ経由が推奨。1か所の変更が全メンバーに波及するため管理が効率的。

「通知の受信者をフィールド値（例: Assigned to）で指定するにはどこで設定するか」→ Notificationの「Who will receive」タブの「Fields」欄でテーブルのユーザー型フィールドを指定する。

「ナレッジ記事の Can Read と Can Contribute は何で制御するか」→ User Criteria で制御する。ロールや部署単位でのアクセス制御。

「Guided VTBでカードを移動すると何が起きるか」→ 背後のレコードのフィールド値（例: State）が自動変更される。

「ReportとPerformance Analyticsの用途の違いは何か」→ Reportはスナップショット（今のデータ）、PAはトレンド（経時変化）。

「onChangeスクリプトでフィールドを必須にするAPIはどれか」→ g_form.setMandatory('field', true)。

「Client ScriptとUI Policyはどちらが先に試みるべきか」→ UI Policyを先に試みる（コード不要で保守しやすい）。複雑な条件がある場合のみClient Scriptを使う。
