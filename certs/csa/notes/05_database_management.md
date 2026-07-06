# 分野5: Database Management(配点 27%・最重要)

## 1. データスキーマの基本

全テーブル定義はsys_db_object。フィールド定義(辞書)はsys_dictionary。ラベルはsys_documentation。sys_idは32文字GUIDで全レコードに存在。

**sys_db_objectの主要フィールド:**
- `name`: テーブルの物理名（例: incident）
- `label`: 表示名（例: Incident）
- `super_class`: 親テーブル（Extends）
- `is_extendable`: 子テーブルを作れるか
- `accessible_from`: アクセス可能なスコープ

**Application Access（ACLとは別レイヤー）:**
- sys_db_objectの「Application Access」タブで設定
- `Can read` / `Can create` / `Can update` / `Can delete` を他スコープに許可するか制御
- ACLはレコード単位の権限、Application Accessはスコープ間のアクセス許可
- スコープドアプリからGlobalテーブルを操作するにはApplication Accessが必要

**テーブル作成方法:**
- Studio（スコープドアプリ開発）
- sys_db_object.list → New（グローバル）
- Schema Map（視覚的なリレーション確認・作成）

## 2. テーブルの拡張(継承)

taskがIncident/Problem/Change等の親。cmdb_ciがCI系の親。sys_userはtask継承ツリーとは無関係の独立した系統(taskの拡張ではない)。親のリストには子のレコードも表示される。新規テーブルにはu_プレフィックス。

## 3. フィールドタイプと参照

Reference(1対多)、List(複数参照)、Choice(sys_choiceで管理)。Dot-walkingで参照先フィールドにアクセス(例: caller_id.company.name)。

## 4. リレーションシップ

1対多=Reference、多対多=m2mテーブル、Database View=JOIN(読み取り専用)。

## 5. CMDB

CI基底テーブルはcmdb_ci。CIリレーションシップはcmdb_rel_ciテーブル。

## 6. ACL(アクセス制御) — 最頻出

評価順序: テーブルレベル(具体→親→ワイルドカード)→フィールドレベル(具体→ワイルドカード)。両方パスしてアクセス可能。ACL変更にはsecurity_adminへのelevate roleが必要。条件3種類: ロール/条件(フィルター)/スクリプト。

**ACL Operation種類（必須）:**
- `read`: レコード/フィールドの読み取り
- `write`: 既存レコードのフィールド更新
- `create`: 新規レコードの作成
- `delete`: レコードの削除
- `execute`: UI Actionの実行（ボタン・コンテキストメニュー専用）
- `report`: レポートでのテーブル使用

**ACLのデフォルト動作（最重要・試験頻出）:**
- テーブルにACLが**1件も存在しない** → **アクセス許可**（デフォルト許可）
- ACLが存在するが**条件を1つも満たさない** → **アクセス拒否**
- ACLが存在し**いずれか1つを満たす** → **アクセス許可**
- ※「ACLがないから安全」は誤り。ACLを作った瞬間に他のACLを満たさないユーザーは拒否される

**ACLスクリプトフィールド:**
- `answer` 変数に `true` または `false` をセットして返す
- `current` でカレントレコードを参照
- `gs.hasRole('role')` でロールチェック
- `answer = true;` でアクセス許可

**ACL条件の評価（AND条件）:**
- ロール / 条件(フィルター) / スクリプト の**3つすべてがtrueのときのみACL通過**
- いずれか1つでもfalseなら拒否

**admin ロール:** ACLを無条件でバイパス（管理者は全ACLを通過）

**行レベルセキュリティ（Row-Level Security）:**
- テーブルACLのConditionやScriptで `current` を使うことでレコード単位のアクセス制御が可能
- 例: `current.caller_id == gs.getUserID()` → 自分が登録したレコードのみ読める

## 7. UI Policy / Data Policy / Business Rule

UI Policy=フォームのみ。Data Policy=全入力経路(インポート・API含む)。Business Ruleはサーバーサイドのinsert/update/delete/queryロジック。

## 8. Business Rule 詳細

**実行タイミング(When):**
- `Before`: DB保存前に実行。フィールド値の変更や処理のアボートに使用
- `After`: DB保存後に実行。他レコードの更新などに使用
- `Async`: 非同期実行。メール送信など重い処理に使用
- `Display`: フォーム表示前に実行。スクラッチパッドでデータを渡す

