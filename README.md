# paypaypay

PayPay の非公式モバイル API クライアントライブラリです。
内部実装は [PayPaython-mobile](https://github.com/taka-4602/PayPaython-mobile) をベースにしています。

本ライブラリは PayPay 公式の提供するものではありません。PayPay 株式会社とは関係がありません。

## 注意事項

- PayPay アプリの内部 API を利用します。非公開のため、予告なく変更・停止される可能性があります。
- 利用にあたっては PayPay の利用規約をご確認ください。アカウントが制限されるリスクがあります。
- 本番運用や金銭取引の自動化への利用は推奨しません。発生した損害について開発者は責任を負いません。
- ログインを3回失敗するとアカウントが一時ロックされます。
- セッションを大量に作るとアカウント凍結の可能性があります。
- 日本国外からはアクセスできません（プロキシの利用が必要です）。

## インストール

```bash
pip install paypaypay
```

## 新規ログイン

```python
from PayPaython_mobile import PayPay

paypay = PayPay("080-1234-5678", "your_password")
paypay.login()
```

`login()` を呼ぶと 2FA 用のワンタイムリンクが発行されます。
別のデバイスで PayPay アプリに表示されたリンクを承認後、`login_confirm()` を呼びます。

```python
paypay.login_confirm("https://www.paypay.ne.jp/portal/oauth2/l?id=XXXX")
# URL全体でもIDだけでもOK

print(paypay.access_token)  # 約90日間有効
print(paypay.device_uuid)
```

### 登録済みデバイスでログイン

```python
paypay = PayPay("080-1234-5678", "your_password", device_uuid="登録済みのUUID")
paypay.login()
# URL入力不要
```

### アクセストークンでログイン（ログインをスキップ）

```python
paypay = PayPay(access_token="your_token")
```

## セッションの保存・復元

```python
paypay.save_session("my_session")

paypay = PayPay.load_session("my_session")
```

セッション情報は `~/.paypay/session.json` に保存されます。

## 残高取得

```python
balance = paypay.get_balance()
print(balance.all_balance)       # 利用可能な残高（合計）
print(balance.useable_balance)   # 使用可能な残高
print(balance.money)             # PayPayマネー
print(balance.money_light)       # PayPayマネーライト
print(balance.points)            # ポイント
print(balance.bank_balance)      # PayPay銀行残高
```

## プロフィール取得

```python
profile = paypay.get_profile()
print(profile.name)               # 表示名
print(profile.external_user_id)   # ユーザーID
print(profile.icon)               # アイコンURL
```

## 送金リンク

### リンクの確認

```python
link = paypay.link_check("https://pay.paypay.ne.jp/KT975hvzbH1EulTr")
# URLでもIDだけでもOK

print(link.amount)        # 金額
print(link.status)        # PENDING / SUCCESS / REJECTED / FAILED
print(link.has_password)  # パスコードの有無
print(link.sender_name)   # 送信者名
print(link.money)         # マネー分
print(link.money_light)   # マネーライト分
```

`web_api=True` でログインなしでも確認できます。

```python
paypay = PayPay()
link = paypay.link_check("KT975hvzbH1EulTr", web_api=True)
```

### リンクの受取・辞退・キャンセル

```python
paypay.link_receive("KT975hvzbH1EulTr", passcode="1234")
paypay.link_reject("KT975hvzbH1EulTr")
paypay.link_cancel("KT975hvzbH1EulTr")
```

`link_info` を渡すとリンクチェックをスキップします。

```python
info = paypay.link_check("KT975hvzbH1EulTr")
paypay.link_receive("KT975hvzbH1EulTr", link_info=info)
```

### リンクの作成

```python
result = paypay.create_link(amount=100, passcode="1234")
print(result.link)          # 送金リンクURL
print(result.chat_room_id)  # チャットルームID
print(result.order_id)      # 注文ID
```

ぽち袋モードにするには `pochibukuro=True` を指定します。

## 送金

```python
result = paypay.send_money(amount=100, receiver_id="external_user_id")
print(result.chat_room_id)
print(result.order_id)
```

## メッセージ送信

```python
paypay.send_message(chat_room_id="chat_room_id", message="ありがとう!")
```

## QRコード決済

```python
result = paypay.pay_qr_code(url="https://qr.paypay.ne.jp/XXXXX")
print(result.amount)         # 支払い金額
print(result.merchant_name)  # 店舗名
print(result.order_status)   # 決済ステータス
```

## PayPay銀行への出金

```python
result = paypay.cashout_to_paypaybank(amount=1000)
print(result.bank_name)
print(result.bank_account_number)
```

## その他の機能

```python
paypay.get_history(size=20)
paypay.get_history(size=20, cashback=True)

paypay.get_chat_rooms(size=20)
paypay.get_chat_room_messages(chat_room_id="chat_room_id")

paypay.get_point_history()

user = paypay.search_p2puser(user_id="paypay_id")
# is_global=True でグローバル検索（レート制限に注意）

room = paypay.initialize_chatroom(external_user_id="external_user_id")
print(room.chatroom_id)

p2p = paypay.create_p2pcode(amount=100)
print(p2p.url)

paypay.set_money_priority(paypay_money=False)  # マネーライト優先
paypay.set_money_priority(paypay_money=True)   # マネー優先
```

## 人間パターンシミュレータ

Bot検知を回避するため、バックグラウンドで人間らしいリクエストを送信します。

```python
paypay.start_alive_simulator(interval_range=(30, 180))

# ... 使用中 ...

paypay.stop_alive_simulator()
```

手動で送信する場合:

```python
paypay.alive()
```

## 例外クラス

| 例外クラス | 説明 |
| --- | --- |
| `PayPayError` | 汎用エラー |
| `PayPayLoginError` | ログイン失敗・トークン失効 |
| `PayPayNetWorkError` | ネットワークエラー |
| `P2PTemporaryHoldError` | 送金一時保留 |

```python
from PayPaython_mobile import PayPayError, PayPayLoginError, PayPayNetWorkError

try:
    paypay.get_balance()
except PayPayLoginError:
    print("ログインしてください")
except PayPayNetWorkError:
    print("ネットワークエラー")
```

## プロキシの使用

```python
paypay = PayPay("080-1234-5678", "password", proxy="http://host:port")
# または
paypay = PayPay.load_session("my_session", proxy="http://host:port")
```

## ライセンス

MIT License
