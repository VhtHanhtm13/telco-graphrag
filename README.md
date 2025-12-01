Data: 
gồm 4 file json: 
    -> bảng dữ liệu thuộc hệ thống BSS/CRM của viễn thông, mô phỏng cách lưu trữ thông tin của thuê bao - gói cước - tài khoản - hạn mức. 
- SubcriberAgent.json: chứa toàn bộ thông tin của một thuê bao 
- ProductAgent.json : dữ liệu về gói cước/dịch vụ mà thuê bao có thể đăng kí 
- BalanceAgent.json: Dữ liệu về tài khoản tiền/quota, chứa thông tin về tài khoảng số dư mà thuê bao có
- AcmBalanceAgent: lưu mức sử dụng tích lũy của thuê bao 
Mối quan hệ của 4 file: 
    SubscriberAgent
   - balanceIdList → BalanceAgent
   - acmBalanceIdList → AcmBalanceAgent
   - productIdList → ProductAgent
-> Subcriber là trung tâm, Balance và ACM là tài khoản, Product là gói cước 