**current オブジェクト:**
- `current.field_name`: フィールドの現在値を取得/設定
- `current.getValue('field')`: 文字列として取得
- `current.setValue('field', value)`: 値をセット

**previous オブジェクト:**
- `previous.field_name`: 更新前の古い値を参照（Beforeのupdate時のみ有効）
- `previous.state`: 変更前のstateフィールド値

**setAbortAction(true):**
- `current.setAbortAction(true)`: DB保存をアボートしロールバック
- `gs.addErrorMessage('メッセージ')`: ユーザーへエラーメッセージ表示
- 組み合わせてバリデーションロジックを実装:
  ```
  if (current.state == '3' && current.assigned_to.nil()) {
    current.setAbortAction(true);
    gs.addErrorMessage('担当者を指定してください');
  }
  ```

**Scratchpad オブジェクト:**
- `g_scratchpad.key = value`: Display Business RuleからClient Scriptにデータを渡す

## 9. GlideRecord API

サーバーサイドでテーブルを操作するJavaScript API。

**単一レコード取得:**
```
var gr = new GlideRecord('incident');
gr.get('sys_id_value');
// または
gr.get('number', 'INC0000001');
```

**クエリ実行:**
```
var gr = new GlideRecord('incident');
gr.addQuery('state', '1');              // state = 1
gr.addQuery('priority', '<', '3');      // priority < 3
gr.addEncodedQuery('active=true^state=1'); // エンコードクエリ
gr.setLimit(10);                        // 件数制限
gr.orderBy('priority');                 // 昇順
gr.orderByDesc('sys_created_on');       // 降順
gr.query();
while (gr.next()) {
  // レコード処理
  var val = gr.getValue('short_description'); // 文字列取得
  var disp = gr.getDisplayValue('state');     // 表示値取得
}
```

**OR条件:**
```
var qc = gr.addQuery('state', '1');
qc.addOrCondition('state', '2');   // state=1 OR state=2
```

**レコード操作:**
```
var gr = new GlideRecord('incident');
gr.initialize();
gr.setValue('short_description', '新規インシデント');
var sysId = gr.insert();           // 作成。sys_idを返す

// 更新
gr.get(sysId);
gr.setValue('state', '2');
gr.update();

// 削除
gr.deleteRecord();
```

**参照フィールドのトラバース:**
```
gr.caller_id.getRefRecord();  // 参照先レコードを取得
gr.getValue('caller_id.email'); // dot-walkで値取得
```

## 10. テーブルと辞書の詳細

**Auto Number (自動番号):**
- Prefix: 番号のプレフィックス（例: INC）
- Next value: 次に付与される数値
- Padding: 桁数（0埋め）

**Dictionary Entry の主なフィールド:**
- Type: 文字列/整数/日付/Reference等
- Max length: 最大文字数
- Default value: デフォルト値
- Mandatory: 必須フラグ

**Reference フィールド:**
- Reference qualifier: 参照先レコードを絞り込む条件スクリプト

**Choice リスト:**
- sys_choice テーブルで管理
- Dependent field: 別フィールドの値に連動して選択肢を絞り込む

**テーブル継承:**
- Extends table: 親テーブルを指定
- 親フィールドは子テーブルに自動的に継承
- sys_metadata: 全設定レコードの基底テーブル

**辞書オーバーライド:**
- 子テーブルだけフィールド属性を変更（親の定義はそのまま）
- 例: 子テーブルでshort_descriptionを必須化

## 11. Script Include

サーバーサイドで再利用可能なスクリプトライブラリ（テーブル: sys_script_include）。

**特徴:**
- Business RuleやFlow Designerから呼び出して使う
- ClientCallable: trueにするとクライアントスクリプトからも呼び出し可能
- Application Scopeに紐づく

**基本構造:**
```
var MyUtils = Class.create();
MyUtils.prototype = {
  initialize: function() {},
  
  myMethod: function(param) {
    var gr = new GlideRecord('incident');
    gr.addQuery('state', param);
    gr.query();
    return gr.getRowCount();
  },
  
  type: 'MyUtils'
};
```

**呼び出し方（Business Ruleから）:**
```
var util = new MyUtils();
var count = util.myMethod('1');
```

## 12. GlideAggregate API

