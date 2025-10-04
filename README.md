💼 Expense Approval Management System

> A Smart Platform for Automated Expense Tracking and Multi-Level Approvals




---

👩‍💻 Participant Details

Name: Nitin Kushwaha
Project Title: Expense Approval Management System
Participation Type: Individual
Problem Statement: Automated Expense Tracking & Approval Flow


---

🚀 Overview

The Expense Approval Management System is a web-based platform designed to digitize and automate employee expense submissions and approvals.
It ensures transparency, reduces manual workload, and introduces multi-level, rule-based approvals in organizations.


---

🌟 Core Features

🔐 Role-Based Authentication

Secure JWT authentication

Three distinct roles:

Admin: Creates managers & employees, manages rules, views all data

Manager: Reviews and approves/rejects team expenses

Employee: Submits expenses for approval




---

💸 Expense Management Flow

Employees create and submit expenses

Managers and Admins approve or reject

Every action is tracked with timestamps and comments



---

🧠 Approval Rule Engine

Dynamic rule creation (by Admin)

Supports:

Percentage-based approvals

Specific approvers

Hybrid or Sequential logic


Fully configurable without changing backend code



---

💬 Approval Comments

Each approval/rejection has an associated comment

Provides transparency and clarity in decision-making



---

📊 (Upcoming) Analytics & Reports

Visualize expenses by category, employee, or month

Export data for auditing or finance review



---

🧾 (Planned) OCR Integration

Auto-read and extract data from uploaded receipts

Smart expense pre-filling using AI



---

🧱 Tech Stack
```
Layer	Technology

Frontend	Next.js (React + TailwindCSS)
Backend	FastAPI (Python)
Database	MySQL
Authentication	JWT (JSON Web Token)

```


---

🗄️ Database Overview
```
🧍‍♀️ users

Field	Type	Description

id	INT	Primary Key
username	VARCHAR	Unique identifier
password	VARCHAR	Hashed password
role	ENUM	admin / manager / employee
manager	VARCHAR	Assigned manager username



---

💰 expenses

Field	Type	Description

id	INT	Expense ID
employee	VARCHAR	Submitted by
amount	DECIMAL	Expense amount
category	VARCHAR	Expense category
description	TEXT	Expense details
status	VARCHAR	pending / approved / rejected
approvers	JSON	List of approvers
comments	JSON	Approval comments
created_at	TIMESTAMP	Submission time



---

⚙️ rules

Field	Type	Description

id	INT	Rule ID
name	VARCHAR	Rule title
type	VARCHAR	percentage / specific / hybrid / sequential
threshold	INT	Percentage threshold
approvers	JSON	List of approvers
specific_approver	VARCHAR	Specific approver username/role
is_active	BOOL	1 = Active, 0 = Inactive
```


---

🧩 Backend Modules
```bash
File	Purpose

main.py	Entry point for FastAPI
api/auth.py	Handles login, JWT creation
api/users.py	CRUD for users (Admin only)
api/expenses.py	Expense logic, approval/rejection
api/rules.py	Admin rule management
database_setup.py	Schema creation & setup

```

---

🖥️ Frontend Features (Next.js)

Role-based dashboards

Expense submission form with validations

Status filters: “All”, “Pending”, “Approved”, “Rejected”

Approve/Reject buttons (Manager/Admin view)

Admin-only access to rule and user management



---

🧠 Key Highlights

✅ Fully automated expense lifecycle<br>
✅ Secure, modular, and scalable<br>
✅ Configurable approval rules<br>
✅ Transparent decision tracking<br>
✅ Future-ready with analytics & OCR


---

🏁 Conclusion

> The Expense Approval Management System enables transparent, faster, and smarter expense handling through automation, structured roles, and rule-driven approvals — making organizational finance management effortless and efficient.




---

✨ Developed  by Nitin Kushwaha
(Individual Participant)

Mockup Link: https://link.excalidraw.com/l/65VNwvy7c4X/4WSLZDTrhkA
