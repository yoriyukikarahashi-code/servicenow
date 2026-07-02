# 分野6: Data Migration and Integration(配点 15%)

## 1. Import Set(インポートセット)— 中心テーマ

外部データをServiceNowに取り込む標準の仕組み。**流れを丸ごと覚える**:

```
① Data Source(データソース)を定義
      ↓ Load Data
② Import Set Table(ステージングテーブル)にロード
      ↓ Transform
③ Transform Map で ターゲットテーブルへ変換・投入
```

- **Data Source**: 取り込み元の定義。ファイル(CSV/Excel/XML/JSON)、**JDBC**(外部DB)、**LDAP**、REST等。ファイルは添付・FTP・HTTP経由で指定可。
- **Import Set Table**: 一時的な受け皿(ステージング)。ロード時に自動作成され、列は取り込みデータから推定される。`sys_import_set_row` を拡張。
- **Transform Map**: ステージング→ターゲットのマッピング定義。
  - **Field Map**: ソース列→ターゲット列の対応(Auto Map で名前一致を自動対応)。
  - **Coalesce(コアレス)**: **キー指定**。coalesce フィールドが一致する既存レコードがあれば**更新**、なければ**新規作成**。coalesce未指定なら**常に新規作成**(重複が生まれる)。複数フィールドcoalesce も可。
  - **Transform Script**: onBefore / onAfter / onStart / onComplete 等のタイミングでスクリプト補正。

## 2. インポート結果のステータス

Import Set Row ごとに結果が記録される:

| ステータス | 意味 |
|------|------|
| Inserted | 新規作成された |
| Updated | coalesce 一致で更新された |
| Ignored | 変更なし等でスキップ |
| Skipped | 条件・エラーでスキップ(例: coalesce対象が複数一致) |
| Error | 変換エラー |

- インポート後は Import Set の一覧・Transform History で結果を必ず確認する。

## 3. スケジュールインポート

- **Scheduled Import** で定期実行(日次のLDAP取り込み等)。
- 実行順序の依存(親子)を設定できる。

## 4. LDAP統合

- LDAP(Active Directory等)から**ユーザー・グループ情報を取り込む**代表的統合。
- LDAP Server 定義 → OU Definition(取り込み範囲)→ Data Source → Transform Map の構成。
- **LDAPはユーザーデータのインポートと認証(SSOの一種)の両方に使える**。
- スケジュールで定期同期するのが一般的。

## 5. Web Services / API

- **REST API**: ServiceNowは **Table API** 等のREST APIを標準提供(外部からレコードCRUD可能)。
- **SOAP** も利用可(レガシー)。
- **REST API Explorer**: インスタンス内でAPIリクエストを試せるツール。
- インバウンド(外部→SN)とアウトバウンド(SN→外部、RESTメッセージ/IntegrationHub)の区別。
- **IntegrationHub**: Flow Designer から外部システム連携(Spoke)を行う有償拡張。

## 6. エクスポート

- リストから右クリック等で **CSV / Excel / PDF / XML / JSON** にエクスポート可能。
- **XMLエクスポート/インポート(Export to XML / Import XML)**: sys_id を保ったままレコードを移送できる(管理者向け。少量データの環境間移動に使う)。
- エクスポート上限はプロパティで制御されている。

## 7. Update Set と Import Set の違い(頻出)

| | Update Set | Import Set |
|---|---|---|
| 対象 | **構成・カスタマイズ**(フォーム、ビジネスルール等) | **データ**(ユーザー、CI、タスク等) |
| 方向 | インスタンス間の移送 | 外部→インスタンスの取り込み |
| 仕組み | XML化された構成変更の記録 | ステージング+Transform Map |

---

## 頻出ポイント

- インポートの3ステップ(Data Source → Import Set Table → Transform Map)
- **Coalesce の挙動**(一致→更新 / 不一致→挿入 / 未指定→常に挿入)
- Import Set Row のステータス(Inserted / Updated / Ignored / Skipped / Error)
- LDAPで取り込めるもの(ユーザー・グループ)
- Update Set(構成)と Import Set(データ)の役割分担
- Export to XML は sys_id を維持する
