from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite 数据库文件放在项目根目录，第一次连接时会自动创建
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

# check_same_thread=False 是 SQLite 特有的设置：
# SQLite 默认禁止跨线程复用连接，而 FastAPI 的请求可能在不同线程里执行，
# 所以必须关掉这个检查，否则会报 "SQLite objects created in a thread..." 错误
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal 是一个 session 工厂：每次调用它都会得到一个新的数据库会话
# autocommit=False：不自动提交，需要显式 commit，方便出错时回滚
# autoflush=False：不自动把内存改动刷进数据库，避免意外写入
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 所有 ORM 模型都要继承这个 Base，Base 负责收集表结构信息
class Base(DeclarativeBase):
    pass


# FastAPI 依赖注入用的函数：每个请求进来时开一个 session，请求结束自动关闭
# 用 yield 是因为这是"生成器依赖"，yield 之后的代码会在响应结束后执行
def get_db():
    b = SessionLocal()
    try:
        yield db
    finally:
        db.close()
