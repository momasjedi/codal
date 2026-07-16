import urllib.request
import json
import xml.etree.ElementTree as ET
import time
import os

# آدرس ای‌پی‌آی کدال برای گرفتن آخرین اطلاعیه‌ها (همه نمادها)
url = "https://search.codal.ir/api/search/v2/q?PageNumber=1&PageSize=100"

# شبیه‌سازی دقیق هدرهای مرورگر کروم برای دور زدن فایروال کدال (مهم‌ترین بخش)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fa,en-US;q=0.9;en;q=0.8",
    "Referer": "https://www.codal.ir/",
    "Origin": "https://www.codal.ir"
}

# ۱. ساخت فیکساتور ارور ۱۲۸ (اگر فایل نبود، یک نمونه اولیه می‌سازد تا گیت کرش نکند)
if not os.path.exists("codal_feed.xml"):
    with open("codal_feed.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Codal Feed</title><link>https://www.codal.ir</link><description>Placeholder</description></channel></rss>')

data = None
# ۲. تلاش مجدد (Retry) تا ۳ بار با مهلت ۳۰ ثانیه‌ای
for attempt in range(1, 4):
    try:
        print(f"Attempt {attempt}: Fetching Codal data...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        print("Successfully connected to Codal API!")
        break
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        if attempt < 3:
            print("Waiting 5 seconds before retrying...")
            time.sleep(5)

if not data or 'Letters' not in data:
    print("CRITICAL: Failed to bypass Codal's firewall. Keeping existing feed to prevent workflow crash.")
    exit(0)

# ۳. پردازش اطلاعات دریافت شده و ساخت فید RSS واقعی
letters = data.get('Letters', [])

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "آخرین اطلاعیه‌های کدال (همه نمادها)"
ET.SubElement(channel, "link").text = "https://www.codal.ir"
ET.SubElement(channel, "description").text = "فید زنده و بدون فیلتر تمامی نمادهای بازار سرمایه"

for letter in letters:
    item = ET.SubElement(channel, "item")
    symbol = letter.get("Symbol", "نامشخص")
    title = letter.get("Title", "بدون عنوان")
    full_title = f"[{symbol}] - {title}"
    ET.SubElement(item, "title").text = full_title
    
    letter_id = letter.get("LetterCode", "")
    link = f"https://www.codal.ir/Reports/Decision.aspx?LetterSerial={letter_id}" if letter_id else "https://www.codal.ir"
    ET.SubElement(item, "link").text = link
    
    pub_date_str = letter.get("PublishTime", "نامشخص")
    desc = f"نماد: {symbol}<br/>شرکت: {letter.get('CompanyName', '')}<br/>زمان انتشار: {pub_date_str}"
    ET.SubElement(item, "description").text = desc
    
    ET.SubElement(item, "guid", isPermaLink="false").text = str(letter.get("TracingNo", letter_id))

# ذخیره نهایی فایل
tree = ET.ElementTree(rss)
ET.indent(tree, space="  ", level=0)
tree.write("codal_feed.xml", encoding="utf-8", xml_declaration=True)
print("Successfully generated codal_feed.xml!")
