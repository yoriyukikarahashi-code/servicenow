# 分野4: Self-Service & Automation(配点 20%)

## 1. サービスカタログ(Service Catalog)

エンドユーザーが商品・サービスを「注文」するセルフサービスの入口。

| 要素 | 内容 |
|------|------|
| **Catalog** | カタログの最上位コンテナ(複数カタログ可。例: IT / HR / 施設) |
| **Category** | カタログ内の分類。入れ子可 |
| **Catalog Item** | 注文可能な項目(PC、アクセス権など) |
| **Record Producer** | カタログUIから**任意のテーブルにレコードを直接作成**する特殊アイテム(例: インシデント起票フォーム) |
| **Order Guide** | 複数アイテムを**1回の注文でまとめて依頼**(例: 新入社員セット)。ルールベースでアイテム出し分け |
| **Variables** | アイテムの入力項目(単一行テキスト、選択、参照など) |
| **Variable Set** | 変数の再利用可能なまとまり(複数アイテムで共有) |

- **注文後のレコード構造(頻出)**: 注文すると **Request(REQ / `sc_request`)** が作られ、その下にアイテムごとの **Requested Item(RITM / `sc_req_item`)**、さらに作業単位の **Catalog Task(SCTASK / `sc_task`)** がぶら下がる。
- カタログアイテムには **Catalog UI Policy / Catalog Client Script** で入力制御を付けられる。
- アイテムの公開制御は **User Criteria**(Available for / Not available for)。

## 2. Service Portal / Employee Center

- **Service Portal**: ウィジェットベースのセルフサービスポータル。カタログ・ナレッジ・チケット照会等を提供。
- **Employee Center**: 部門横断(IT/HR/施設等)の統合ポータル(新しい標準)。
- ポータルはページ+ウィジェットで構成され、ブランディングを個別に設定できる。

## 3. ナレッジ・Virtual Agent によるセルフサービス

- ポータル検索でナレッジ記事・カタログアイテムを横断検索 → チケット起票前に自己解決(**チケット削減=Deflection**)。
- **Virtual Agent**: チャットボット。定型の会話フロー(トピック)で問い合わせを自動処理。

## 4. Flow Designer(CSA自動化の中心)

コードを書かずにプロセスを自動化するツール。旧Workflowの後継。

| 概念 | 内容 |
|------|------|
| **Flow** | トリガー+アクションの並び(自動化プロセス全体) |
| **Trigger** | 起動条件: **Record(作成/更新)/ Schedule(日時)/ Application(カタログ注文等)** |
| **Action** | 個々の処理(レコード更新、承認依頼、通知送信など)。再利用可能 |
| **Subflow** | トリガーを持たない再利用可能なフロー部品(他フローから呼び出し) |
| **Spoke** | アクションのまとまり(アプリ/外部サービス単位のコネクタ。例: Slack spoke) |

- **Data Pill**: 前のステップの出力値をドラッグで後続ステップに渡す仕組み。ドット表記の展開も可能。
- フローは**テスト実行**でき、実行履歴(コンテキスト)で各ステップの入出力を確認できる。
- 承認は「**Ask for Approval**」アクション。承認結果で分岐できる。

## 5. 承認(Approvals)

- 承認レコードは `sysapproval_approver`。ユーザーは My Approvals から承認/却下。
- 承認の仕掛けは Flow Designer(推奨)や旧Workflowで構成。
- メールから直接承認可能な設定もある(メール返信・承認リンク)。

## 6. SLA(Service Level Agreement)

- **SLA Definition** で対象テーブル・開始/停止/一時停止条件・目標時間を定義。
- 実行中のSLAは **Task SLA**(`task_sla`)レコードとして各タスクに付く。
- **Retroactive Start**: 過去の時点(例: 作成日時)に遡って計時を開始するオプション。
- SLAの経過に応じてエスカレーション処理(通知等)を **SLA Workflow / Flow** で実行できる。

## 7. Assignment(自動割当)

- **Assignment Rules**: 条件一致で Assignment group / Assigned to を設定(テーブル単位、最初に一致した1つが適用)。
- データルックアップ(Data Lookup)でフィールド値に基づく優先度等の自動設定も可能(例: Priority Lookup)。

---

## 頻出ポイント

- **REQ → RITM → SCTASK** の親子関係(注文1回=REQ1つ、アイテムごとにRITM)
- Record Producer は「任意テーブルへのレコード作成」/ Order Guide は「複数アイテム一括注文」
- Variable Set の再利用性
- Flow / Subflow / Action / Spoke / Trigger の区別
- SLA の Retroactive Start
- User Criteria によるカタログ・ナレッジの公開制御
