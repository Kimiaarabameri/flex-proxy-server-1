from flask import Flask, jsonify, request
import random
import string
import os
import time
import uuid
import requests

app = Flask(__name__)

# User-Agent list for iOS 16
ios_user_agents = [
    # iOS User-Agents - updated for version 3.104.1.0
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20G81",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20G75",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20F75",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20F66",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20E252",
]

# User-Agent list for Android - updated for version 2.512.0.0
android_user_agents = [
    "Amazon/2.512.0.0 (Linux; Android 13; SM-S918B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 13; SM-G998U Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 13; Pixel 7 Build/TQ2A.230505.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 12; SM-S906N Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
]

# آدرس سرور امضا - این را باید با آدرس واقعی سرور دوم تغییر دهید
SIGNATURE_SERVER = os.environ.get('SIGNATURE_SERVER', 'https://flex-proxy-server-2.onrender.com')
SIGNATURE_API_KEY = os.environ.get('SIGNATURE_API_KEY', '8c200fc0d90bc71acb837ea45eae90c8')

@app.route('/')
def home():
    return jsonify({
        "status": "Request Proxy Server is running",
        "message": "Use /accept/<api_key>/<marketplace_id> or /challenge/<api_key>/<marketplace_id> endpoints"
    })

# تابع کمکی برای انتخاب User-Agent مناسب براساس پلتفرم
def get_user_agent():
    # بررسی تنظیمات پلتفرم از فایل
    use_ios = False
    userdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "AMAZON_FLEX_BOT-main", "userdata", "use_ios")
    if os.path.exists(userdata_path):
        with open(userdata_path, "r") as f:
            use_ios = f.read().strip().lower() == "true"
    
    return random.choice(ios_user_agents if use_ios else android_user_agents)

@app.route('/accept/<api_key>/<marketplace_id>')
def accept_offer(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    try:
        # انتخاب User-Agent مناسب
        user_agent = get_user_agent()
        
        # درخواست امضا از سرور دوم
        signature_request = requests.get(
            f"{SIGNATURE_SERVER}/signature/{SIGNATURE_API_KEY}/{marketplace_id}",
            params={
                "method": "POST",
                "path": "/AcceptOffer",
                "request_id": str(uuid.uuid4())
            },
            timeout=5,
            headers={
                'User-Agent': user_agent,
                'Content-Type': 'application/json'
            }
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
        # انتخاب User-Agent مناسب
        user_agent = get_user_agent()
        
        # درخواست امضا از سرور دوم
        signature_request = requests.get(
            f"{SIGNATURE_SERVER}/signature/{SIGNATURE_API_KEY}/{marketplace_id}",
            params={
                "method": "POST",
                "path": "/ValidateChallenge",
                "request_id": str(uuid.uuid4())
            },
            timeout=5,
            headers={
                'User-Agent': user_agent,
                'Content-Type': 'application/json'
            }
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
        "user_agent": get_user_agent()
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 