# 分野5: Database Management(配点 27%・最重要)

## 1. データスキーマの基本

全テーブル定義はsys_db_object。フィールド定義(辞書)はsys_dictionary。ラベルはsys_documentation。sys_idは32文字GUIDで全レコードに存在。

## 2. テーブルの拡張(継承)

taskがIncident/Problem/Change等の親。cmdb_ciがCI系の親。sys_userは単独テーブル(拡張ではない)。親のリストには子のレコードも表示される。新規テーブルにはu_プレフィックス。

## 3. フィールドタイプと参照

Reference(1対多)、List(複数参照)、Choice(sys_choiceで管理)。Dot-walkingで参照先フィールドにアクセス(例: caller_id.company.name)。

## 4. リレーションシップ

1対多=Reference、多対多=m2mテーブル、Database View=JOIN(読み取り専用)。

## 5. CMDB

CI基底テーブルはcmdb_ci。CIリレーションシップはcmdb_rel_ciテーブル。

## 6. ACL(アクセス制御) — 最頻出

評価順序: テーブルレベル(具体→親→ワイルドカード)→フィールドレベル(具体→ワイルドカード)。両方パスしてアクセス可能。ACL変更にはsecurity_adminへのelevate roleが必要。条件3種類: ロール/条件(フィルター)/スクリプト。

## 7. UI Policy / Data Policy / Business Rule

UI Policy=フォームのみ。Data Policy=全入力経路(インポート・API含む)。Business Ruleはサーバーサイドのinsert/update/delete/queryロジック。

## 8. 監査・辞書オーバーライド

Auditingはsys_auditに記録。辞書オーバーライドで子テーブルだけ属性変更(親の定義は変えない)。

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

  sys_user ── (継承なし・独立テーブル)

  【子→親の参照】
  子テーブルのレコード ──→ 親テーブルのリストにも表示される

【リレーションシップ層】
  1対多  : Referenceフィールド ──→ 参照先テーブル
  多対多  : m2mテーブル(例: sys_user_has_role)
                ├── sys_user へのReference
                └── sys_user_role へのReference
  結合表示: Database View(読み取り専用・JOINの仮想テーブル)
  Dot-walk: caller_id ──→ .company ──→ .name

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
    ロールチェック → 条件(フィルター) → スクリプト
    ※すべての条件がtrueの場合のみACL通過

  ACL変更操作:
    通常ロール ──→ elevate ──→ security_admin ──→ ACL編集可能

【変更管理ポリシー層】
  データ入力経路
    ┌─ フォーム操作 ──→ UI Policy が適用される
    ├─ フォーム操作 ──→ Data Policy も適用される
    ├─ インポート  ──→ Data Policy のみ適用される
    └─ API/REST    ──→ Data Policy のみ適用される

  Business Rule(サーバーサイド)
    insert / update / delete / query のタイミングで実行
    Before / After / Async の実行タイプ

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
5. 【確認ポイント】sys_db_objectが「テーブルの入れ物」、sys_dictionaryが「フィールドの設計図」であることを視覚的に把握する

**タスク2: テーブル継承の親子関係を確認する**

1. `All → System Definition → Tables` を開く(またはナビゲーターに `sys_db_object.list`)
2. `incident` テーブルを開き、「Extends table」フィールドが `task` になっていることを確認する
3. `task.list` をナビゲーターに入力し、taskリストを開く
4. リストにincident/problem/change_requestのレコードが混在して表示されることを確認する
5. 【確認ポイント】親テーブルのリストには子テーブルのレコードも表示されるという継承の動作を体感する

**タスク3: ACLのelevate roleとACL編集を体験する**

1. `All → User Administration → Users` から自分のユーザーを開き、Rolesを確認する(`security_admin`がないことを確認)
2. 右上のアバターアイコン → `Elevate Roles` をクリックし、`security_admin` にチェックを入れてOKを押す
3. `All → System Security → Access Control (ACL)` を開く
4. `incident` テーブルのACLを1件開き、「Requires role」「Condition」「Script」の3タブを確認する
5. 評価順序(ロール → 条件 → スクリプト)がUIの構造として現れていることを確認する
6. 【確認ポイント】elevateなしではACL一覧が読み取り専用になること、またはメニューが制限されることを比較して観察する

**タスク4: UI PolicyとData Policyの適用範囲の違いを確認する**

1. `All → System UI → UI Policies` を開き、任意のUI Policyを1件開く
2. 「Applies on」フィールドが「Form」のみであることを確認する
3. `All → System Policy → Data Policies` を開き、任意のData Policyを1件開く
4. 「Applies to」に「Import Sets」や「REST API」が含まれる設定を確認する
5. 同じフィールドを必須化する場合、フォームのみならUI Policy、API経由も含むならData Policyが必要であることを比較メモする

**タスク5: 辞書オーバーライドで子テーブルだけ属性変更する**

1. `All → System Definition → Dictionary` を開く
2. 検索フィルターで `Table` = `incident`、`Column name` = `short_description` を探して開く
3. 「Dictionary Overrides」関連リストを確認する(または新規追加ボタンを押す)
4. 子テーブル(`u_`プレフィックスのカスタムテーブル)を指定し、`Mandatory` を `true` に変更して保存する
5. 親テーブル(task)の`short_description`定義は変わっていないことをsys_dictionaryで確認する
6. 【確認ポイント】親の定義を汚さずに子だけ属性を変えられることを手で確かめる

## 試験との接続

「新しいカスタムテーブルを作成した場合、テーブル名のプレフィックスはどうなるか」→ PDIでテーブル作成画面(`System Definition → Tables → New`)を実際に開くと、Label入力後に自動で`u_`が付与されるのを目で見て確認でき、「u_プレフィックスは自動付与」という事実が体に入る。

「ACLの評価順序として正しいものはどれか」→ PDIでACL一覧(`System Security → Access Control`)をテーブル名でソートすると、具体テーブル→ワイルドカード(`*`)の順にレコードが並ぶのを確認でき、「具体的なものが先に評価される」という順序が一覧の並び順として直感的にわかる。

「UI PolicyとData Policyの違いとして正しい記述はどれか」→ PDIで両方のフォームを開いて並べると、UI Policyには「Show/Hide」「Mandatory」「Read Only」を「フォーム上で」制御するフィールドしかないのに対し、Data Policyには「Import Sets」チェックボックスがあることが視覚的に比較でき、適用範囲の違いが一目でわかる。

「Dot-walkingの説明として正しいものはどれか」→ PDIでReportかList Filterを作成する際に`caller_id.company.name`のようにフィールドをドットでたどれることを実際に試すと、「参照フィールドを経由して別テーブルの値にアクセスできる」という概念が操作として染みこみ、選択肢の誤記述(「Dot-walkingは書き込みにも使える」等)を即座に排除できるようになる。

「テーブル継承に関して正しい記述はどれか」→ PDIで`task.list`を開くと、Incidentのレコードが混在して一覧に現れることを確認でき、「親テーブルのリストには子テーブルのレコードも表示される」という仕様が体験として定着し、「sys_userはtaskを拡張している」などの誤りの選択肢を自信を持って除外できる。
