# 分野6: Data Migration and Integration(配点 15%)

## 1. Import Set — 中心テーマ

Data Source → Import Set Table(ステージング) → Transform Map(変換) の3ステップ。Coalesceがキー: 一致→更新、不一致→挿入、未指定→常に挿入。結果ステータス: Inserted/Updated/Ignored/Skipped/Error。

## 2. スケジュールインポート

Scheduled Importで定期実行。LDAP統合ではユーザー・グループを定期同期。

## 3. Web Services / API

Table APIなどREST APIを標準提供。REST API Explorerでインスタンス内テスト可能。IntegrationHubはFlow Designerから外部連携するSpoke群(有償)。

## 4. エクスポート

CSV/Excel/PDF/XML/JSONでエクスポート可能。Export to XMLはsys_idを維持したまま移送できる。

## 5. Update Set vs Import Set

Update Set=構成・カスタマイズのインスタンス間移送。Import Set=外部データの取り込み。

## 全体構造マップ

```
【外部データ取り込み: Import Set フロー】

  外部ソース (CSV / Excel / JDBC / REST)
        │
        ▼
  Data Source (接続定義: sys_data_source)
        │
        ▼
  Import Set Table [ステージング領域]
  (u_imp_xxxx)
        │
        ├─ 手動ロード: Load All Records
        └─ 自動ロード: Scheduled Import (sys_trigger)
                │
                ▼
        Transform Map (sys_transform_map)
          ├─ Field Map (列の対応定義)
          │    例: [source: name] → [target: sys_user.first_name]
          ├─ Coalesce フィールド指定
          │    一致あり → Update (既存レコード更新)
          │    一致なし → Insert (新規行追加)
          │    未指定  → 常に Insert
          └─ Transform Script (onBefore / onAfter)
                │
                ▼
        ターゲットテーブル (例: sys_user / cmdb_ci_server など)
                │
                ▼
        Import Set Run Log
          Inserted / Updated / Ignored / Skipped / Error

【API / 外部連携】

  外部システム
    ├─ REST (Table API / Scripted REST)
    │    └─ REST API Explorer でインスタンス内テスト
    ├─ SOAP
    └─ IntegrationHub Spoke (有償)
         └─ Flow Designer → Action → HTTP Step

【LDAP 同期】

  LDAP サーバー
    └─ LDAP Server 定義 (sys_ldap_server)
         └─ Scheduled Import で定期同期
              └─ sys_user / sys_user_group へ反映
```

## PDI 操作ガイド

### タスク1: Import Set で CSV をインポートする

1. サンプル CSV を準備する (列: first_name, last_name, email)
2. **All → System Import Sets → Load Data** を開く
3. "Create table" を選択し、テーブルラベルに `Test User Import` と入力
4. Import from: File を選択し、CSV をアップロードして **Submit**
5. ステージングテーブル (`u_imp_test_user_import`) に行が作成されたことを確認する

### タスク2: Transform Map を作成して Coalesce を確認する

1. **All → System Import Sets → Transform Maps** を開く
2. **New** をクリックし、Source Table に `u_imp_test_user_import`、Target Table に `sys_user` を設定して保存
3. **Field Maps** タブで **Auto Map Matching Fields** をクリックし、自動マッピングを生成する
4. email フィールドの Field Map を開き、**Coalesce** チェックボックスをオンにして保存
5. Transform Map 画面上部の **Transform** ボタンをクリックして実行する
6. Import Set Run Log で Inserted / Updated の件数を確認する

### タスク3: Coalesce なしとの比較実験

1. タスク2と同じ CSV を再度 Load Data でロードする
2. Transform Map の email の Coalesce チェックを**外して** Transform を実行する
3. sys_user に重複レコードが挿入される (Inserted のみで Updated が 0) ことを確認する

### タスク4: REST API Explorer で Table API を試す

1. **All → System Web Services → REST API Explorer** を開く
2. API Name: `Table API`、Method: GET、tableName: `incident`、sysparm_limit: `3` を入力して **Send** をクリックする
3. JSON レスポンスに incident レコードが返ることを確認する

## MID Server

オンプレミスシステムとServiceNowをつなぐミドルウェア（Management, Instrumentation, and Discovery Server）。

**役割:**
- ファイアウォール内のシステム（JDBC / LDAP / SNMP）とServiceNowの橋渡し
- Discovery・IntegrationHub・LDAP同期で必要
- ServiceNowインスタンス側からは直接オンプレミスにアクセスできないため必要

**MID Serverが必要なケース:**
- オンプレミスDBへのJDBC接続
- 社内LDAPサーバーとの同期
- SNMP/WMIを使ったDiscovery

**MID Serverが不要なケース:**
- クラウドシステムとのREST/SOAP連携（直接HTTPSで通信可能）

## REST Message（アウトバウンドREST）

ServiceNowから外部システムへHTTPリクエストを送る仕組み（テーブル: sys_rest_message）。

**Table API（インバウンド）との違い:**
- Table API: 外部 → ServiceNow（受け取る側）
- REST Message: ServiceNow → 外部（送る側）

```
var r = new sn_ws.RESTMessageV2('MyRestMessage', 'get');
r.setStringParameter('param', value);
var response = r.execute();
var body = response.getBody();
```

## Scripted REST API

ServiceNow上にカスタムREST APIエンドポイントを作る仕組み（テーブル: sys_ws_definition）。

**Table API との違い:**
- Table API: 既存テーブルへの汎用CRUD操作
- Scripted REST API: 独自ロジックを含むカスタムエンドポイント定義

## Transform Script フック（全種類）

- `onStart`: 変換処理の開始時（全レコード処理前に1回）
- `onBefore`: 各レコードの変換前
- `onAfter`: 各レコードの変換後
- `onComplete`: 変換処理の完了時（全レコード処理後に1回）

## 試験との接続

「Coalesce フィールドを指定しない場合、Transform の結果はどうなるか」→ 常に Insert される（既存レコードを無視して毎回新規挿入）。

「Import Set と Update Set の用途の違いを問う問題」→ Import Setは外部データの取り込み、Update Setは構成カスタマイズの移送。

「REST API Explorer の主な用途を問う問題」→ インスタンス内でAPIをテスト・検証できるツール。

「LDAP 統合でユーザーを定期同期するために使うのはどの機能か」→ Scheduled Import。LDAP Server定義だけでは同期されない。
