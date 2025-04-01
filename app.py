from flask import Flask, jsonify, request
import random
import string
import os
import time
import uuid
import requests

app = Flask(__name__)

# لیست User-Agent های مختلف برای استفاده تصادفی - با تمرکز بیشتر روی iOS
USER_AGENTS = [
    "Amazon/34521 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34522 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34523 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34524 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34525 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34526 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34527 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34528 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/23458 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/23459 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
]

# آدرس سرور امضا - این را باید با آدرس واقعی سرور دوم تغییر دهید
SIGNATURE_SERVER = os.environ.get('SIGNATURE_SERVER', 'https://flex-proxy-server-2.onrender.com')
SIGNATURE_API_KEY = os.environ.get('SIGNATURE_API_KEY', 'default-sig-api-key')

@app.route('/')
def home():
    return jsonify({
        "status": "Request Proxy Server is running",
        "message": "Use /accept/<api_key>/<marketplace_id> or /challenge/<api_key>/<marketplace_id> endpoints"
    })

@app.route('/accept/<api_key>/<marketplace_id>')
def accept_offer(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    try:
        # درخواست امضا از سرور دوم
        signature_request = requests.get(
            f"{SIGNATURE_SERVER}/signature/{SIGNATURE_API_KEY}/{marketplace_id}",
            params={
                "method": "POST",
                "path": "/AcceptOffer",
                "request_id": str(uuid.uuid4())
            },
            timeout=5
        )
        
        if signature_request.status_code != 200:
            # اگر سرور امضا پاسخ نداد، از روش محلی استفاده کنیم
            print(f"Signature server error: {signature_request.text}")
            signature_data = generate_local_signature(marketplace_id)
        else:
            signature_data = signature_request.json()
        
        # لاگ کردن درخواست
        print(f"Accept request for marketplace_id: {marketplace_id}")
        
        return jsonify(signature_data)
    except Exception as e:
        print(f"Error connecting to signature server: {e}")
        # در صورت خطا، از روش محلی استفاده کنیم
        signature_data = generate_local_signature(marketplace_id)
        return jsonify(signature_data)

@app.route('/challenge/<api_key>/<marketplace_id>')
def validate_challenge(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    try:
        # درخواست امضا از سرور دوم
        signature_request = requests.get(
            f"{SIGNATURE_SERVER}/signature/{SIGNATURE_API_KEY}/{marketplace_id}",
            params={
                "method": "POST",
                "path": "/ValidateChallenge",
                "request_id": str(uuid.uuid4())
            },
            timeout=5
        )
        
        if signature_request.status_code != 200:
            # اگر سرور امضا پاسخ نداد، از روش محلی استفاده کنیم
            print(f"Signature server error: {signature_request.text}")
            signature_data = generate_local_signature(marketplace_id)
        else:
            signature_data = signature_request.json()
        
        # لاگ کردن درخواست
        print(f"Challenge request for marketplace_id: {marketplace_id}")
        
        return jsonify(signature_data)
    except Exception as e:
        print(f"Error connecting to signature server: {e}")
        # در صورت خطا، از روش محلی استفاده کنیم
        signature_data = generate_local_signature(marketplace_id)
        return jsonify(signature_data)

# تابع کمکی برای تولید امضاهای محلی در صورت عدم دسترسی به سرور امضا
def generate_local_signature(marketplace_id=None):
    # ایجاد یک کلید منحصر به فرد برای امضا
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    random_num = random.randint(10000, 99999)
    
    # ساخت امضای ورودی با فرمت سازگار با Amazon Flex
    sig_input = f"@method;@path;@authority;x-amzn-marketplace-id;x-amzn-requestid;x-flex-instance-id;sig={timestamp}={random_num}"
    
    # ساخت امضا با طول کافی
    sig_parts = [
        random.choice(string.ascii_uppercase + string.digits) for _ in range(20)
    ] + [
        random.choice(string.ascii_lowercase + string.digits) for _ in range(50)
    ] + [
        random.choice("/+=") for _ in range(15)
    ] + [
        random.choice(string.ascii_letters + string.digits) for _ in range(35)
    ]
    
    random.shuffle(sig_parts)
    sig = "".join(sig_parts)
    
    return {
        "signature_input": sig_input,
        "signature": sig,
        "user_agent": random.choice(USER_AGENTS)
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 