from database import get_db

def setup_database():
    conn = get_db()
    cur = conn.cursor()

    # users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(200) NOT NULL,
        role VARCHAR(50) NOT NULL,
        manager VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # expenses
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee VARCHAR(100) NOT NULL,
        amount DECIMAL(12,2) NOT NULL,
        currency VARCHAR(10) NOT NULL,
        category VARCHAR(100),
        description TEXT,
        status VARCHAR(30) DEFAULT 'pending',
        approvers JSON,
        comments JSON,
        votes JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # rules - approval rules configured by admin
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200),
        type VARCHAR(50), -- 'percentage' | 'specific' | 'hybrid' | 'sequence'
        threshold INT, -- used for percentage (0-100)
        approvers JSON, -- list of usernames who vote/are approvers
        specific_approver VARCHAR(100), -- username or role (string)
        seq JSON, -- ordered approvers (for sequence flow)
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # expense_approvers - each approver's decision in sequence
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expense_approvers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        expense_id INT NOT NULL,
        approver VARCHAR(100) NOT NULL,
        seq INT NOT NULL DEFAULT 0,
        decision ENUM('pending','approved','rejected') DEFAULT 'pending',
        decided_at DATETIME NULL,
        comment TEXT NULL,
        FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
    );
    """)

    # receipts - for uploaded expense receipts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        expense_id INT NOT NULL,
        filename VARCHAR(255),
        url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database setup completed.")

if __name__ == "__main__":
    setup_database()