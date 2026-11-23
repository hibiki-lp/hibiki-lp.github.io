"""SwitchBotロックの Key ID と暗号鍵を取得する（標準ライブラリのみ）。

使い方:  python3 get_key.py
  - SwitchBotアカウント（ロックの所有者）のメールアドレスとパスワード、
    ロックのBLE MACアドレスを入力します。
  - 2段階認証が有効だと取得できません。一時的にオフにしてから実行してください。
  - パスワードはSwitchBotのサーバー(api.switchbot.net)にだけ送信されます。
"""
import getpass
import json
import urllib.request

CLIENT_ID = "5nnwmhmsa9xxskm14hd85lm9bm"  # SwitchBot公式アプリのID（pySwitchbotと同じ）


def call(url, data, token=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", **({"authorization": token} if token else {})},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.load(r)
    if res.get("statusCode") != 100:
        raise SystemExit(f"エラー: {res.get('message')} (statusCode {res.get('statusCode')})")
    return res["body"]


def main():
    mac = input("ロックのBLE MACアドレス (例 AA:BB:CC:DD:EE:FF): ").strip()
    mac = mac.replace(":", "").replace("-", "").upper()
    if len(mac) != 12:
        raise SystemExit("MACアドレスの形式が正しくありません")
    user = input("SwitchBotアカウントのメールアドレス: ").strip()
    pw = getpass.getpass("パスワード（入力は表示されません）: ")

    acct = "https://account.api.switchbot.net/account/api/v1/user/"
    token = call(acct + "login", {
        "clientId": CLIENT_ID, "username": user, "password": pw,
        "grantType": "password", "verifyCode": "",
    })["access_token"]
    region = call(acct + "userinfo", {}, token).get("botRegion") or "us"
    body = call(
        f"https://wonderlabs.{region}.api.switchbot.net/wonder/keys/v1/communicate",
        {"device_mac": mac, "keyType": "user"}, token,
    )
    ck = body["communicationKey"]
    print("\n取得できました。ウェブアプリの「設定」に入力してください。")
    print("Key ID :", ck["keyId"])
    print("暗号鍵 :", ck["key"])


if __name__ == "__main__":
    main()
