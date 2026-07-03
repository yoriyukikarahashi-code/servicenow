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
  (u_imp_xxxx / テーブル名は自動生成)
        │
        ├─ 手動ロード: Load All Records
        └─ 自動ロード: Scheduled Import (sys_trigger)
                │
                ▼
        Transform Map (sys_transform_map)
          ├─ Field Map (列の対応定義)
          │    例: [source: name] → [target: sys_user.first_name]
          ├─ Coalesce フィールド指定
          │    一致あり → Update (sys_user 既存レコード更新)
          │    一致なし → Insert (sys_user 新規行追加)
          │    未指定  → 常に Insert
          └─ Transform Script (変換前後のロジック: onBefore / onAfter)
                │
                ▼
        ターゲットテーブル (例: sys_user / cmdb_ci_server など)
                │
                ▼
        Import Set Run Log (結果確認)
          Inserted / Updated / Ignored / Skipped / Error

【インスタンス間移送: Update Set フロー】

  開発インスタンス (Dev)
    └─ Update Set を "In Progress" に設定
         └─ カスタマイズ作業 (フォーム / スクリプト / フロー など)
              → 変更が自動的に Update Set に記録 (sys_update_xml)
                   │
                   ▼
              Update Set をエクスポート (XML)
                   │
                   ▼
  本番インスタンス (Prod)
    └─ Update Set をインポート → Preview → Commit

【API / 外部連携】

  外部システム
    ├─ REST (Table API / Scripted REST)
    │    └─ REST API Explorer (All → System Web Services → REST API Explorer)
    ├─ SOAP (Web Service Import Sets)
    └─ IntegrationHub Spoke
         └─ Flow Designer → Action → HTTP Step など (有償)

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
6. 観察: Import Set Rows の各行に raw データが格納されていることを確認する

### タスク2: Transform Map を作成して Coalesce を確認する

1. **All → System Import Sets → Transform Maps** を開く
2. **New** をクリックし、Source Table に `u_imp_test_user_import`、Target Table に `sys_user` を設定して保存
3. **Field Maps** タブで **Auto Map Matching Fields** をクリックし、自動マッピングを生成する
4. email フィールドの Field Map を開き、**Coalesce** チェックボックスをオンにして保存
5. Transform Map 画面上部の **Transform** ボタンをクリックして実行する
6. 観察: Import Set Run Log で Inserted / Updated の件数を確認し、Coalesce の効果を体感する

### タスク3: Coalesce なしとの比較実験

1. タスク2と同じ CSV を再度 Load Data でロードする (新しい Import Set Run)
2. Transform Map の email の Coalesce チェックを**外して** Transform を実行する
3. 観察: sys_user に重複レコードが挿入される (Inserted のみで Updated が 0) ことを確認し、Coalesce の重要性を理解する

### タスク4: REST API Explorer で Table API を試す

1. **All → System Web Services → REST API Explorer** を開く
2. API Namespace: `now`、API Name: `Table API`、API Version: 最新を選択する
3. Method: GET、tableName: `incident`、sysparm_limit: `3` を入力して **Send** をクリックする
4. 観察: JSON レスポンスに incident レコードが返ることを確認し、Table API の構造を把握する
5. 次に Method: POST で incident を 1 件作成し、sys_id が発行されることを確認する

### タスク5: Update Set の作成と移送の流れを体験する

1. **All → System Update Sets → Local Update Sets** を開き、**New** で Update Set を作成して "In Progress" にする
2. Application: Global のまま、フォームに軽微な変更 (例: incident フォームにフィールド追加) を加える
3. Update Set に変更が記録されたことを **Preview Update Set** で確認する
4. **Export to XML** でファイルをダウンロードし、別 PDI があれば **Retrieved Update Sets** からインポートする
5. 観察: sys_update_xml テーブルに各変更の XML が 1 行ずつ記録されていることを確認する

### タスク6: Scheduled Import の設定を確認する

1. **All → System Import Sets → Scheduled Imports** を開く
2. **New** をクリックし、Name・Import Set Table・実行間隔 (例: Daily) を設定する
3. Data Source を選択し (タスク1で作成したもの)、**Execute Now** で即時実行する
4. 観察: Import Set Run が自動で作成され、ログに実行結果が記録されることを確認する

## 試験との接続

「Coalesce フィールドを指定しない場合、Transform の結果はどうなるか」
→ PDIでタスク3の重複挿入実験を行うと、Coalesce 未指定では既存レコードを無視して毎回 Insert が走ることが目で見てわかる。試験では「常に挿入される」が正解肢であることを体感として確認できる。

「Import Set と Update Set の用途の違いを問う問題」
→ PDIでタスク2 (外部 CSV → sys_user への取り込み) とタスク5 (カスタマイズの XML 移送) を両方実施すると、Import Set は"データ"・Update Set は"設定"という役割の違いが操作レベルで明確になる。試験では混同しやすいため、この体験が決め手になる。

「Transform Map の実行結果ステータス (Inserted / Updated / Ignored / Error) の意味を問う問題」
→ PDIのタスク2で Import Set Run Log を開くと各ステータスが色分けで表示される。Ignored は Transform Script で `ignore=true` を設定した行、Error は必須フィールド不足などと対応していることを Log の詳細行から読み取れ、選択肢を絞り込む根拠になる。

「REST API Explorer の主な用途を問う問題」
→ PDIのタスク4で実際に GET / POST を送信すると「インスタンス内でテスト・検証できるツール」であることが直感的にわかる。試験では「外部ツールなしで API をテストする方法」として REST API Explorer が正解肢になるパターンが頻出。

「LDAP 統合でユーザーを定期同期するために使うのはどの機能か」
→ PDIのタスク6で Scheduled Import の設定画面を確認すると、Data Source・Import Set Table・実行スケジュールの三点セットが LDAP 同期にもそのまま適用されることがわかる。試験では「LDAP Server 定義だけでは同期されない / Scheduled Import が必要」という引っかけが出るため、操作経験が判断を助ける。
