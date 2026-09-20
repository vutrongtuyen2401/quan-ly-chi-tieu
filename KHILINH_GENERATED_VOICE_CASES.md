# KHÍ LINH VOICE INTELLIGENCE — TẬP TEST CASE GIỌNG NÓI TỰ NHIÊN

> Tập hợp các biến thể phát âm tự nhiên bằng tiếng Việt thực tế được sinh ra để kiểm thử toàn diện khả năng NLU/Voice của Khí Linh qua trình duyệt.

## 1. PHÂN BỐ DỮ LIỆU KIỂM THỬ GIỌNG NÓI
- **Các dạng số tiền:** Số thường (50000, 2000000), chữ viết (năm mươi nghìn, hai triệu), tiếng lóng đời thường (năm chục, 1 củ, 2 lốp, 3 lít, 5 xị), viết tắt (50k, 2tr, 1.5tr, 2 triệu rưỡi).
- **Các dạng câu:** Câu ngắn cụt, câu đầy đủ chủ vị, câu tu tiên khẩu ngữ, câu đảo trật tự từ, câu chứa từ đệm, câu tự sửa đổi giữa chừng.
- **Các tình huống:** Lệnh hoàn chỉnh 1 lượt, lệnh thiếu tham số, lệnh mơ hồ nhiều đối tượng, lệnh điều chỉnh (modify), lệnh hủy bỏ (cancel), lệnh thức tỉnh (wake word).

---

### WAKE_WORD
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `WAKE-01` | `WAKE_ONLY` | "Hệ thống" | Thức tỉnh Khí Linh (AWAKENING), chuyển sang LISTENING |
| `WAKE-02` | `WAKE_COMPOUND` | "Hệ thống, chuyển cho ta 1 triệu từ MoMo sang tiền mặt" | Thức tỉnh và lập tức giữ toàn bộ lệnh chuyển tiền |
| `WAKE-03` | `WAKE_NO_PREFIX_SLEEP` | "Hôm nay trời đẹp quá" | Không thức tỉnh khi đang SLEEPING |
| `WAKE-04` | `WAKE_COMPOUND_SLANG` | "Hệ thống, ghi ăn sáng năm chục ví tiền mặt" | Thức tỉnh và giữ lệnh chi tiêu 50.000 Đ |

### TRANSACTIONS
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `TX-01` | `CREATE_EXPENSE_NATURAL` | "Thêm chi tiêu 50 nghìn tiền ăn sáng" | Tạo chi tiêu 50.000 Đ, danh mục Ăn Uống |
| `TX-02` | `CREATE_EXPENSE_SLANG` | "Sáng nay ta ăn hết năm chục ví tiền mặt" | Tạo chi tiêu 50.000 Đ, ví Tiền Mặt |
| `TX-03` | `CREATE_EXPENSE_SHORT` | "Ăn trưa 65k" | Tạo chi tiêu 65.000 Đ |
| `TX-04` | `CREATE_EXPENSE_WORD_NUM` | "Mua sách tu tiên hết hai trăm ba mươi nghìn" | Tạo chi tiêu 230.000 Đ |
| `TX-05` | `CREATE_INCOME_NATURAL` | "Vừa nhận lương mười lăm triệu vào ví Vietcombank" | Tạo thu nhập 15.000.000 Đ vào Vietcombank |
| `TX-06` | `CREATE_INCOME_SLANG` | "Khách vừa bắn cho 2 củ vào MoMo" | Tạo thu nhập 2.000.000 Đ vào MoMo |
| `TX-07` | `DELETE_TRANSACTION_ID` | "Xóa giao dịch mới nhất giúp ta" | Hỏi xác nhận xóa giao dịch gần nhất |

### WALLETS_AND_TRANSFER
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `WAL-01` | `TRANSFER_ONE_SHOT` | "Chuyển 1 triệu từ MoMo sang tiền mặt" | Chuyển tiền MoMo -> Tiền mặt 1.000.000 Đ |
| `WAL-02` | `TRANSFER_SLANG` | "Rút một củ từ MoMo về tiền mặt" | Chuyển tiền MoMo -> Tiền mặt 1.000.000 Đ |
| `WAL-03` | `TRANSFER_INVERTED` | "Từ Vietcombank bắn sang MoMo năm trăm nghìn" | Chuyển tiền Vietcombank -> MoMo 500.000 Đ |
| `WAL-04` | `CREATE_WALLET_BASIC` | "Mở cho ta ví mới tên là Tiết Kiệm VCB" | Tạo ví Tiết Kiệm VCB loại ngân hàng |
| `WAL-05` | `DELETE_WALLET_PROTECTION` | "Xóa ví tiền mặt đi" | Cảnh báo bảo toàn hoặc hỏi xác nhận xóa ví |

