# PayPaython-mobile

Python用のPayPayモバイルAPIラッパー

## インストール

```bash
pip install paypaypay
```

GitHubから直接インストールする場合:

```bash
pip install git+https://github.com/konxjp/paypy.git
```

## 注意事項

- ログインを3回失敗するとアカウントが一時ロックされます
- セッションを大量に作るとアカウント凍結の可能性があります
- 日本国外からはアクセスできません（プロキシが必要）

## 使い方

### ログイン

```python
from PayPaython_mobile import PayPay

paypay = PayPay("080-1234-5678", "password")
paypay.login()

print(paypay.access_token)
print(paypay.device_uuid)
```

アクセストークンは約90日間有効です。

### アクセストークンでログイン（次回以降）

```python
paypay = PayPay(access_token="your_token", device_uuid="your_uuid")
```

### セッションの保存・復元

```python
paypay.save_session("my_session")

paypay = PayPay.load_session("my_session")
```

### 残高取得

```python
paypay.get_balance()
print(paypay.all_balance)
print(paypay.useable_balance)
print(paypay.money)
print(paypay.money_light)
print(paypay.point)
```

### プロフィール取得

```python
paypay.get_profile()
print(paypay.name)
print(paypay.external_user_id)
print(paypay.icon)
```

### 送金リンク

```python
link_info = paypay.link_check("https://pay.paypay.ne.jp/KT975hvzbH1EulTr")
print(paypay.link_amount)
print(paypay.link_status)

paypay.link_receive("KT975hvzbH1EulTr", passcode="1234")
paypay.link_reject("KT975hvzbH1EulTr")
paypay.link_cancel("KT975hvzbH1EulTr")

paypay.create_link(amount=100, passcode="1234")
print(paypay.created_link)
```

### 送金・メッセージ

```python
paypay.send_money(amount=100, receiver_id="external_user_id")
paypay.send_message(chat_room_id="chat_room_id", message="ありがとう!")
```

### その他

```python
paypay.get_history(size=20)
paypay.get_chat_rooms(size=20)
paypay.get_chat_room_messages(chat_room_id="chat_room_id")
paypay.get_point_history()
paypay.search_p2puser(user_id="paypay_id")
paypay.create_p2pcode(amount=100)
paypay.set_money_priority(paypay_money=False)
paypay.initialize_chatroom(external_user_id="external_user_id")
paypay.cashout_to_paypaybank(amount=1000)
paypay.pay_qr_code(url="qr_url")

paypay.start_alive_simulator()
paypay.stop_alive_simulator()
```
