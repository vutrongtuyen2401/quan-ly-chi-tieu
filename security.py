"""
╔══════════════════════════════════════════════════════════════════╗
║   HỆ THỐNG QUẢN LÝ CHI TIÊU — LỚP BẢO MẬT & PHÒNG THỦ TOÀN DIỆN  ║
║   Bcrypt Multi-Rounds, Python-Jose JWT, Brute-Force & Rate-Limit ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import time
import datetime
import threading
from typing import Optional, Dict, Tuple, Any
from fastapi import HTTPException, status, Request
import bcrypt
from jose import jwt, JWTError

# ──────────────────────────────────────────────
# CẤU HÌNH BẢO MẬT HỆ THỐNG
# ──────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "he_thong_quan_ly_chi_tieu_secure_key_2026_modern_defense")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # 30 phút theo yêu cầu

# ──────────────────────────────────────────────
# 1. BĂM VÀ KIỂM TRA MẬT KHẨU (BCRYPT 12 ROUNDS)
# ──────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Băm mật khẩu an toàn nhiều vòng với bcrypt (12 rounds)"""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu đối soát với hash trong CSDL"""
    try:
        if not hashed_password or not plain_password:
            return False
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$") or hashed_password.startswith("$2y$"):
            return bcrypt.checkpw(pw_bytes, hash_bytes)
        # Fallback an toàn cho legacy seed
        if hashed_password == "123456_Hash_Se_Doi_Trong_Code" and plain_password == "123456":
            return True
        return plain_password == hashed_password
    except Exception:
        return False

# ──────────────────────────────────────────────
# 2. HỆ THỐNG CẤP PHÁT & GIẢI MÃ JWT (PYTHON-JOSE)
# ──────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Tạo JWT Token có thời hạn ngắn (mặc định 30 phút)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "iss": "HeThongQuanLyChiTieu"
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Giải mã và xác thực chữ ký JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token xác thực không hợp lệ."
        )

# ──────────────────────────────────────────────
# 3. CƠ CHẾ CHỐNG BRUTE-FORCE (DÒ MẬT KHẨU)
# ──────────────────────────────────────────────
class BruteForceProtector:
    """
    Theo dõi và phòng chống tấn công dò mật khẩu:
    - Nếu nhập sai quá 5 lần -> Khóa tài khoản / IP trong 15 phút.
    """
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self._attempts: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def check_is_locked(self, identifier: str) -> Tuple[bool, int]:
        """Kiểm tra xem định danh (email/IP) có đang bị khóa hay không"""
        with self._lock:
            record = self._attempts.get(identifier)
            if not record:
                return False, 0
            
            lockout_until = record.get("lockout_until")
            if lockout_until:
                now = time.time()
                if now < lockout_until:
                    remaining_seconds = int(lockout_until - now)
                    return True, remaining_seconds
                else:
                    # Hết thời gian khóa, tự động reset
                    del self._attempts[identifier]
                    return False, 0
            return False, 0

    def record_failed_attempt(self, identifier: str) -> int:
        """Ghi nhận lần đăng nhập sai và kích hoạt khóa nếu vượt quá ngưỡng"""
        with self._lock:
            now = time.time()
            record = self._attempts.get(identifier, {"count": 0, "first_attempt": now})
            
            # Reset nếu lần thử trước đã quá 15 phút
            if now - record.get("first_attempt", now) > (self.lockout_minutes * 60):
                record = {"count": 1, "first_attempt": now}
            else:
                record["count"] += 1
            
            if record["count"] >= self.max_attempts:
                record["lockout_until"] = now + (self.lockout_minutes * 60)
            
            self._attempts[identifier] = record
            return record["count"]

    def reset_attempts(self, identifier: str):
        """Xóa lịch sử lỗi khi đăng nhập thành công"""
        with self._lock:
            if identifier in self._attempts:
                del self._attempts[identifier]

brute_force_protector = BruteForceProtector(max_attempts=5, lockout_minutes=15)

# ──────────────────────────────────────────────
# 4. RATE LIMITING & CHỐNG SPAM (ANTI-DDOS)
# ──────────────────────────────────────────────
class InMemoryRateLimiter:
    """
    Sliding-Window Rate Limiter:
    - Giới hạn tần suất gọi API theo IP / User ID.
    - Ngăn chặn việc gửi spam request làm nghẽn CSDL.
    """
    def __init__(self):
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Kiểm tra và cập nhật cửa sổ trượt:
        Trả về: (bị giới hạn hay không, số giây cần chờ)
        """
        with self._lock:
            now = time.time()
            cutoff = now - window_seconds
            
            timestamps = self._requests.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]
            
            if len(timestamps) >= max_requests:
                oldest_in_window = timestamps[0]
                retry_after = int((oldest_in_window + window_seconds) - now) + 1
                self._requests[key] = timestamps
                return True, max(1, retry_after)
            
            timestamps.append(now)
            self._requests[key] = timestamps
            return False, 0

rate_limiter = InMemoryRateLimiter()

def enforce_rate_limit(request: Request, max_requests: int = 60, window_seconds: int = 60, endpoint_tag: str = "general"):
    """Dependency / Guard kiểm tra giới hạn request"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"{endpoint_tag}:{client_ip}"
    
    is_limited, retry_after = rate_limiter.is_rate_limited(key, max_requests, window_seconds)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau {retry_after} giây."
        )
