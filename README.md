# NCBC

NCBC 是一個 Discord 機器人，會從多個來源抓取新聞、透過 OpenAI 清理與整理內容，並在 Discord 論壇頻道自動發文與更新。

## 功能
- 抓取新聞（Yahoo、4Gamers；可擴充其他來源）
- 使用 OpenAI 清理內文、重寫標題、產生簡短評論
- 使用 Embedding 去重，並合併高度相似的新聞
- 在 Discord 論壇頻道建立/更新主題，套用合適標籤
- 具備排程自動抓取與手動指令

## 需求
- Python 3.10+
- Discord Bot Token
- OpenAI API Key

## 安裝與啟動
1) 建立 `.env` 檔並填入必要環境變數：
	- `DISCORD_TOKEN=...`
	- `OPENAI_API_KEY=...`

2) 建立與啟用虛擬環境，並安裝相依套件：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) 啟動機器人：

```bash
python main.py
```

## 本機測試
- 快速驗證：啟動機器人，確認能登入並同步指令。
- 排程任務：確認排程 cog 會執行並在論壇發文。

可選環境檢查：
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DISCORD_TOKEN set:', bool(os.getenv('DISCORD_TOKEN'))); print('OPENAI key set:', bool(os.getenv('OPENAI_API_KEY')))"
```

## 虛擬環境常用指令
- 建立：`python3 -m venv .venv`
- 啟用：`source .venv/bin/activate`
- 安裝依賴：`pip install -r requirements.txt`
- 關閉：`deactivate`

## 以 systemd 部署（Linux）
1) 建立專用系統使用者（建議）：
```bash
sudo useradd -r -m -d /opt/ncbc -s /usr/sbin/nologin ncbc
```

2) 放置專案到 `/opt/ncbc/NCBC`（或依實際情況調整路徑）：
```bash
sudo mkdir -p /opt/ncbc
sudo chown -R $USER:$USER /opt/ncbc
cp -r . /opt/ncbc/NCBC
```

3) 建立服務專用虛擬環境並安裝依賴：
```bash
python3 -m venv /opt/ncbc/NCBC/.venv
source /opt/ncbc/NCBC/.venv/bin/activate
pip install -r /opt/ncbc/NCBC/requirements.txt
deactivate
sudo chown -R ncbc:ncbc /opt/ncbc/NCBC
```

4) 建立環境變數檔 `/opt/ncbc/NCBC/.env`（擁有者 `ncbc`、權限 600）：
```bash
sudo -u ncbc bash -c 'cat > /opt/ncbc/NCBC/.env <<EOF
DISCORD_TOKEN=你的token
OPENAI_API_KEY=你的key
# 可選，未設定時預設 0.55
SIMILARITY_THRESHOLD=0.5
EOF
chmod 600 /opt/ncbc/NCBC/.env'
```

5) 建立 systemd 服務 `/etc/systemd/system/ncbc.service`：
```ini
[Unit]
Description=NCBC Discord News Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ncbc
Group=ncbc
WorkingDirectory=/opt/ncbc/NCBC
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/ncbc/NCBC/.env
ExecStart=/opt/ncbc/NCBC/.venv/bin/python /opt/ncbc/NCBC/main.py
Restart=on-failure
RestartSec=5s
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
```

6) 啟動並設定開機自動：
```bash
sudo systemctl daemon-reload
sudo systemctl start ncbc.service
sudo systemctl status ncbc.service --no-pager
sudo systemctl enable ncbc.service
```

7) 檢視日誌：
```bash
journalctl -u ncbc.service -f --no-pager
```

## 安全性注意事項
- `.env` 內含機密；已被 `.gitignore` 忽略。若外洩請立刻重置 Token/Key。
- 僅賦予機器人執行所需的最低 Discord 權限。

## 參數調整
在 `config/config.py` 可調整：
- `NEWS_FETCH_INTERVAL`：自動抓取間隔（秒）
- `NEWS_MEMORY`：記憶保留天數（用於去重與清理）
- `SIMILARITY_THRESHOLD`：相似度門檻，僅在 `config/config.py` 中調整（預設 0.55）

