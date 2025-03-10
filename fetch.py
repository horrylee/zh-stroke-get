import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import logging

# 設定儲存資料夾和目標 URL
BASE_DIR = "data"
LOG_FILE = "download_log.txt"
BASE_URL = "https://stroke-order.learningweb.moe.edu.tw/dictView.jsp?ID={}&la=0"

# 自訂 headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# 確保資料夾存在
Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

# 設置日誌記錄
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# 提取並保存 XML 的函數
def fetch_and_save_xml(unicode_dec):
    hex_code = f"{unicode_dec:x}".upper()
    filename = os.path.join(BASE_DIR, f"{hex_code}.xml")
    target_page = BASE_URL.format(unicode_dec)

    # 如果文件已存在，跳過
    if os.path.exists(filename):
        print(f"文件 {filename} 已存在，跳過...")
        return True

    # 設置無頭瀏覽器
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        print(f"載入目標網頁: {target_page}")
        driver.get(target_page)

        # 檢查頁面是否返回 "ID Miss!"
        page_content = driver.page_source
        if "ID Miss!" in page_content:
            logging.info(f"ID Miss! [U+{hex_code}]")
            print(f"網頁返回 'ID Miss! [U+{hex_code}]'，記錄到日誌並跳過")
            return False

        # 等待頁面主要元素出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "svg"))
        )
        # 額外等待 JavaScript 執行
        time.sleep(5)

        # 獲取頁面源碼
        page_content = driver.page_source

        # 直接提取 xml[unicode_dec] 的內容
        start_marker = f'xml[{unicode_dec}]="'
        end_marker = '";'
        start_idx = page_content.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = page_content.find(end_marker, start_idx)
            if end_idx != -1:
                xml_data = page_content[start_idx:end_idx]
                # 清理轉義字符並保存
                xml_content = xml_data.encode("utf-8").replace(b"\\n", b"\n").replace(b"\\t", b"\t").replace(b"\\\"", b"\"")
                with open(filename, "wb") as f:
                    f.write(xml_content)
                print(f"成功提取並保存 {hex_code}.xml")
                return True
            else:
                logging.info(f"Unicode {hex_code} (ID={unicode_dec}): 找到 'xml[{unicode_dec}]' 但未找到結束標記 ';'")
                print(f"未找到結束標記 ';'，記錄到日誌")
        else:
            logging.info(f"Unicode {hex_code} (ID={unicode_dec}): 未找到 'xml[{unicode_dec}]' 數據")
            print(f"未找到 XML 數據，記錄到日誌")

        # 保存頁面源碼以供檢查
        with open(f"page_source_{hex_code}.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        print(f"已保存源碼到 page_source_{hex_code}.html")

    except Exception as e:
        logging.info(f"ID Miss! [U+{hex_code}]")  # 將異常視為 ID Miss!
        print(f"發生錯誤，視為 'ID Miss! [U+{hex_code}]'，記錄到日誌並跳過")
        return False
    finally:
        if driver:
            driver.quit()

    return False

# 主程式
def main():
    # 中文字 Unicode 範圍：U+4E00 到 U+9FFF (19968 到 40959)
    start_unicode = 0x669C  # 19968
    end_unicode = 0x9FFF    # 40959

    print(f"開始下載所有中文字 XML (Unicode 範圍: {hex(start_unicode)} - {hex(end_unicode)})")
    for unicode_dec in range(start_unicode, end_unicode + 1):
        hex_code = f"{unicode_dec:x}".upper()
        print(f"\n處理 Unicode {hex_code} (十進位: {unicode_dec})...")
        success = fetch_and_save_xml(unicode_dec)
        if not success:
            print(f"無法下載 {hex_code}.xml，已記錄到 {LOG_FILE}")

    print("\n所有中文字 XML 下載完成！")

if __name__ == "__main__":
    main()