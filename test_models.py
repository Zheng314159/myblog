#!/usr/bin/env python3
"""
模型测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

async def test_models():
    """测试所有模型"""
    try:
        print("🔍 测试模型导入...")
        
        # 测试模型导入
        from app.models.user import User, UserCreate, UserUpdate, UserResponse, UserRole
        print("✅ User 模型导入成功")
        
        from app.models.article import Article, ArticleCreate, ArticleUpdate, ArticleResponse, ArticleStatus
        print("✅ Article 模型导入成功")
        
        from app.models.comment import Comment, CommentCreate, CommentUpdate, CommentResponse
        print("✅ Comment 模型导入成功")
        
        from app.models.tag import Tag, TagCreate, TagUpdate, TagResponse, ArticleTag
        print("✅ Tag 模型导入成功")
        
        # 测试模型实例化
        print("\n🔍 测试模型实例化...")
        
        # 创建用户
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        print("✅ UserCreate 实例化成功")
        
        # 创建文章
        article_data = ArticleCreate(
            title="Test Article",
            content="This is a test article content.",
            summary="Test summary",
            status=ArticleStatus.DRAFT
        )
        print("✅ ArticleCreate 实例化成功")
        
        # 创建评论
        comment_data = CommentCreate(
            content="This is a test comment.",
            parent_id=None
        )
        print("✅ CommentCreate 实例化成功")
        
        # 创建标签
        tag_data = TagCreate(
            name="test-tag",
            description="Test tag description"
        )
        print("✅ TagCreate 实例化成功")
        
        # 测试枚举
        print(f"✅ UserRole 枚举: {UserRole.ADMIN}")
        print(f"✅ ArticleStatus 枚举: {ArticleStatus.PUBLISHED}")
        
        print("\n🎉 所有模型测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """测试数据库连接"""
    try:
        print("\n🔍 测试数据库连接...")
        
        from app.core.database import engine, create_db_and_tables
        
        # 创建数据库表
        await create_db_and_tables()
        print("✅ 数据库表创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 模型和数据库测试")
    print("=" * 50)
    
    # 测试模型
    models_result = await test_models()
    
    # 测试数据库
    db_result = await test_database_connection()
    
    print("\n" + "=" * 50)
    if models_result and db_result:
        print("🎉 所有测试通过！")
        print("✅ 模型定义正确")
        print("✅ 数据库连接正常")
        print("✅ 系统可以正常启动")
    else:
        print("❌ 部分测试失败")
        if not models_result:
            print("❌ 模型测试失败")
        if not db_result:
            print("❌ 数据库测试失败")

if __name__ == "__main__":
    asyncio.run(main()) 