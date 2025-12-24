# Shop-Server 配置（給 Cursor 使用）

建立於: 2025_12_24

## 快速參考

### 連線資訊
- **SSH 別名**: `shop-server`
- **IP 地址**: `192.168.196.154` (ZeroTier)
- **使用者**: `cbc`
- **認證**: SSH 金鑰（免密碼）
- **sudo**: 免密碼（NOPASSWD）

### 基本操作

```bash
# 連線
ssh shop-server

# 執行命令
ssh shop-server "command"

# 執行 sudo 命令
ssh shop-server "sudo command"

# 傳輸檔案
scp file shop-server:~/path/
scp shop-server:~/file local_path
```

## 詳細配置

### SSH 設定
- **私鑰**: `~/.ssh/shop_server_key`
- **公鑰**: `~/.ssh/shop_server_key.pub`
- **SSH Config**: `~/.ssh/config` (已配置 `shop-server` 別名)

### 伺服器資訊
- **作業系統**: Ubuntu Server
- **主機名稱**: `cbcserver`
- **家目錄**: `/home/cbc`
- **ZeroTier 網路 ID**: `9e1948db6329396d`

### 管理介面
- **Webmin**: https://192.168.196.154:10000
- **Portainer**: https://192.168.196.154:9000

## 常用操作

### 系統管理
```bash
# 檢查系統狀態
ssh shop-server "uptime && free -h && df -h"

# 服務管理
ssh shop-server "sudo systemctl status service_name"
ssh shop-server "sudo systemctl restart service_name"
ssh shop-server "sudo journalctl -u service_name -n 50"
```

### 檔案操作
```bash
# 查看檔案
ssh shop-server "cat ~/file_path"

# 編輯檔案
ssh shop-server "nano ~/file_path"

# 建立目錄
ssh shop-server "mkdir -p ~/directory_path"
```

### 進程管理
```bash
# 查看進程
ssh shop-server "ps aux | grep keyword"

# 系統資源
ssh shop-server "top -bn1 | head -20"
```

## 注意事項

1. **認證方式**: 僅使用金鑰認證，密碼認證已停用
2. **網路連線**: 需要 ZeroTier 連線正常
3. **sudo 權限**: 已配置免密碼，可直接執行 sudo 命令
4. **檔案權限**: 
   - 私鑰: `chmod 600 ~/.ssh/shop_server_key`
   - SSH config: `chmod 600 ~/.ssh/config`

## 相關文件

- `.cursor/SSH_SERVER_OPERATION.md` - 完整操作指南
- `pages/伺服器SSH配置.md` - 詳細配置記錄
- `.cursor/shop-server-config.json` - JSON 格式配置

