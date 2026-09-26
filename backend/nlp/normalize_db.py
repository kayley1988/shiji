"""一次性规范化数据库的 normalized_content 字段"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from nlp.char_convert import normalize_poetry_text

engine = create_engine('sqlite:///E:/shiji/backend/shiyayaji.db')
Session = scoped_session(sessionmaker(bind=engine))
db = Session()

print('开始规范化 normalized_content...')

# 批量更新
all_lines = db.execute(text('SELECT id, content FROM poem_lines'))
updated = 0
for row in all_lines:
    line_id, content = row
    norm = normalize_poetry_text(content)
    db.execute(text(
        'UPDATE poem_lines SET normalized_content = :norm WHERE id = :id'
    ), {'norm': norm, 'id': line_id})
    updated += 1
    if updated % 50000 == 0:
        db.commit()
        print(f'  已更新 {updated} 条...')

db.commit()
print(f'规范化完成，共 {updated} 条')

# 验证
result = db.execute(text('SELECT content, normalized_content FROM poem_lines LIMIT 5'))
print('\n规范化前后对比:')
for row in result:
    print(f'  原文: {row[0]}')
    print(f'  规范: {row[1]}')
    print()

# 测试
result2 = db.execute(text('''
    SELECT pl.content, p.title
    FROM poem_lines pl
    JOIN poems p ON p.id = pl.poem_id
    WHERE p.title = '靜夜思'
    ORDER BY pl.line_no
'''))
print('靜夜思规范化后:')
for row in result2:
    print(f'  {row[0]} | {row[1]}')

# 搜索床前明月光
result3 = db.execute(text('''
    SELECT pl.content, p.title
    FROM poem_lines pl
    JOIN poems p ON p.id = pl.poem_id
    WHERE pl.normalized_content LIKE '%床前明月光%'
    LIMIT 5
'''))
print('\n搜索"床前明月光":')
for row in result3:
    print(f'  {row[0]} | {row[1]}')

db.close()
print('\n完成!')
