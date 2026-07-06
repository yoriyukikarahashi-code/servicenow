# 分野4: Self-Service & Automation(配点 20%)

## 1. サービスカタログ(Service Catalog)

Catalog > Category > Catalog Item の階層。注文するとREQ(Request) > RITM(Requested Item) > SCTASK(Catalog Task)の親子構造が作られる。Record Producerは任意テーブルへのレコード直接作成。Order Guideは複数アイテム一括注文。Variable Setで変数を再利用。

## 2. Service Portal / Employee Center

ウィジェットベースのセルフサービスポータル。Employee Centerが新標準。

## 3. Flow Designer

トリガー(Record/Schedule/Application) + Action の並び。Subflowはトリガーなしの再利用部品。Spokeはアプリ/外部サービス単位のコネクタ。Data Pillで前ステップの値を後続に渡す。

## 4. 承認(Approvals)

Ask for Approvalアクションで承認依頼。sysapproval_approverテーブルに記録。

## 5. SLA

SLA Definitionで開始/停止/一時停止条件と目標時間を定義。Task SLA(task_sla)レコードとして各タスクに付く。**Retroactive Start**: SLAが適用される前からStart Conditionを満たしていた場合、その条件を最初に満たした時点(Set start toで指定したフィールド、通常は作成日時)まで遡って計時を開始する。OFF(デフォルト)ならSLAレコード生成時点から計時。

## 6. Assignment(自動割当)

Assignment Rulesで条件一致時にAssignment group/Assigned toを自動設定。

## 全体構造マップ

```
【ユーザーの入口】
  Service Portal / Employee Center
        ↓ アクセス
  ┌─────────────────────────────────┐
  │        Service Catalog          │
  │  sc_catalog (カタログ)          │
  │    └─ sc_category (カテゴリ)    │
  │         └─ sc_cat_item (アイテム)│
  │              └─ Variable / Variable Set │
  └─────────────────────────────────┘
        ↓ 注文(Order)
  REQ (sc_request)
    └─ RITM (sc_req_item)
         └─ SCTASK (sc_task)
                ↓ トリガー
  ┌─────────────────────────────────────┐
  │           Flow Designer             │
  │  ┌──────────┐   ┌────────────────┐  │
  │  │ Trigger  │──▶│ Action Step 1  │  │
  │  │(Record/  │   │  (Ask for      │  │
  │  │ Schedule)│   │   Approval)    │  │
  │  └──────────┘   └───────┬────────┘  │
  │                         │ Data Pill  │
  │                   ┌─────▼────────┐  │
  │                   │ Action Step 2 │  │
  │                   │ (Create Task) │  │
  │                   └──────────────┘  │
  │  Subflow (トリガーなし・再利用部品)  │
  │  Spoke  (外部サービス連携単位)      │
  └─────────────────────────────────────┘

  Record Producer → 対象テーブルへ直接 (REQ/RITMなし)
  Order Guide     → 複数アイテムを束ねて一括注文

【SLA フロー】
  SLA Definition
    ├── Start condition  → 計時開始
    ├── Pause condition  → 一時停止
    ├── Stop condition   → 計時終了
    └── Retroactive Start → 過去時点から計時

  → Task SLA (task_sla) として各レコードに付く
```

## PDI 操作ガイド

**タスク1: カタログアイテムを作成して注文する**

1. `All → Service Catalog → Catalog Definitions → Maintain Items` を開く
2. `New` をクリック。Name に「テスト貸出PC」、Catalogs に「Service Catalog」、Category に任意のカテゴリを設定して保存
3. 関連リスト `Variables` で `New` をクリック。Type を `Single Line Text`、Question を「用途を記入してください」として保存
4. `Try It` ボタンで注文を実行
5. `All → Service Catalog → Open Records → Requests` を開き、生成されたREQ/RITM/SCTASKの親子構造を確認する

**タスク2: Record Producerを作成する**

1. `All → Service Catalog → Catalog Definitions → Record Producers` を開く
2. `New` をクリック。Name に「インシデント報告フォーム」、Table に `incident` を選択して保存
3. Variables タブで `New` → Short Description 用の変数を作成し、Script タブで `current.short_description = producer.変数名;` と記述
4. Service Portal でフォームを検索・送信し、`All → Incident → All` に新規インシデントが作成されたことを確認する
   - 確認ポイント: REQやRITMは生成されず、incidentテーブルに直接レコードが作られること

**タスク3: Flow Designer でApprovalフローを作成する**

1. `All → Flow Designer` を開き、`New → Flow` をクリック
2. Flow Name に「PC承認フロー」と入力し、`Add a trigger → Record → Created` を選択。Table は `sc_req_item` を指定
3. `Add an Action → ServiceNow Core → Ask for Approval` を選択
4. Activate してカタログアイテムを注文し、`All → My Approvals` に承認依頼が届いていることを確認する

**タスク4: SLA Definitionを作成して動作を確認する**

1. `All → SLA → SLA Definitions → New` を開く
2. Name に「RITM 2時間SLA」、Table に `sc_req_item`、Duration に `2 Hours` を設定
3. Start condition を `State is Open`、Stop condition を `State is Closed Complete` に設定して保存
4. カタログアイテムを注文し、生成されたRITMを開く
5. 関連リスト `SLAs` を確認し、Task SLA(task_sla)レコードが生成されていること、および残り時間が計時されていることを確認する

## Catalog UI Policy / Catalog Client Script

カタログアイテム専用の UI Policy / Client Script。**通常のものとは別テーブルで管理される。**

**Catalog UI Policy（catalog_ui_policy）:**
- 適用対象: サービスカタログのフォームのみ
- 通常のUI Policy（sys_ui_policy）はカタログフォームに効かない
- 設定場所: カタログアイテムレコードの「Catalog UI Policies」関連リスト
- Variable（変数）に対して必須/表示/読み取り専用を制御

**Catalog Client Script（catalog_script_client）:**
- 適用対象: サービスカタログのフォームのみ
- 通常のClient Script（sys_script_client）はカタログフォームに効かない
- 種類: onLoad / onChange / onSubmit（カタログ専用）
- `g_form` APIは同様に使用可能

**なぜ別物か:**
カタログアイテムのフォームはVariableで構成されており、通常のテーブルフィールドとは異なる仕組みのため。

## SLA Business Time（就業時間スケジュール）

SLAの計時が就業時間のみか24時間かを制御する設定。

**Schedule フィールド:**
- `8-5 weekdays` などのスケジュールを指定
- SLAは就業時間内のみカウントされる（営業時間外は一時停止）
- 未指定の場合は24時間365日でカウント

**Timezone:** SLAの計時に使うタイムゾーンを指定可能

## 試験との接続

「Record ProducerとCatalog Itemの違いは何か」→ Record Producerは任意テーブルへ直接レコード作成。REQ/RITMは生成されない。

「注文後に作成されるレコードの親子関係はどれか」→ REQ(sc_request) > RITM(sc_req_item) > SCTASK(sc_task)。

「Flow DesignerのSubflowとFlowの違いは何か」→ SubflowはTriggerを持たない。Flowから呼び出す再利用部品。

「SLAが一時停止(Pause)するのはどの条件が設定されている場合か」→ Pause condition フィールドに条件が設定されている場合。Start/Stop/Pauseは独立したフィールド。

「Variable Setを使う主な目的はどれか」→ 変数の定義を1か所で管理して複数アイテムに再利用するため。
