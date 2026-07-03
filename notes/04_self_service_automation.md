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

SLA Definitionで開始/停止/一時停止条件と目標時間を定義。Task SLA(task_sla)レコードとして各タスクに付く。Retroactive Startで過去時点から計時開始。

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
  │              └─ Variable / Variable Set (item_option_new) │
  └─────────────────────────────────┘
        ↓ 注文(Order)
  REQ (sc_request)
    └─ RITM (sc_req_item)  ←── Record Producerもここに関与
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
  │                   │ (Create Task/ │  │
  │                   │  Send Email)  │  │
  │                   └──────────────┘  │
  │  Subflow (トリガーなし・再利用部品)  │
  │  Spoke  (外部サービス連携単位)      │
  └─────────────────────────────────────┘
        ↓ 承認フロー発生時
  sysapproval_approver (承認レコード)
    └─ 承認者: sys_user
        ↓ 承認完了後、タスク割当
  Assignment Rules
    └─ 条件一致 → sc_task.assignment_group / assigned_to を自動設定
        ↓ 作業開始と同時に計時
  SLA Definition (agreement_service_level)
    └─ Task SLA (task_sla) ── 各RITMやタスクに1対多で付く
         ├─ 開始条件 (Start condition)
         ├─ 停止条件 (Stop condition)
         ├─ 一時停止条件 (Pause condition)
         └─ Retroactive Start → 過去時点から計時

【Order Guideの位置付け】
  Order Guide (sc_cat_item_guide)
    └─ 複数の sc_cat_item を束ねて一括注文
         └─ 各アイテムが個別のRITMを生成
```

## PDI 操作ガイド

**タスク1: カタログアイテムを作成して注文する**

1. `All → Service Catalog → Catalog Definitions → Maintain Items` を開く
2. `New` をクリック。Name に「テスト貸出PC」、Catalogs に「Service Catalog」、Category に任意のカテゴリを設定して保存
3. 関連リスト `Variables` で `New` をクリック。Type を `Single Line Text`、Question を「用途を記入してください」として保存
4. `Try It` ボタン(または Service Portal からアイテムを検索)して注文を実行
5. `All → Service Catalog → Open Records → Requests` を開き、生成されたREQ/RITM/SCTASKの親子構造を確認する
   - 確認ポイント: RITMのVariables タブに入力した値が記録されていること

**タスク2: Record Producerを作成する**

1. `All → Service Catalog → Catalog Definitions → Record Producers` を開く
2. `New` をクリック。Name に「インシデント報告フォーム」、Table に `incident` を選択して保存
3. Variables タブで `New` → Short Description 用の変数を作成し、Script タブで `current.short_description = producer.変数名;` と記述
4. Service Portal でフォームを検索・送信し、`All → Incident → All` に新規インシデントが作成されたことを確認する
   - 確認ポイント: REQやRITMは生成されず、incidentテーブルに直接レコードが作られること

**タスク3: Flow Designer でApprovalフローを作成する**

1. `All → Flow Designer` を開き、`New → Flow` をクリック
2. Flow Name に「PC承認フロー」と入力し、`Add a trigger → Record → Created` を選択。Table は `sc_req_item` を指定
3. `Add an Action → ServiceNow Core → Ask for Approval` を選択。Record に Data Pill でトリガーレコードを設定。Approvers に自分のユーザーを追加
4. `Approved` 分岐の下に `Update Record` アクションを追加し、RITMのStateを `Approved` に変更する設定を加える
5. Activate してカタログアイテムを注文し、`All → My Approvals` に承認依頼が届いていることを確認する
   - 確認ポイント: sysapproval_approver テーブルに承認レコードが生成されていること

**タスク4: SLA Definitionを作成して動作を確認する**

1. `All → SLA → SLA Definitions → New` を開く
2. Name に「RITM 2時間SLA」、Table に `sc_req_item`、Duration に `2 Hours` を設定
3. Start condition を `State is Open`、Stop condition を `State is Closed Complete` に設定して保存
4. カタログアイテムを注文し、生成されたRITMを開く
5. 関連リスト `SLAs` を確認し、Task SLA(task_sla)レコードが生成されていること、および残り時間が計時されていることを確認する
   - 確認ポイント: Retroactive Start のチェックボックスの有無でカウント開始時刻が変わること

**タスク5: Assignment Ruleを作成する**

1. `All → Incident → Assignment Lookup Rules → New` を開く(またはナビゲーターで`assignment` と検索)
2. Table に `sc_task`、条件を「Priority is 1 - Critical」に設定
3. Assignment group に任意のグループを割り当てて保存
4. 優先度1のSCTASKを手動作成または注文経由で生成し、Assignment group が自動設定されることを確認する
   - 確認ポイント: ルールの優先度(Order)が低い数値のものが先に適用されること

## 試験との接続

「Record ProducerとCatalog Itemの違いは何か」→ PDIでRecord Producerを作成してincidentテーブルに送信すると、REQ/RITMが生成されず対象テーブルに直接レコードが作られることを目で見て確認できるため、「任意テーブルへの直接作成」という定義が体感として定着する。

「注文後に作成されるレコードの親子関係はどれか」→ PDIでカタログアイテムを注文した後にREQ/RITM/SCTASKをナビゲーターから個別に開くと、それぞれの Reference フィールド(request、req_item)が上位レコードを指していることが確認でき、親子の方向と各テーブル名(sc_request, sc_req_item, sc_task)がセットで記憶できる。

「Flow DesignerのSubflowとFlowの違いは何か」→ PDIでSubflowを新規作成する画面を開くと、Trigger の選択肢が存在しないことに気づく。この「トリガーを持てない＝単独では起動しない再利用部品」という特徴をUI上で直接確認することで、試験の選択肢で混乱しなくなる。

「SLAが一時停止(Pause)するのはどの条件が設定されている場合か」→ PDIでSLA Definitionを開き、Pause conditionフィールドを確認すると、Start/Stop/Pauseが独立した条件フィールドとして分かれていることがわかる。実際にRITMのStateを変えながらtask_slaレコードの`Paused`フラグと`Business elapsed percentage`の変化を観察すると、一時停止の仕組みが直感的に理解できる。

「Variable Setを使う主な目的はどれか」→ PDIで同一のVariable Setを複数のCatalog Itemに関連付ける操作を行うと、変数の定義を1か所で管理して複数アイテムに再利用できることを実際の画面で確認できるため、「再利用・一元管理」という解答の根拠が明確になる。
