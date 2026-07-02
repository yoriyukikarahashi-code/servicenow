# 分野5: Database Management(配点 27%・最重要)

## 1. データスキーマの基本

- **テーブル** = レコード(行)+フィールド(列)の集合。すべてのテーブル定義は `sys_db_object` に格納。
- **フィールド定義(辞書)**: `sys_dictionary`(型・最大長・参照先・必須等)。**ラベル**は `sys_documentation`。
- 全レコードが持つシステムフィールド: `sys_id`(32文字GUID・一意)、`sys_created_on/by`、`sys_updated_on/by`、`sys_mod_count`。
- **スキーママップ(Schema Map)**: テーブル間の関係(拡張・参照)を図で確認するツール。

## 2. テーブルの拡張(継承)

- テーブルは親テーブルを**拡張(extend)**できる。子は親の全フィールドを継承し、独自フィールドを追加できる。
- 代表例:
  - `task` → Incident / Problem / Change / sc_request など(プロセス系)
  - `cmdb_ci` → cmdb_ci_computer / cmdb_ci_server など(構成アイテム系)
  - `sys_user` は拡張ではなく単独テーブル(頻出のひっかけ)
- 親テーブルのリストには子テーブルのレコードも表示される(task リストにインシデントも出る)。
- テーブル作成時に「Extensible(拡張可能)」な親を選ぶ。作成後に親は変更できない。
- 新規テーブル作成時、自動で**モジュール・アプリケーションメニューを自動生成**するオプションがある。また `u_` プレフィックスが付く(スコープアプリは `x_` )。

## 3. フィールドタイプと参照

- 主な型: String / Integer / Boolean(True/False) / Date/Time / Choice / **Reference** / List / Journal(Work notes等)。
- **Reference フィールド**: 他テーブルの1レコードを指す(**1対多**の関係を作る)。実体は参照先の sys_id を保持。
- **List フィールド**: 複数レコードを参照(カンマ区切りのsys_id)。
- **Choice フィールド**: 選択肢は `sys_choice` テーブルで管理。
- **Reference Qualifier**: 参照フィールドで選べるレコードを条件で絞る(Simple / Dynamic / Advanced)。
- **Cascade / Delete の挙動**: 参照先レコード削除時の動作(参照クリア、削除カスケード、削除制限等)を辞書で設定できる。

## 4. リレーションシップの種類

| 種類 | 実現方法 |
|------|------|
| 1対多 | Reference フィールド(多側に置く) |
| 多対多 | **Many-to-Many(m2m)テーブル**で中間テーブルを作る |
| 階層 | テーブル拡張(is-a関係) |
| Database View | 複数テーブルをJOINした読み取り専用の仮想テーブル(レポート用途) |

- **Dot-walking**: 参照フィールドを辿って参照先のフィールドにアクセス(例: `caller_id.company.name`)。リスト・レポート・スクリプトで使える。**3階層程度まで**が推奨。
- **Related List**: フォーム下部に「このレコードを参照しているレコード一覧」を表示。

## 5. CMDB

- **CI(Configuration Item)**: 管理対象の構成要素。基底テーブルは `cmdb_ci`。
- **CIリレーションシップ**: `cmdb_rel_ci` テーブルに「親CI - 関係タイプ - 子CI」で格納(例: Runs on::Runs)。
- CIクラス階層は CI Class Manager で管理。
- インシデント等のタスクは Configuration item フィールドでCIに紐づく(影響分析に使う)。

## 6. アクセス制御(ACL)— 最頻出

- ACL(Access Control List)= `sys_security_acl`。**テーブル・フィールドへの操作(read/write/create/delete)を制御**。
- ACLの変更には **security_admin ロールへの昇格(Elevate Role)** が必要。
- **評価順序(頻出)**:
  1. まず**テーブルレベル**のACLを評価: 具体的なテーブル(`incident`)→ 親(`task`)→ ワイルドカード(`*`)の順にマッチするものを探す
  2. 次に**フィールドレベル**のACLを評価: `incident.number` → `incident.*` → `*.*`
  3. **テーブルACLとフィールドACLの両方をパスして初めてアクセス可能**
- ACLの条件は3種類(すべて満たす必要): **①ロール ②条件(フィルター) ③スクリプト**。
- マッチするACLが1つもないテーブルはデフォルトで拒否(admin以外)。
- **High Security Settings** プラグインでデフォルト拒否等のセキュリティ強化。
- デバッグ: **Debug Security Rules** でフォーム/リスト上のACL評価結果を確認。

## 7. UI Policy / Data Policy / ビジネスルール(データ整合性)

| 仕組み | 動作場所 | 用途 |
|------|------|------|
| **UI Policy** | ブラウザ(フォーム上) | フィールドの必須/読取専用/表示切替。**フォーム経由のみ有効** |
| **Data Policy** | サーバー | 必須/読取専用を**すべての入口(インポート・API含む)で強制**。UI Policyに変換適用も可 |
| **Business Rule** | サーバー | レコードのinsert/update/delete/query時のロジック(before/after/async/display) |
| **Client Script** | ブラウザ | onLoad / onChange / onSubmit / onCellEdit のスクリプト制御 |

- **UI PolicyとData Policyの違いは最頻出**: UI Policyはフォームだけ、Data Policyはインポートやスクリプトにも効く。

## 8. 監査・履歴・データ管理

- **Auditing**: 辞書で監査有効化(taskはデフォルト有効)。変更履歴は `sys_audit` に記録され、フォームの History で確認。
- **削除**: レコード削除の復元は限定的(Rollback & Delete Recovery)。大量削除・テーブル削除は慎重に。
- **辞書オーバーライド(Dictionary Override)**: 継承フィールドの属性(デフォルト値・必須等)を**子テーブルでだけ**変える仕組み(親の定義は変えない)。

---

## 頻出ポイント

- ACLの評価順序(テーブル→フィールド、具体→ワイルドカード)と security_admin
- UI Policy vs Data Policy
- テーブル拡張と task / cmdb_ci ファミリー
- 1対多=Reference、多対多=m2mテーブル、Database View はJOIN(読み取り専用)
- Dot-walking の書き方
- 辞書(sys_dictionary)とラベル(sys_documentation)、辞書オーバーライド
- sys_id は32文字の一意ID
