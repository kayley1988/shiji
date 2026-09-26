"""
诗词批量标注脚本 - 简化版
直接用 SQL 操作，不依赖 ORM 关系
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlite3
from nlp import get_tagger

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shiyayaji.db')


def get_db():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def ensure_tag(conn, cursor, tag_type: str, name: str) -> str:
    """确保标签存在，返回标签ID"""
    # 检查是否存在
    cursor.execute(
        "SELECT id FROM tags WHERE type = ? AND normalized_name = ?",
        (tag_type, name)
    )
    row = cursor.fetchone()
    
    if row:
        return row[0]
    
    # 创建新标签
    import uuid
    tag_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO tags (id, type, name, normalized_name, active) VALUES (?, ?, ?, ?, 1)",
        (tag_id, tag_type, name, name)
    )
    conn.commit()
    return tag_id


def add_tag_to_line(conn, cursor, line_id: str, tag_id: str, confidence: int):
    """给诗句添加标签"""
    # 检查是否已存在
    cursor.execute(
        "SELECT 1 FROM poem_line_tags WHERE poem_line_id = ? AND tag_id = ?",
        (line_id, tag_id)
    )
    if cursor.fetchone():
        return
    
    cursor.execute(
        "INSERT INTO poem_line_tags (poem_line_id, tag_id, confidence) VALUES (?, ?, ?)",
        (line_id, tag_id, confidence)
    )


def tag_all_poems():
    """给所有诗词打标签"""
    conn = get_db()
    cursor = conn.cursor()
    tagger = get_tagger()
    
    try:
        # 获取所有诗句
        cursor.execute("""
            SELECT pl.id, pl.content, pl.normalized_content
            FROM poem_lines pl
            JOIN poems p ON pl.poem_id = p.id
            WHERE p.review_status = 'APPROVED'
        """)
        lines = cursor.fetchall()
        
        print(f"共有 {len(lines)} 句诗需要标注")
        
        for i, (line_id, content, _) in enumerate(lines):
            # 标注
            result = tagger.tag(content)
            
            # 添加季节标签
            if result.season:
                tag_id = ensure_tag(conn, cursor, 'season', result.season)
                add_tag_to_line(conn, cursor, line_id, tag_id, 100)
            
            # 添加五行标签
            if result.element:
                tag_id = ensure_tag(conn, cursor, 'element', result.element)
                add_tag_to_line(conn, cursor, line_id, tag_id, 100)
            
            # 添加意象标签
            for imagery in result.imagery:
                tag_id = ensure_tag(conn, cursor, 'scene', imagery)
                add_tag_to_line(conn, cursor, line_id, tag_id, 90)
            
            # 添加情感标签
            for emotion in result.emotion:
                tag_id = ensure_tag(conn, cursor, 'scene', emotion)
                add_tag_to_line(conn, cursor, line_id, tag_id, 80)
            
            # 添加颜色标签
            if result.color:
                tag_id = ensure_tag(conn, cursor, 'scene', result.color)
                add_tag_to_line(conn, cursor, line_id, tag_id, 95)
            
            # 添加地域标签
            if result.region:
                tag_id = ensure_tag(conn, cursor, 'region', result.region)
                add_tag_to_line(conn, cursor, line_id, tag_id, 85)
            
            # 每10句提交一次
            if (i + 1) % 10 == 0:
                conn.commit()
                print(f"已处理 {i + 1}/{len(lines)}...")
        
        conn.commit()
        print(f"\n标注完成！共处理 {len(lines)} 句诗")
        
    finally:
        conn.close()


def show_stats():
    """显示统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 标签统计
        print("\n" + "=" * 50)
        print("标签统计")
        print("=" * 50)
        
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM tags 
            GROUP BY type
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} 个")
        
        # 平均标签数
        cursor.execute("""
            SELECT COUNT(*) / (SELECT COUNT(*) FROM poem_lines) as avg_tags
            FROM poem_line_tags
        """)
        row = cursor.fetchone()
        print(f"\n平均每句诗标签数: {row[0] if row else 0:.2f}")
        
        # 示例
        print("\n" + "=" * 50)
        print("标注示例")
        print("=" * 50)
        
        cursor.execute("""
            SELECT pl.content, GROUP_CONCAT(t.name, ', ') as tags
            FROM poem_lines pl
            JOIN poem_line_tags plt ON pl.id = plt.poem_line_id
            JOIN tags t ON plt.tag_id = t.id
            GROUP BY pl.id
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"\n{row[0]}")
            print(f"  标签: {row[1]}")
        
    finally:
        conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['tag', 'stats'], default='tag')
    args = parser.parse_args()
    
    if args.action == 'tag':
        tag_all_poems()
    elif args.action == 'stats':
        show_stats()
