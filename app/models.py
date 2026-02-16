from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')))
classroom_students = Table(
    "classroom_students",
    Base.metadata,
    Column("classroom_id", Integer, ForeignKey("classrooms.id")),
    Column("student_id", Integer, ForeignKey("users.id")),
)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    users = relationship("User", secondary=user_roles, back_populates="roles")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    classrooms = relationship("Classroom", back_populates="instructor")
    enrolled_classrooms = relationship(
        "Classroom",
        secondary="classroom_students",
        back_populates="students"
    )

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    instructor = relationship("User", back_populates="classrooms")
    students = relationship("User", secondary="classroom_students", back_populates="enrolled_classrooms")
    lessons = relationship("Lesson", back_populates="classroom")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))

    classroom = relationship("Classroom", back_populates="lessons")
    sessions = relationship("Session", back_populates="lesson")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    lesson = relationship("Lesson", back_populates="sessions")