### BUDGETS
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `BUD-01` | `CREATE_BUDGET_NATURAL` | "Tháng này cho ăn uống tối đa 2 triệu nhé" | Tạo hạn mức Ăn Uống 2.000.000 Đ tháng hiện tại |
| `BUD-02` | `CREATE_BUDGET_SLANG` | "Giới hạn mua sắm tháng này là 3 củ rưỡi" | Tạo hạn mức Mua Sắm 3.500.000 Đ |
| `BUD-03` | `BUDGET_STATUS_QUERY` | "Hạn mức ăn uống tháng này còn bao nhiêu" | Truy vấn tình trạng chi tiêu so với hạn mức |

### SAVING_GOALS
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `SAV-01` | `CREATE_SAVING_GOAL` | "Lập mục tiêu tiết kiệm mua phi kiếm 50 triệu" | Tạo mục tiêu Mua phi kiếm 50.000.000 Đ |
| `SAV-02` | `SAVING_DEPOSIT` | "Nạp 2 triệu vào mục tiêu mua phi kiếm" | Nạp 2.000.000 Đ vào mục tiêu |
| `SAV-03` | `SAVING_STATUS` | "Mục tiêu mua phi kiếm đã tích lũy được bao nhiêu" | Đọc tiến độ mục tiêu tiết kiệm |

### DEBTS
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `DEB-01` | `CREATE_DEBT_LEND` | "Cho Lý Mỗ mượn 500k" | Ghi nợ cho vay Lý Mỗ 500.000 Đ |
| `DEB-02` | `CREATE_DEBT_BORROW` | "Vay Đạo Hữu Nam 2 triệu" | Ghi nợ mượn Nam 2.000.000 Đ |
| `DEB-03` | `SETTLE_DEBT` | "Lý Mỗ đã trả nợ xong" | Quyết toán khoản nợ của Lý Mỗ |

### RECURRING
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `REC-01` | `CREATE_RECURRING` | "Đặt lịch chi tiền trọ 3 triệu vào ngày mùng 5 hàng tháng" | Tạo giao dịch định kỳ 3.000.000 Đ mỗi tháng |

### REPORTS_ANALYTICS
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `REP-01` | `SPENDING_OVERVIEW` | "Tháng này ta đã tiêu hết bao nhiêu linh thạch" | Báo cáo tổng chi tháng này |
| `REP-02` | `WALLET_BALANCE` | "Ví tiền mặt hiện tại còn bao nhiêu tiền" | Đọc số dư ví Tiền mặt |
| `REP-03` | `CATEGORY_DRILLDOWN` | "Khoản nào tốn kém nhất trong tháng" | Phân tích top danh mục chi tiêu cao nhất |

### DISCOURSE_AND_LIFECYCLE
| Case ID | Intent | Câu Nói Thực Tế (Utterance) | Kỳ Vọng (Expected Outcome) |
| :--- | :--- | :--- | :--- |
| `DIS-01` | `MISSING_PARAM_FLOW` | "Chuyển tiền cho ta -> Từ MoMo -> Sang Tiền mặt -> Một triệu -> Xác nhận" | Hỏi từng thông tin còn thiếu, duy trì context và execute |
| `DIS-02` | `AMBIGUITY_FLOW` | "Chuyển 500k từ ngân hàng sang tiền mặt" | Hỏi rõ ngân hàng nào khi có nhiều ví ngân hàng |
| `DIS-03` | `CORRECTION_MID_STREAM` | "Ăn sáng 50 nghìn... à nhầm, 70 nghìn" | Ghi nhận 70.000 Đ thay vì 50.000 Đ |
| `DIS-04` | `MODIFICATION_PENDING` | "Ăn sáng 50k -> (Confirm) -> Đổi thành 60k -> Xác nhận" | Đổi thành 60k và chỉ lưu 60k |
| `DIS-05` | `CANCELLATION_PENDING` | "Ăn sáng 50k -> (Confirm) -> Thôi hủy bỏ -> Xác nhận" | Hủy bỏ, 'Xác nhận' sau đó không thực thi |
| `DIS-06` | `INTENT_OVERRIDE` | "Chuyển 1 triệu -> (Confirm) -> Tháng này tiêu bao nhiêu" | Hủy pending transfer, trả lời thống kê |
| `DIS-07` | `SILENCE_TIMEOUT` | "Mở Khí Linh -> im lặng 10s" | Timeout an toàn, tự đóng live mode về sleeping |
