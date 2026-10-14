# paypy

Python client for PayPay mobile API.

## Install

```bash
pip install -e .
```

## Usage

```python
from PayPaython_mobile import PayPay

paypay = PayPay(access_token="your_token", device_uuid="your_uuid")

balance = paypay.get_balance()
print(balance.useable_balance)

paypay.save_session("my_session")

paypay2 = PayPay.load_session("my_session")
paypay2.start_alive_simulator()
```
