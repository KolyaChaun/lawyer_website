import base64
import hashlib
import json


def generate_liqpay_form(params: dict, public_key: str, private_key: str) -> str:
    data = base64.b64encode(json.dumps(params).encode()).decode()

    signature = base64.b64encode(
        hashlib.sha1((private_key + data + private_key).encode()).digest()
    ).decode()

    return f"""
    <form method="POST" action="https://www.liqpay.ua/api/3/checkout">
        <input type="hidden" name="data" value="{data}">
        <input type="hidden" name="signature" value="{signature}">
        <input type="submit" value="Оплатити" style="display:none">
    </form>
    <script>
        document.forms[0].submit();
    </script>
    """