COUNT/SUM/AVG等の集計を効率的に実行するAPI（GlideRecordより高速）。

```
var ga = new GlideAggregate('incident');
ga.addQuery('active', 'true');
ga.addAggregate('COUNT');           // 件数カウント
ga.groupBy('priority');             // 優先度別に集計
ga.query();
while (ga.next()) {
  var priority = ga.getValue('priority');
  var count = ga.getAggregate('COUNT');
  gs.info('Priority ' + priority + ': ' + count);
}
```

**GlideRecord vs GlideAggregate:**
- GlideRecord: レコードの中身を処理したいとき
- GlideAggregate: 件数・合計・平均だけ知りたいとき（全レコード取得不要）

## 13. GlideSystem (gs) API まとめ

`gs` オブジェクトはサーバーサイドスクリプト全般で使用可能。

**ユーザー情報:**
- `gs.getUserID()`: 現在ユーザーのsys_id
- `gs.getUserName()`: ユーザーID（login名）
- `gs.getUser().getFullName()`: フルネーム
- `gs.hasRole('role')`: ロール保持確認（trueなら保持）

**メッセージ:**
- `gs.addInfoMessage('msg')`: 情報メッセージ表示
- `gs.addErrorMessage('msg')`: エラーメッセージ表示
- `gs.info('msg')` / `gs.warn('msg')` / `gs.error('msg')`: ログ出力（推奨）
- `gs.log()`: 旧来のログAPI（**非推奨**。試験では gs.info() が正解になることが多い）

**システム情報:**
- `gs.getProperty('property.name')`: System Propertyの値取得
- `gs.nowDateTime()`: 現在日時（GMT）
- `gs.eventQueue('event.name', current)`: イベントキューに追加

## 14. Journal フィールド（Work Notes / Comments）

**フィールドタイプ: journal / journal_input**
- `work_notes`: 内部メモ（担当者のみ）
- `comments` (Additional Comments): 顧客向け追記
- **追記式**: 既存内容は変更不可、新しい内容が上に追加される
- **読み取り専用**: 過去のエントリーは編集・削除不可
- **sys_journal_field**: Journalフィールドの内容を格納するテーブル

## 15. 監査・辞書オーバーライド

**Auditing**: sys_auditに変更履歴を記録（テーブルごとに有効化必要）。

**辞書オーバーライド**: 子テーブルだけ属性変更（親の定義は変えない）。

## 全体構造マップ

```
【スキーマ層】
  sys_db_object(テーブル定義)
      │
      ├──→ sys_dictionary(フィールド定義・辞書)
      │         │
      │         └──→ sys_documentation(ラベル・翻訳)
      │
      └──→ sys_choice(Choiceフィールドの選択肢)

【テーブル継承ツリー】
  task(親)
    ├── incident
    ├── problem
    └── change_request

  cmdb_ci(親)
    ├── cmdb_ci_computer
    ├── cmdb_ci_server
    └── cmdb_ci_appl

  sys_user ── (task継承ツリーとは無関係の独立系統)

【アクセス制御層】
  リクエスト
      ↓
  ACL評価(テーブルレベル)
      具体テーブル名 → 親テーブル名 → *(ワイルドカード)
      ↓ パス
  ACL評価(フィールドレベル)
      具体フィールド名 → *(ワイルドカード)
      ↓ パス
  アクセス許可
      ↓ どちらか失敗
  アクセス拒否

  ACL条件の評価順序:
    ロールチェック → 条件(フィルター) → スクリプト(answer=true/false)
    ※すべての条件がtrueの場合のみACL通過
    ※admin ロールはACLをバイパス

【Business Rule タイミング】
  Before  ── DB保存前 ── current変更・setAbortAction・バリデーション
  After   ── DB保存後 ── 他レコード更新・後処理
  Async   ── 非同期   ── メール送信・重い処理
  Display ── 表示前   ── scratchpadでClientScriptにデータ渡し

  current.setAbortAction(true) → 保存をロールバック
  previous.field              → 更新前の値(Beforeのupdate時)

【GlideRecord APIフロー】
  new GlideRecord('table')
      ├── addQuery() / addEncodedQuery() → 条件追加
      ├── setLimit() / orderBy()         → 件数・並び順
      ├── query()                         → クエリ実行
      └── while (gr.next())              → レコード反復
              ├── getValue('field')       → 文字列値
              ├── getDisplayValue('field') → 表示値
              ├── setValue('field', val)  → 値セット
              └── update() / insert() / deleteRecord()

【変更管理ポリシー層】
  データ入力経路
    ┌─ フォーム操作 ──→ UI Policy が適用される
    ├─ フォーム操作 ──→ Data Policy も適用される
    ├─ インポート  ──→ Data Policy のみ適用される
    └─ API/REST    ──→ Data Policy のみ適用される

【監査層】
  レコード変更
      └──→ sys_audit(変更履歴を自動記録)
                ※テーブルごとにAudit有効化が必要

  辞書オーバーライド
      親テーブルの定義はそのまま
      └──→ 子テーブルだけ属性を上書き(必須化など)
```

