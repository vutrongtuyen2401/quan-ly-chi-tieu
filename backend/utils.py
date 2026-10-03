"""Hàm tiện ích dùng chung."""


def vnd(amount) -> str:
    """Định dạng số tiền kiểu Việt Nam: 1234567 -> 1.234.567"""
    return f"{amount:,.0f}".replace(",", ".")
