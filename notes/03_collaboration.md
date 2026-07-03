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

**PA Breakdowns (分解):**
- Indicatorのデータを切り口で分解（例: Priority別、Assignment Group別）

**PA Scheduled Jobs:**
- Indicatorのデータを定期収集するジョブ

**Scores / Targets / Thresholds:**
- Score: 実測値 / Target: 目標値 / Threshold: アラート閾値

## 10. 通知詳細

**Notification Digest:** 複数の通知をまとめてバッチ送信

**Notification Subscriptions:** ユーザーが通知のオン/オフを自分で設定

**Notification Devices:** Email / SMS / Push Notification

**通知テンプレート変数:** ${field_name} でフィールド値を本文に挿入

## 11. グループ詳細

**グループタイプ:** Assignment Group / Notification Group / 両方兼用

**ロール継承:** グループに付与したロールはメンバー全員に継承される

**Contains Roles:** ロールが別のロールを包含する（例: admin は itil を含む）

## 全体構造マップ

```
【ユーザー管理の3層構造】

  sys_user (ユーザー)
    └─ 所属 ──→ sys_user_group (グループ)
                    └─ 付与 ──→ sys_user_role (ロール)
                                    └─ 制御 ──→ ACL / Application Access

【タスク継承ツリー】
  task (親テーブル)
    ├── incident
    ├── problem
    ├── change_request
    └── sc_request → sc_req_item

【通知フロー】
  トリガー条件 → Notification
    ├── When to send
    ├── Who receives
    └── What contains (${field_name} テンプレート)

【Client Script の種類と g_form API】
  onLoad / onChange / onSubmit / onCellEdit
  g_form.getValue / setValue / setMandatory / setVisible / setReadOnly

【Performance Analytics 構造】
  Indicator → Scheduled Job → Score → Target/Threshold
  Breakdown → セグメント分解 → Scorecard/Widget

【レポート vs PA】
  Report: 現時点スナップショット
  PA: 時系列トレンド分析
```

## PDI 操作ガイド

### タスク1: Client Scriptを作成してg_form APIを試す

1. **All → System Definition → Client Scripts** を開く
2. 「New」をクリック。Table: `incident`、Type: `onChange`、Field name: `priority` を指定
3. Script 欄に以下を入力して保存:
   - onChange時にpriority=1なら short_description を必須化し、メッセージを表示
4. Incidentフォームを開き、Priority を「1 - Critical」に変更して動作を確認する

### タスク2: 通知(Notification)の3要素を確認する

1. **All → System Notification → Email → Notifications** を開く
2. 既存の通知を開き、When to send / Who will receive / What it will contain の3タブを確認する
3. 「Send to event creator」チェックボックスの位置と意味を把握する

### タスク3: ナレッジベースの記事を作成し公開フローを体験する

1. **All → Knowledge → Knowledge Bases** を開き、新規KBを作成する
2. 記事を新規作成し、Draft → Submit for Review → Publish のフローを体験する
3. User Criteria で Can Read を設定して閲覧制限を確認する

### タスク4: Visual Task Boardを3種類確認する

1. **All → Visual Task Board** を開き「New Board」をクリック
2. Guided を選択し、incidentテーブル、StateフィールドでVTBを作成する
3. カードをドラッグするとStateが自動変更されることを確認する

## 試験との接続

「ロールをグループ経由で付与するのがなぜ推奨か」→ 1か所の変更が全メンバーに波及するため管理が効率的。

「通知のWho will receiveでフィールド値(例: Assigned to)を指定するには」→ Notificationの「Who will receive」タブの「Fields」欄で指定する。

「Guided VTBでカードを移動すると何が起きるか」→ 背後のレコードのフィールド値(例: State)が自動変更される。

「onChangeスクリプトでフィールドを必須にするAPIはどれか」→ g_form.setMandatory('field', true)。

「Client ScriptとUI Policyはどちらが先に試みるべきか」→ UI Policyを先に試みる（コード不要で保守しやすい）。

「ReportとPerformance Analyticsの違いは」→ Reportはスナップショット、PAはトレンド（時系列）分析。
