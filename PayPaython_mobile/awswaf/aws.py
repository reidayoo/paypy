import random, json

from curl_cffi import requests
from .verify import CHALLENGE_TYPES, network_bandwidth
from .fingerprint import get_fp


class AwsWaf:
    def __init__(self, goku_props: str,
                 endpoint: str,
                 domain: str,
                 user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                 ):
        self.session = requests.Session(impersonate="chrome")
        self.session.headers = {
            "connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "user-agent": user_agent,
            "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9"
        }
        self.goku_props = goku_props
        self.user_agent = user_agent
        self.domain = domain
        self.endpoint = endpoint

    @staticmethod
    def extract(html: str):
        goku_props = json.loads(html.split("window.gokuProps = ")[1].split(";")[0])
        host = html.split("src=\"https://")[1].split("/challenge.js")[0]
        return goku_props, host

    def get_inputs(self):
        return self.session.get(
            f"https://{self.endpoint}/inputs?client=browser").json()

    def _is_mp_verify(self, challenge_type: str) -> bool:
        """NetworkBandwidthチャレンジかどうかを判定"""
        return challenge_type == 'ha9faaffd31b4d5ede2a2e19d2d7fd525f66fee61911511960dcbb52d3c48ce25'

    def build_payload(self, inputs: dict):
        """ペイロードを構築する（mp_verifyとverifyで共通部分）"""
        verify_func = CHALLENGE_TYPES[inputs["challenge_type"]]
        checksum, fp = get_fp(self.user_agent)

        is_mp = self._is_mp_verify(inputs["challenge_type"])

        if is_mp:
            # mp_verify: solutionはFormDataのsolution_dataフィールドで送る
            # solution_metadataのsolutionはnull
            solution_data = verify_func(inputs["challenge"]["input"], checksum, inputs["difficulty"])
            solution_in_metadata = None
        else:
            # 従来のverify: solutionはJSON内に含める
            solution_data = None
            solution_in_metadata = verify_func(inputs["challenge"]["input"], checksum, inputs["difficulty"])

        payload = {
            "challenge": inputs["challenge"],
            "checksum": checksum,
            "solution": solution_in_metadata,
            "signals": [{"name": "Zoey", "value": {"Present": fp}}],
            "existing_token": None,
            "client": "Browser",
            "domain": self.domain,
            "metrics": [
                {"name": "2", "value": round(random.uniform(0.5, 3.0), 13), "unit": "2"},
                {"name": "100", "value": 1, "unit": "2"},
                {"name": "101", "value": 1, "unit": "2"},
                {"name": "102", "value": 1, "unit": "2"},
                {"name": "103", "value": random.randint(8, 12), "unit": "2"},
                {"name": "104", "value": 0, "unit": "2"},
                {"name": "105", "value": 0, "unit": "2"},
                {"name": "106", "value": 0, "unit": "2"},
                {"name": "107", "value": 0, "unit": "2"},
                {"name": "108", "value": 1, "unit": "2"},
                {"name": "undefined", "value": 1, "unit": "2"},
                {"name": "110", "value": 0, "unit": "2"},
                {"name": "111", "value": random.randint(20, 35), "unit": "2"},
                {"name": "112", "value": random.randint(1, 3), "unit": "2"},
                {"name": "undefined", "value": 1, "unit": "2"},
                {"name": "3", "value": round(random.uniform(8.0, 16.0), 15), "unit": "2"},
                {"name": "7", "value": 0, "unit": "4"},
                {"name": "1", "value": round(random.uniform(50.0, 90.0), 1), "unit": "2"},
                {"name": "4", "value": round(random.uniform(4.0, 8.0), 13), "unit": "2"},
                {"name": "5", "value": round(random.uniform(0.3, 1.5), 13), "unit": "2"},
                {"name": "6", "value": round(random.uniform(60.0, 90.0), 14), "unit": "2"},
                {"name": "8", "value": 1, "unit": "4"},
            ],
            "goku_props": self.goku_props,
        }

        return payload, solution_data, is_mp

    def verify(self, payload, solution_data=None, is_mp=False):
        """WAFトークンを取得する"""
        if is_mp:
            return self._mp_verify(payload, solution_data)
        else:
            return self._legacy_verify(payload)

    def _mp_verify(self, payload, solution_data):
        """mp_verify エンドポイント（FormData送信）"""
        self.session.headers.update({
            "origin": f"https://{self.domain}",
            "referer": f"https://{self.domain}/",
        })
        # Content-Typeはmultipart/form-dataだが、curl_cffiが自動設定するので削除
        if "content-type" in self.session.headers:
            del self.session.headers["content-type"]

        # FormDataとして送信
        # solution_data: Base64エンコードされたゼロバイト列
        # solution_metadata: JSON文字列（solutionはnull）
        metadata_json = json.dumps(payload, separators=(',', ':'))

        # curl_cffiではmultipartパラメータを使う
        from curl_cffi import CurlMime
        mp = CurlMime()
        mp.addpart(
            name="solution_data",
            content_type="text/plain",
            data=solution_data.encode('utf-8'),
        )
        mp.addpart(
            name="solution_metadata",
            content_type="application/json",
            data=metadata_json.encode('utf-8'),
        )

        res = self.session.post(
            f"https://{self.endpoint}/mp_verify",
            multipart=mp,
        )
        result = res.json()

        if result.get("token"):
            return result["token"]

        # トークンが返されなかった場合、新しいinputsで再試行
        if result.get("inputs"):
            raise Exception(f"mp_verify: トークン取得失敗、新しいチャレンジが返されました")

        raise Exception(f"mp_verify: 予期しないレスポンス: {result}")

    def _legacy_verify(self, payload):
        """従来の verify エンドポイント（JSON送信）"""
        self.session.headers.update({
            "content-type": "text/plain;charset=UTF-8",
            "origin": f"https://{self.domain}",
            "referer": f"https://{self.domain}/",
        })
        res = self.session.post(
            f"https://{self.endpoint}/verify",
            json=payload).json()
        return res["token"]

    def __call__(self, max_retries=3):
        """WAFチャレンジを解決してトークンを返す"""
        for attempt in range(max_retries):
            try:
                inputs = self.get_inputs()
                payload, solution_data, is_mp = self.build_payload(inputs)
                return self.verify(payload, solution_data, is_mp)
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                raise
