# 分野5: Database Management(配点 27%・最重要)

## 1. データスキーマの基本

全テーブル定義はsys_db_object。フィールド定義(辞書)はsys_dictionary。ラベルはsys_documentation。sys_idは32文字GUIDで全レコードに存在。

## 2. テーブルの拡張(継承)

taskがIncident/Problem/Change等の親。cmdb_ciがCI系の親。sys_userは単独テーブル(拡張ではない)。親のリストには子のレコードも表示される。新規テーブルにu_プレフィックス。

## 3. フィールドタイプと参照

Reference(1対多)、List(複数参照)、Choice(sys_choiceで管理)。Dot-walkingで参照先フィールドにアクセス(例: caller_id.company.name)。

## 4. リレーションシップ

1対多=Reference、多対多=m2mテーブル、Database View=JOIN(読み取り専用)。

## 5. CMDB

CI基底テーブルはcmdb_ci。CIリレーションシップはcmdb_rel_ciテーブル。

## 6. ACL(アクセス制御) — 最頼出

評価順序: テーブルレベル(具体→親→ワイルドカード)→フィールドレベル(具体→ワイルドカード)。両方パスしてアクセス可能。ACL変更にsecurity_adminへのelevate roleが必要。条件3種類: ロール/条件(フィルター)/スクリプト。

**ACLスクリプトフィールド:**
- `answer` 変数に `true` または `false` をセットして返す
- `current` でカレントレコードを参照
- `gs.hasRole('role')` でロールチェック
- admin ロールはACLを無条件でバイパス

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
- `previous.state`: 変更前のStatフィールド値

**setAbortAction(true):**
- `current.setAbortAction(true)`: DB保存をアボートしロールバック
- `gs.addErrorMessage('メッセージ')`: ユーザーへエラーメッセージ表示
- Before Business Ruleでバリデーションロジックを実装する際に使用

**Scratchpad オブジェクト:**
- `g_scratchpad.key = value`: Display Business RuleかClient Scriptにデータを渡す

## 9. GlideRecord API

サーバーサイドでテーブルを操作するJavaScript API。

**単一レコード取得:**
- `gr.get(sys_id)` または `gr.get('number', 'INC0000001')`

**クエリ実行:**
- `gr.addQuery('state', '1')` — state = 1
- `gr.addQuery('priority', '<', '3')` — priority < 3
- `gr.addEncodedQuery('active=true^state=1')` — エンコードクエリ
- `gr.setLimit(10)` — 件数制限
- `gr.orderBy('priority')` / `gr.orderByDesc('sys_created_on')`
- `gr.query()` — クエリ実行
- `while (gr.next()) { ... }` — レコード反復

**OR条件:**
- `var qc = gr.addQuery('state', '1'); qc.addOrCondition('state', '2');`

**値の取得・設定:**
- `gr.getValue('field')` — 文字列値
- `gr.getDisplayValue('field')` — 表示値
- `gr.setValue('field', value)` — 値セット

**レコード操作:**
- `gr.insert()` — 作成。sys_idを返す
- `gr.update()` — 更新。保存
- `gr.deleteRecord()` — 削除

## 10. テーブルと辞書の詳細

**Auto Number (自動番号):**
- Prefix: 番号のプレフィックス(例: INC)
- Next value: 次に付与される数値
- Padding: 桁数(0埋め)

**Dictionary Entry の主なフィールド:**
- Type: 文字列/整数/日付/Reference等
- Max length: 最大文字数
- Default value: デフォルト値
- Mandatory: 必須フラグ

**Reference フィールド:** Reference qualifier で参照先レコードを絞り込む条件スクリプト

**辞書オーバーライド:** 子テーブルだけフィールド属性を変更（親の定義はたそのまま）

## 11. 監査・辞書オーバーライド

**Auditing**: sys_auditに変更履歴を記録（テーブルごとに有効化必要）。

**辞書オーバーライド**: 子テーブルだけ属性変更（親の定義は変えない）。

## 全体構造マップ

```
【スキーマ層】
  sys_db_object(テーブル定義)
      ├─→ sys_dictionary(フィールド定義・辞書)
      └─→ sys_choice(Choiceフィールドの選択肢)

【テーブル継承ツリー】
  task(親) → incident / problem / change_request
  cmdb_ci(親) → cmdb_ci_computer / cmdb_ci_server
  sys_user — (継承なし・独立テーブル)

【ACL 評価フロー】
  リクエスト → テーブルACL評価(具体→親→*)
  → フィールドACL評価(具体→*) → アクセス許可/拒否
  ACL条件: ロール → 条件 → スクリプト(answer=true/false)
  admin ロールはACLをバイパス

【Business Rule タイミング】
  Before  — DB保存前 — current変更・setAbortAction・バリデーション
  After   — DB保存後 — 他レコード更新・後処理
  Async   — 非同期   — メール送信・重い処理
  Display — 表示前   — scratchpadでClient Scriptにデータ渡し

  current.setAbortAction(true) → 保存をロールバック
  previous.field → 更新前の値(Beforeのupdate時)

【GlideRecord APIフロー】
  new GlideRecord('table')
      ├─ addQuery() / addEncodedQuery()
      ├─ setLimit() / orderBy()
      ├─ query() → while (gr.next())
      ├─ getValue / getDisplayValue / setValue
      └─ insert() / update() / deleteRecord()
```

## PDI 操作ガイド

**タスク1: Business Ruleを作成してsetAbortActionを試す**

1. **All → System Definition → Business Rules** を開く
2. 「New」をクリック。Table: `incident`、When: `Before`、InsertとUpdateにチェック
3. AdvancedタブのScript欄にバリデーションスクリプトを入力して保存
4. Incidentフォームで条件違反状態で保存しようとするとアボートされることを確認

**タスク2: GlideRecordをBackground Scriptで試す**

1. **All → System Definition → Scripts - Background** を開く
2. GlideRecordでincidentをクエリし、numberとshort_descriptionをgs.info()で出力する
3. 実行ログでincidentレコードが出力されることを確認する

**タスク3: ACLのelevate roleとACL編集を体験する**

1. 右上のアバターアイコン → `Elevate Roles` をクリックし、`security_admin` にチェック
2. **All → System Security → Access Control (ACL)** を開く
3. `incident` テーブルのACLを開き、Roles/Condition/Scriptの3タブを確認する
4. Scriptタブで `answer = gs.hasRole('itil');` のようなスクリプトを確認する

**タスク4: 辞書オーバーライドで子テーブルだけ属性変更する**

1. **All → System Definition → Dictionary** を開く
2. `incident` テーブルの `short_description` フィールドを開く
3. 「Dictionary Overrides」関連リストで子テーブルに `Mandatory` を `true` に設定して保存
4. 親テーブル(task)の定義は変わっていないことを確認する

## 試験との接続

「新しいカスタムテーブルのプレフィックスは」→ `u_` が自動付与される。

「ACLの評価順序として正しいものはどれか」→ テーブルレベル(具体→親→*)の後にフィールドレベル(具体→*)。両方パスで初めてアクセス可能。

「UI PolicyとData Policyの違いとして正しい記述はどれか」→ UI Policyはフォームのみ。Data PolicyはAPIやImport Setにも適用される。

「Business RuleのcurrentとpreviousはどのWhenで両方使えるか」→ Before + Updateの組み合わせでのみ `previous` が有効。

「GlideRecordでクエリを実行した後にレコードを反復するメソッドは」→ `gr.next()`。whileループで使用。

「setAbortAction(true)を使う主な目的は何か」→ バリデーション失敗時にデータベースへの保存をキャンセルするため。
