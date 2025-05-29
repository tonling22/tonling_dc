# 使用官方 Python 輕量版映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝套件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案程式碼
COPY . .

# 暴露 port 7860（你 app.py 中的預設）
EXPOSE 7860

# 設定環境變數，讓 Flask 以生產模式跑（可視情況調整）
ENV FLASK_ENV=production

# 啟動 Flask app
CMD ["python", "linebot_app.py"]