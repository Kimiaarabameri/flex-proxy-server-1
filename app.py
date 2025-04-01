from flask import Flask, jsonify, request
import random
import string
import os
import time

app = Flask(__name__)

# لیست User-Agent های مختلف برای استفاده تصادفی
USER_AGENTS = [
    "Amazon/23456 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Mobile Safari/537.36",
    "Amazon/23457 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.9999.99 Mobile Safari/537.36",
    "Amazon/23458 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/23459 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
]

# تابع کمکی برای تولید امضاهای تصادفی
def generate_signature_data():
    # تولید یک امضا تصادفی
    sig_input = f"@method;@path;@authority;x-amzn-marketplace-id;x-amzn-requestid;x-flex-instance-id;sig={int(time.time() * 1000)}={random.randint(1000, 9999)}"
    sig = "".join(random.choices(string.ascii_letters + string.digits + "/+=", k=120))
    
    return {
        "signature_input": sig_input,
        "signature": sig,
        "user_agent": random.choice(USER_AGENTS)
    }

@app.route('/')
def home():
    return jsonify({
        "status": "Server 1 is running",
        "message": "Use /accept/<api_key>/<marketplace_id> or /challenge/<api_key>/<marketplace_id> endpoints"
    })

@app.route('/accept/<api_key>/<marketplace_id>')
def accept_offer(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    # تولید داده‌های امضا
    signature_data = generate_signature_data()
    
    # لاگ کردن درخواست
    print(f"Accept request for marketplace_id: {marketplace_id}")
    
    return jsonify(signature_data)

@app.route('/challenge/<api_key>/<marketplace_id>')
def validate_challenge(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    # تولید داده‌های امضا
    signature_data = generate_signature_data()
    
    # لاگ کردن درخواست
    print(f"Challenge request for marketplace_id: {marketplace_id}")
    
    return jsonify(signature_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 