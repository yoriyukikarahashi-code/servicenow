# 分野3: Configuring Applications for Collaboration(配点 20%)

## 1. ユーザー・グループ・ロール

| オブジェクト | テーブル | ポイント |
|------|------|------|
| ユーザー | `sys_user` | ログインする人。ロックアウト・アクティブフラグあり |
| グループ | `sys_user_group` | ユーザーの集合。**ロール付与・タスク割当の基本単位** |
| ロール | `sys_user_role` | 権限の単位。ユーザー/グループに付与。**ロールはロールを含められる(継承)** |

- **ベストプラクティス: ロールはユーザー個人ではなくグループに付与**し、ユーザーをグループに入れる。
- グループにロールを付与すると、**所属メンバー全員がそのロールを継承**する。
- 主要ロール:
  - `admin`: ほぼ全権限(ただし security_admin は別)
  - `security_admin`: ACLの変更に必要(**elevate role で一時的に昇格**して使う)
  - `itil`: ITSMの標準的な作業者(インシデント処理等)
  - `approver_user`: 承認操作
  - `catalog_admin` / `knowledge_admin` など機能別管理ロール

## 2. タスクテーブル(Task Table)

- `task` テーブルは多くのアプリの**親テーブル**(Incident, Problem, Change, Request等が拡張)。
- 共通フィールド(Number, Assigned to, Assignment group, State, Priority等)は task で定義され子に継承。
- **Assignment Rules(割当ルール)**: 条件に応じて Assignment group / Assigned to を自動設定。
- **サービスレベル(SLA)**: タスクに対する応答・解決期限を管理(分野4でも出題)。

## 3. Visual Task Board(VTB)

- タスクをカンバン形式で管理するボード。
- **Flexible Board**: 任意のフィールドを軸にせず自由にレーン作成(ボード上の操作はレコードを変更しない)。
- **Guided Board**: 特定フィールド(State等)をレーンに対応させ、**カード移動でレコードのフィールド値が実際に更新される**。
- **Freeform Board**: 任意のタスクを自由に追加。

## 4. 通知(Notifications)

- **Email Notification** の発火条件: ①レコードの挿入/更新(条件指定) ②**イベント(Event)発火時** ③トリガー(スケジュール)。
- 構成3要素: **When to send(いつ)/ Who will receive(誰に)/ What it will contain(何を)**。
- **イベントレジストリ**(`sysevent_register`)に登録されたイベントを、ビジネスルール等から `gs.eventQueue()` で発火できる。
- **Email Template** で本文を再利用。変数 `${field_name}` でフィールド値を差し込み。
- ユーザーは **Notification Preferences** で自分の受信方法を制御できる。
- インスタンスのメール送受信はプロパティで有効化する(デフォルトの送信は `instance@service-now.com` 経由)。

## 5. レポートとダッシュボード

- **レポートタイプ**: Bar / Pie / Time Series / List / Single Score / Map など。
- レポート作成は Report Designer。**共有(Sharing)**: 個人 / グループ / ロール / 全員に公開、スケジュール配信も可。
- レポートのデータは**閲覧者のACLで絞られる**(見えないデータは表示されない)。
- **ダッシュボード**: 複数レポート(ウィジェット)を1画面に配置。タブ・共有設定あり。
- **Performance Analytics(PA)** はスナップショットによる**時系列トレンド分析**(レポートとの違いとして頻出)。レポートは「今」のデータ、PAは「経時変化」。

## 6. ナレッジ管理(Knowledge Management)

- **Knowledge Base(KB)** > **Category** > **Article** の階層。
- 記事のライフサイクル: **Draft → Review → Published → Retired**(ワークフローで制御)。
- KBごとに設定可能: **User Criteria で Can Read / Can Contribute** を制御。
- 記事はバージョン管理される。フィードバック(評価・コメント・フラグ)機能あり。
- インシデント等から**ナレッジ記事を作成**できる(Post Knowledge / KCS的な使い方)。
- 検索はグローバル検索・ポータル・サービスカタログから可能。

## 7. Connect / チャット・その他コラボ

- **Connect Chat**: プラットフォーム内のリアルタイムチャット(レコードに紐づくConnectサポートもある)。
- **Agent Workspace**: エージェント向け統合作業画面(複数タブ・関連情報表示)。
- **アクティビティストリーム**: フォーム上の Work notes(内部) / Additional comments(顧客向け)の履歴表示。Work notes は itil 等の内部ユーザーのみ閲覧。

---

## 頻出ポイント

- ロールは**グループに付与**がベストプラクティス/ロールの継承
- security_admin と elevate role の関係
- 通知の3要素(When / Who / What)とイベント駆動
- ナレッジ記事のライフサイクル(Draft → Review → Published → Retired)
- User Criteria(Can Read / Can Contribute)
- レポート vs Performance Analytics の違い
- VTBの3種類(Flexible / Guided / Freeform)と Guided のフィールド更新
