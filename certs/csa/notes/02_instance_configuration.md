# 分野2: Instance Configuration(配点 11%)

## 1. システムプロパティ(System Properties)

- インスタンス全体の動作を制御する設定値。テーブルは `sys_properties`。
- 例: `glide.ui.session_timeout`(セッションタイムアウト)、メール送受信の有効化など。
- 変更はインスタンス全体に影響するため、変更前に影響範囲を確認する。

## 2. ブランディング / テーマ

- **Next Experience**では、テーマ(ロゴ・配色)を **Next Experience の Theme(ブランディング設定)** で構成する。
- 会社ロゴ・ブラウザタブのタイトル・バナー画像などを設定可能。
- ポータル(Service Portal / Employee Center)のブランディングは別途ポータル側で設定する。

## 3. フォーム設定

| 手段 | 用途 |
|------|------|
| **Form Layout** | フィールドの追加・削除・並び替え(シンプルなスレート型UI) |
| **Form Design** | ドラッグ&ドロップのWYSIWYG。セクション・列構成も編集可 |
| **ビュー(View)** | 同じテーブルに複数のフォーム/リストレイアウトを持たせる仕組み。例: 標準ビュー・モバイルビュー・ロール別ビュー |

- ビューはリストにも適用される。**ビュールール(View Rules)**で条件に応じたビュー自動切替が可能。
- フォームのセクションは2列表示等に設定できる。

## 4. リスト設定

- **List Layout** で列の追加・削除・順序変更(管理者は全員向けデフォルトを変更、一般ユーザーは個人設定)。
- 個人の列設定(Personal List)はデフォルトより優先される。

## 5. プラグイン(Plugins)

- 機能単位の拡張モジュール。**有効化はできるが、基本的に無効化(アンインストール)はできない**。
- 一部プラグインは有償・要ライセンス。有効化はNow Supportからのリクエストが必要なものもある。
- 有効化するとデモデータを含められる場合がある(本番では通常含めない)。

## 6. Update Set(更新セット)

構成変更(カスタマイズ)をインスタンス間で移送するための仕組み。**CSA頻出**。

- **記録されるもの**: 構成レコード(フォームレイアウト、ビジネスルール、ACL等の「カスタマイズ」)。
- **記録されないもの**: **データ(タスクレコード等)・スケジュールジョブの実行結果・ホームページ/ダッシュボード(手動追加が必要な場合あり)・新規テーブルのデータ**。
- 流れ: 開発環境で Update Set 作成 → **Complete** に変更 → テスト環境で **Retrieve(取得)** → **Preview(プレビュー)** で衝突検出 → **Commit(コミット)**。
- **Default update set**: 更新セットを指定しないときの受け皿。移送用には使わない。
- 複数の更新セットは**バッチ(親子関係)**にまとめて一括移送できる。
- プレビューで衝突(Collision)が出たら、Accept/Skip を判断してからコミット。

## 7. 開発プロセス(インスタンス構成)

- 典型構成: **開発(Dev) → テスト(Test) → 本番(Prod)** の3インスタンス。
- カスタマイズは Dev で行い、Update Set で昇格。本番で直接変更しない。
- **クローン(Clone)**: 本番インスタンスのデータ・構成を下位環境へコピーする機能(逆方向はしない)。

## 8. 多言語・ローカライゼーション

- 言語プラグイン(I18N)を有効化するとUIの多言語化が可能。
- ユーザーごとに言語・タイムゾーン・日付書式を設定できる。

---

## 頻出ポイント

- Update Set に**含まれるもの/含まれないもの**(データは含まれない)
- Update Set の移送フロー(Complete → Retrieve → Preview → Commit)
- Form Layout と Form Design の違い、ビューの概念
- プラグインは基本的に無効化できない
- クローンは本番→下位環境の方向

---

## 全体構造マップ

```
【インスタンス全体の制御】
  sys_properties (System Properties テーブル)
      │
      ├── セッション・メール・UI動作などを制御
      └── Next Experience テーマ設定 ──→ ロゴ・配色・バナー
              │
              └── Service Portal ブランディング(別管理)

【フォーム・リスト表示の制御】
  テーブル定義 (sys_dictionary)
      │
      ├── Form Layout / Form Design
      │       └── ビュー(View) ──→ ビュールール(View Rules)で自動切替
      │               ├── 標準ビュー
      │               ├── モバイルビュー
      │               └── ロール別ビュー
      │
      └── List Layout
              ├── 管理者設定(全員のデフォルト)
              └── 個人設定(Personal List) ← デフォルトより優先

【機能拡張】
  Plugins (sys_store_app / sys_plugins)
      └── 有効化のみ可(無効化は原則不可)
              └── デモデータ含める/含めない を選択

【環境間の変更管理】
  開発(Dev) ──Update Set作成──→ Complete
                                    │
                          テスト(Test)でRetrieve(取得)
                                    │
                               Preview(プレビュー)
                                    │
                          衝突(Collision)? ──→ Accept / Skip 判断
                                    │
                               Commit(コミット)
                                    │
                          本番(Prod)でも同様に適用

  ※ Update Set テーブル: sys_update_set / sys_update_xml
  ※ 記録対象: 構成レコード(カスタマイズ)のみ
  ※ 非記録: データレコード(incident等)・ダッシュボード・実行結果

【環境コピー】
  本番(Prod) ──Clone──→ テスト(Test) / 開発(Dev)
  ※ 逆方向(下位→本番)のクローンは行わない
```