## PDI 操作ガイド

**タスク1: sys_db_objectとsys_dictionaryを直接閲覧する**

1. ナビゲーションフィルターに `sys_db_object.list` と入力してEnterを押す
2. 検索フィルターで `Name` = `incident` と入力してレコードを開く
3. 「Dictionary Entries」関連リストを確認し、incidentテーブルが持つ全フィールドを一覧で見る
4. 任意のフィールド(例: `caller_id`)をクリックし、タイプが `Reference` で参照先が `sys_user` になっていることを確認する

**タスク2: Business Ruleを作成してsetAbortActionを試す**

1. **All → System Definition → Business Rules** を開く
2. 「New」をクリック。Table: `incident`、When: `Before`、操作: `Insert`、`Update` にチェック
3. 「Advanced」タブのScript欄に以下を入力:
   ```
   if (current.state == '6' && current.assigned_to.nil()) {
     current.setAbortAction(true);
     gs.addErrorMessage('Resolved状態にする前に担当者を割り当ててください');
   }
   ```
4. Incidentフォームで担当者未設定のまま「Resolved」にしようとすると保存がアボートされることを確認

**タスク3: GlideRecordをBackground Scriptで試す**

1. **All → System Definition → Scripts - Background** を開く
2. 以下のスクリプトを実行して動作確認:
   ```
   var gr = new GlideRecord('incident');
   gr.addQuery('state', '1');
   gr.setLimit(3);
   gr.query();
   while (gr.next()) {
     gs.info(gr.getValue('number') + ': ' + gr.getValue('short_description'));
   }
   ```
3. 実行ログでincidentレコードが出力されることを確認する

**タスク4: ACLのelevate roleとACL編集を体験する**

1. 右上のアバターアイコン → `Elevate Roles` をクリックし、`security_admin` にチェック
2. **All → System Security → Access Control (ACL)** を開く
3. `incident` テーブルのACLを1件開き、「Requires role」「Condition」「Script」の3タブを確認する
4. Scriptタブで `answer = gs.hasRole('itil');` のようなスクリプトを確認する

**タスク5: 辞書オーバーライドで子テーブルだけ属性変更する**

1. **All → System Definition → Dictionary** を開く
2. 検索フィルターで `Table` = `incident`、`Column name` = `short_description` を探して開く
3. 「Dictionary Overrides」関連リストを確認する
4. 子テーブルに `Mandatory` を `true` に変更して保存する
5. 親テーブル(task)の定義は変わっていないことをsys_dictionaryで確認する

## 試験との接続

「新しいカスタムテーブルを作成した場合、テーブル名のプレフィックスはどうなるか」→ `u_` が自動付与される。

「ACLの評価順序として正しいものはどれか」→ テーブルレベル(具体→親→*)の後にフィールドレベル(具体→*)。両方パスで初めてアクセス可能。

「UI PolicyとData Policyの違いとして正しい記述はどれか」→ UI Policyはフォームのみ。Data PolicyはAPIやImport Setにも適用される。

「Dot-walkingの説明として正しいものはどれか」→ 参照フィールドを経由して別テーブルの値にアクセスできる機能。書き込みには使えない（読み取りのみ）。

「Business RuleのcurrentとpreviousはどのWhenで両方使えるか」→ Before + Update の組み合わせでのみ `previous` が有効。

「GlideRecordでクエリを実行した後にレコードを反復するメソッドはどれか」→ `gr.next()`。whileループで使用。

「setAbortAction(true)を使う主な目的は何か」→ バリデーション失敗時にデータベースへの保存をキャンセルするため。
