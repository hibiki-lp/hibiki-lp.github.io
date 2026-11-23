"""SwitchBotロックの Key ID と暗号鍵を取得する（標準ライブラリのみ）。

使い方:  python3 get_key.py
  - SwitchBotアカウント（ロックの所有者）のメールアドレスとパスワード、
    ロックのBLE MACアドレスを入力します。
  - 2段階認証が有効だと取得できません。一時的にオフにしてから実行してください。
  - パスワードはSwitchBotのサーバー(api.switchbot.net)にだけ送信されます。
"""
import json
import sys
import urllib.error
import urllib.request

CLIENT_ID = "5nnwmhmsa9xxskm14hd85lm9bm"  # SwitchBot公式アプリのID（pySwitchbotと同じ）


def call(url, data, token=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", **({"authorization": token} if token else {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            res = json.load(e)
        except Exception:
            raise SystemExit(f"エラー: サーバーが {e.code} を返しました")
    except Exception as e:
        raise SystemExit(f"エラー: 通信できませんでした ({e})")
    if res.get("statusCode") != 100:
        raise SystemExit(f"エラー: {res.get('message')} (statusCode {res.get('statusCode')})")
    return res["body"]


def main():
    mac = input("ロックのBLE MACアドレス (例 AA:BB:CC:DD:EE:FF): ").strip()
    mac = mac.replace(":", "").replace("-", "").upper()
    if len(mac) != 12:
        raise SystemExit("MACアドレスの形式が正しくありません")
    user = input("SwitchBotアカウントのメールアドレス: ").strip()
    # a-Shell では getpass が固まることがあるため通常入力にする（入力が画面に表示されます）
    pw = input("パスワード（画面に表示されます）: ").strip()

    acct = "https://account.api.switchbot.net/account/api/v1/user/"
    print("ログイン中…", flush=True)
    token = call(acct + "login", {
        "clientId": CLIENT_ID, "username": user, "password": pw,
        "grantType": "password", "verifyCode": "",
    })["access_token"]
    print("アカウント情報を取得中…", flush=True)
    region = call(acct + "userinfo", {}, token).get("botRegion") or "us"
    print(f"暗号鍵を取得中…（地域: {region}）", flush=True)
    body = call(
        f"https://wonderlabs.{region}.api.switchbot.net/wonder/keys/v1/communicate",
        {"device_mac": mac, "keyType": "user"}, token,
    )
    ck = body.get("communicationKey")
    if not ck:
        raise SystemExit("エラー: 暗号鍵が返ってきませんでした。MACアドレスと、ロックの所有者のアカウントか確認してください")
    print("\n取得できました。ウェブアプリの「設定」に入力してください。")
    print("Key ID :", ck["keyId"])
    print("暗号鍵 :", ck["key"])


if __name__ == "__main__":
    main()
