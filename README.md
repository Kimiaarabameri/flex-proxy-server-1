# Flex Proxy Server 1

این سرور پروکسی برای تولید امضاهای مورد نیاز برای درخواست‌های Amazon Flex استفاده می‌شود.

## نصب در Render

1. یک حساب در [Render](https://render.com) ایجاد کنید.
2. روی دکمه "New +" کلیک کنید و "Web Service" را انتخاب کنید.
3. مخزن گیت خود را به Render متصل کنید یا "Deploy from GitHub" را انتخاب کنید.
4. مسیر دایرکتوری `flex-proxy-server-1` را در تنظیمات وارد کنید.
5. تنظیمات زیر را انجام دهید:
   - نام: `flex-proxy-server-1`
   - محیط: `Python 3`
   - دستور ساخت: `pip install -r requirements.txt`
   - دستور شروع: `gunicorn app:app`

## متغیرهای محیطی

متغیرهای محیطی زیر را در Render تنظیم کنید:

- `API_KEY`: کلید API برای احراز هویت درخواست‌ها (مثال: `your-api-key-for-server1`)

## نحوه استفاده

پس از نصب، سرور روی آدرس زیر در دسترس خواهد بود:

```
https://<your-render-service-name>.onrender.com/
```

دو مسیر API در دسترس هستند:

1. `/accept/<api_key>/<marketplace_id>`: برای درخواست‌های پذیرش پیشنهاد
2. `/challenge/<api_key>/<marketplace_id>`: برای درخواست‌های تأیید چالش 