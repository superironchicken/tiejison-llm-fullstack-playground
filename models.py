from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Conversation(Base):
    """一次对话。侧边栏里的每一条就是一个 Conversation。"""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 侧边栏显示的名字，可以先用第一条用户消息截断生成
    title: Mapped[str] = mapped_column(String(255), default="新对话")
    # server_default=func.now() 让数据库自己填时间，不依赖 Python 的时区
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # onupdate=func.now()：每次这行被更新时，数据库自动刷新这个时间，
    # 侧边栏就可以按"最近更新"排序
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 一个会话对应多条消息
    # cascade="all, delete-orphan"：删除会话时，ORM 会自动连带删除它的消息
    # （注意 SQLite 默认不强制外键约束，所以这里靠 ORM 层面的级联来保证）
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """一条消息，属于某个 Conversation。"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 外键指向 conversations.id，index=True 加快"按会话查消息"的速度
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    # role 只有 "user" / "assistant" 两种取值
    role: Mapped[str] = mapped_column(String(20))
    # 用 Text 而不是 String，因为回复可能很长，不受长度限制
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
