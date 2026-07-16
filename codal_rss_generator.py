# -*- coding: utf-8 -*-
"""
اسکریپت خودکار تولید فید RSS از سایت کدال (Codal.ir)
توسعه داده شده برای استفاده شخصی و حرفه‌ای.

راهنمای اجرا:
1. این اسکریپت را در یک سرور، هاست، یا سیستم محلی ذخیره کنید.
2. کتابخانه‌های پیش‌فرض پایتون برای این اسکریپت کافی هستند (نیاز به نصب هیچ پکیجی بورسی یا متفرقه‌ای نیست).
3. دستور اجرا: python codal_rss_generator.py
4. فایل خروجی 'codal_feed.xml' تولید می‌شود که می‌توانید آن را در فیدخوان خود (Feedly، Inoreader و ...) وارد کنید.
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# تنظیمات آدرس API کدال و نام فایل خروجی
CODAL_API_URL = "https://search.codal.ir/api/search/v2/q?search=true&PageNumber=1"
OUTPUT_FILE = "codal_feed.xml"

def fetch_codal_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://codal.ir",
        "Referer": "https://codal.ir/"
    }
    req = urllib.request.Request(CODAL_API_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching data from Codal API: {e}")
        return None

def build_rss(data):
    if not data or 'Letters' not in data:
        print("No letter data found in the API response.")
        return False
    
    # ایجاد ریشه RSS
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # اطلاعات کلی فید
    ET.SubElement(channel, "title").text = "آخرین اطلاعیه‌های کدال (Codal RSS)"
    ET.SubElement(channel, "link").text = "https://codal.ir"
    ET.SubElement(channel, "description").text = "فید RSS غیررسمی برای آخرین اطلاعیه‌های منتشر شده در سامانه کدال (نمادهای بورسی و فرابورسی)"
    ET.SubElement(channel, "language").text = "fa-ir"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    for letter in data.get('Letters', []):
        item = ET.SubElement(channel, "item")
        
        # مشخصات اطلاعیه
        publisher = letter.get('PublisherName', 'ناشر ناشناس')
        title_text = letter.get('Title', 'بدون عنوان')
        symbol = letter.get('Symbol', 'بدون نماد')
        sent_date = letter.get('SentDate', '')
        tracing_no = letter.get('TracingNo', '')
        
        # ساخت عنوان آیتم
        full_title = f"[{symbol}] {publisher} - {title_text}"
        ET.SubElement(item, "title").text = full_title
        
        # ساخت لینک کامل اطلاعیه
        relative_url = letter.get('Url', '')
        full_url = f"https://codal.ir{relative_url}" if relative_url else f"https://codal.ir/Reports/Decision.aspx?TracingNo={tracing_no}"
        ET.SubElement(item, "link").text = full_url
        
        # شناسه یکتا (GUID)
        guid = ET.SubElement(item, "guid", isPermaLink="false")
        guid.text = str(tracing_no) if tracing_no else full_url
        
        # تاریخ انتشار (استفاده از زمان کنونی به صورت استاندارد RFC 822)
        ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # توضیحات غنی به همراه HTML جهت نمایش بهتر در فیدخوان‌ها
        desc_html = f"""<![CDATA[
        <div dir="rtl" style="font-family: Tahoma, Arial, sans-serif; text-align: right; line-height: 1.6;">
            <p><strong>نماد بورسی:</strong> <span style="color: #007bff;">{symbol}</span></p>
            <p><strong>ناشر / شرکت:</strong> {publisher}</p>
            <p><strong>موضوع اطلاعیه:</strong> {title_text}</p>
            <p><strong>تاریخ ارسال به سامانه:</strong> {sent_date}</p>
            <p style="margin-top: 15px;">
                <a href="{full_url}" target="_blank" style="background-color: #28a745; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px;">مشاهده و دانلود اطلاعیه در کدال</a>
            </p>
        </div>
        ]]>"""
        ET.SubElement(item, "description").text = desc_html
        
    # زیباسازی و ذخیره خروجی XML
    tree = ET.ElementTree(rss)
    try:
        ET.indent(tree, space="  ", level=0)
    except AttributeError:
        pass
    
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Success! RSS saved to {OUTPUT_FILE}")
    return True

if __name__ == "__main__":
    print("Fetching latest data from Codal API...")
    data = fetch_codal_data()
    if data:
        build_rss(data)
    else:
        print("Could not complete. Please check internet connection or API availability.")
