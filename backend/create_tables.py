"""创建 poem_notes 表"""
import pymysql
conn = pymysql.connect(
    host='127.0.0.1', port=3307, user='root',
    password='Zhouqian@2026', database='shiyayaji', charset='utf8mb4'
)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS poem_notes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    poem_id VARCHAR(36) NOT NULL,
    line_text VARCHAR(500) NOT NULL,
    poem_title VARCHAR(200),
    poet_name VARCHAR(100),
    note TEXT,
    mood_tag VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_poem_notes_user (user_id),
    INDEX ix_poem_notes_mood (mood_tag)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
''')
conn.commit()
print('poem_notes 表创建成功')
cur.close()
conn.close()