## PDI 操作ガイド

### タスク1: System Properties を閲覧する

1. ナビゲーションバーの検索欄に `sys_properties.list` と入力してEnter。
2. 検索フィルターで Name に `glide.ui.session_timeout` と入力して絞り込む。
3. レコードを開き、Value の値を確認する(デフォルト: 30分相当)。
4. 値の型(文字列/整数)と説明(Description)フィールドがあることを確認する。

### タスク2: Update Set を作成してフォームレイアウトを変更する

1. `All → System Update Sets → Local Update Sets` を開く。
2. 「New」をクリックし、Name に `練習用UpdateSet_01` と入力して保存。
3. 保存したレコードを開き、右上の「Make Current」をクリック。
4. インシデントフォームを開き、フォームヘッダー(タイトルバー)を右クリック → `Configure` → `Form Layout` を選択。
5. 利用可能フィールドから「Impact」を追加して保存。
6. `Local Update Sets` に戻り、「Customer Updates」関連リストに変更が記録されていることを確認する。
7. State を「Complete」に変更して保存。

### タスク3: Form Layout と Form Design の違いを確認する

1. インシデントフォームを開く。
2. フォームヘッダーを右クリック → `Configure` → `Form Layout` を選択 → シンプルな2列選択UI(Available/Selected)を確認。
3. 同じフォームに戻り、フォームヘッダーを右クリック → `Configure` → `Form Design` を選択。
4. ドラッグ&ドロップ可能なキャンバスUI、セクション追加が可能なことを確認する。

### タスク4: プラグインの有効化画面を確認する

1. `All → System Definition → Plugins` を開く(自動的に **Application Manager** 画面にリダイレクトされる)。
2. 検索欄に `Survey` と入力して絞り込む。
3. 「Surveys and Assessments」プラグインのレコードを開く。
4. 「Activate/Upgrade」ボタンをクリックすると「Load demo data?」のダイアログが表示されることを確認する(実際には保存しない)。
5. 有効化済みプラグインは基本的に無効化できないことを確認する(Deactivateが表示されても機能しない/グレーアウト)。

## Scheduled Jobs（スケジュールジョブ）

定期実行するスクリプト（テーブル: sys_trigger / sysauto_script）。

**設定項目:**
- `Run`: 実行頻度（Daily / Weekly / Monthly / Once / On Demand / Periodically）
- `Run time`: 実行時刻
- `Script`: 実行するGlideScriptコード

**用途例:**
- 夜間バッチ処理（古いレコードのクローズ）
- 定期レポート生成
- Performance AnalyticsのIndicatorデータ収集

**Scheduled Importとの違い:**
- Scheduled Import: 外部データの定期取り込み（Import Set使用）
- Scheduled Job: 任意のサーバーサイドスクリプトを定期実行

## Application Scope（スコープ）

**Global スコープ vs スコープドアプリ:**
- `Global`: 全アプリケーションからアクセス可能な共通領域
- `Scoped App`: 独自の名前空間を持つ分離されたアプリ（例: x_myco_myapp）

**スコープの切り替え:**
- 右上のアプリケーションセレクター（Application Pill）でスコープを切り替え
- スコープ外のリソースへのアクセスはApplication Accessで制御

**スコープドアプリのプレフィックス:**
- カスタムテーブル: `x_ベンダーコード_アプリ名_テーブル名`
- ※ グローバルスコープのカスタムテーブルは `u_` プレフィックス

## 試験との接続

「Update Set に含まれないものはどれか」→ データレコード(incident等)は含まれない。Customer Updates関連リストを見れば、構成レコードのみが記録されることが確認できる。

「Update Set をテスト環境に移送する正しい順序はどれか」→ Complete → Retrieve → Preview → Commit。PDIでボタンが段階的にしか有効にならない設計を見ると自然に記憶される。

「Form Layout と Form Design の主な違いはどれか」→ Form Layoutはシンプルなフィールド追加/並び替えのみ。Form Designはセクション・列構成をドラッグで変更できる。

「プラグインの有効化に関して正しい記述はどれか」→ 有効化は一方通行(無効化不可)。有効化時にデモデータを含めるか選択できる。本番ではデモデータを含めない。
