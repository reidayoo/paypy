import re
import json

def solve_aws_waf_challenge(html_response: str, user_agent: str) -> str:
    """AWS WAF Challengeを解決してトークンを取得"""
    try:
        from .awswaf.aws import AwsWaf
        
        goku_props_match = re.search(r'window\.gokuProps = ({.*?});', html_response, re.DOTALL)
        if not goku_props_match:
            raise Exception("AWS WAF Challenge: gokuPropsの抽出に失敗")
        
        goku_props_str = goku_props_match.group(1)
        goku_props = json.loads(goku_props_str)
        
        endpoint_match = re.search(r'src="https://([^"]+)/challenge\.js"', html_response)
        if not endpoint_match:
            raise Exception("AWS WAF Challenge: endpointの抽出に失敗")
        
        endpoint = endpoint_match.group(1)
        
        waf_solver = AwsWaf(
            goku_props=goku_props,
            endpoint=endpoint,
            domain="www.paypay.ne.jp",
            user_agent=user_agent
        )
        
        aws_waf_token = waf_solver()
        return aws_waf_token
        
    except ImportError as e:
        raise Exception(f"AWS WAF Challenge解決に必要なライブラリが不足しています: {e}\n`pip install -r requirements.txt` を実行してください。")
    except Exception as e:
        raise Exception(f"AWS WAF Challenge解決中にエラー: {str(e)}")
