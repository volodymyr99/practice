from typing import List, Optional
from flask_login import UserMixin
from sqlalchemy import Date, DateTime, ForeignKeyConstraint, Index, String, Text, text
from sqlalchemy.dialects.mysql import ENUM, INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Groups(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    year: Mapped[int] = mapped_column(INTEGER(11))

    orders_and_contracts: Mapped[List['OrdersAndContracts']] = relationship('OrdersAndContracts', back_populates='group')
    users: Mapped[List['Users']] = relationship('Users', back_populates='group')
    practice_assignments: Mapped[List['PracticeAssignments']] = relationship('PracticeAssignments', back_populates='group')


class IntegrationLogs(Base):
    __tablename__ = 'integration_logs'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    action: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[Optional[str]] = mapped_column(ENUM('success', 'failed'), server_default=text("'success'"))


class PracticeBases(Base):
    __tablename__ = 'practice_bases'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    address: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    contact_info: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))

    practice_assignments: Mapped[List['PracticeAssignments']] = relationship('PracticeAssignments', back_populates='base')


class PracticeStages(Base):
    __tablename__ = 'practice_stages'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))

    practice_assignments: Mapped[List['PracticeAssignments']] = relationship('PracticeAssignments', back_populates='practice_stage')


class OrdersAndContracts(Base):
    __tablename__ = 'orders_and_contracts'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE', name='orders_and_contracts_ibfk_1'),
        Index('group_id', 'group_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    group_id: Mapped[int] = mapped_column(INTEGER(11))
    file_type: Mapped[str] = mapped_column(ENUM('contract', 'order'))
    file_path: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    group: Mapped['Groups'] = relationship('Groups', back_populates='orders_and_contracts')


class Users(Base, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='SET NULL', name='users_ibfk_1'),
        Index('email', 'email', unique=True),
        Index('group_id', 'group_id'),
        Index('username', 'username', unique=True)
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    username: Mapped[str] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    password_hash: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    email: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    role: Mapped[str] = mapped_column(ENUM('student', 'teacher', 'staff'))
    full_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    group_id: Mapped[Optional[int]] = mapped_column(INTEGER(11))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    group: Mapped[Optional['Groups']] = relationship('Groups', back_populates='users')
    messages: Mapped[List['Messages']] = relationship('Messages', foreign_keys='[Messages.receiver_id]', back_populates='receiver')
    messages_: Mapped[List['Messages']] = relationship('Messages', foreign_keys='[Messages.sender_id]', back_populates='sender')
    practice_assignments: Mapped[List['PracticeAssignments']] = relationship('PracticeAssignments', foreign_keys='[PracticeAssignments.student_id]', back_populates='student')
    practice_assignments_: Mapped[List['PracticeAssignments']] = relationship('PracticeAssignments', foreign_keys='[PracticeAssignments.supervisor_id]', back_populates='supervisor')
    resources: Mapped[List['Resources']] = relationship('Resources', back_populates='users')
    practice_evaluations: Mapped[List['PracticeEvaluations']] = relationship('PracticeEvaluations', back_populates='evaluator')

    def get_id(self):
        return str(self.id)

class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE', name='messages_ibfk_2'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE', name='messages_ibfk_1'),
        Index('receiver_id', 'receiver_id'),
        Index('sender_id', 'sender_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    sender_id: Mapped[int] = mapped_column(INTEGER(11))
    receiver_id: Mapped[int] = mapped_column(INTEGER(11))
    message: Mapped[str] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    receiver: Mapped['Users'] = relationship('Users', foreign_keys=[receiver_id], back_populates='messages')
    sender: Mapped['Users'] = relationship('Users', foreign_keys=[sender_id], back_populates='messages_')


class PracticeAssignments(Base):
    __tablename__ = 'practice_assignments'
    __table_args__ = (
        ForeignKeyConstraint(['base_id'], ['practice_bases.id'], name='practice_assignments_ibfk_5'),
        ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE', name='practice_assignments_ibfk_2'),
        ForeignKeyConstraint(['practice_stage_id'], ['practice_stages.id'], name='practice_assignments_ibfk_3'),
        ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE', name='practice_assignments_ibfk_1'),
        ForeignKeyConstraint(['supervisor_id'], ['users.id'], name='practice_assignments_ibfk_4'),
        Index('base_id', 'base_id'),
        Index('group_id', 'group_id'),
        Index('practice_stage_id', 'practice_stage_id'),
        Index('student_id', 'student_id'),
        Index('supervisor_id', 'supervisor_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    student_id: Mapped[int] = mapped_column(INTEGER(11))
    group_id: Mapped[int] = mapped_column(INTEGER(11))
    practice_stage_id: Mapped[int] = mapped_column(INTEGER(11))
    supervisor_id: Mapped[int] = mapped_column(INTEGER(11))
    base_id: Mapped[int] = mapped_column(INTEGER(11))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(ENUM('assigned', 'in_progress', 'completed'), server_default=text("'assigned'"))

    base: Mapped['PracticeBases'] = relationship('PracticeBases', back_populates='practice_assignments')
    group: Mapped['Groups'] = relationship('Groups', back_populates='practice_assignments')
    practice_stage: Mapped['PracticeStages'] = relationship('PracticeStages', back_populates='practice_assignments')
    student: Mapped['Users'] = relationship('Users', foreign_keys=[student_id], back_populates='practice_assignments')
    supervisor: Mapped['Users'] = relationship('Users', foreign_keys=[supervisor_id], back_populates='practice_assignments_')
    practice_evaluations: Mapped[List['PracticeEvaluations']] = relationship('PracticeEvaluations', back_populates='assignment')
    practice_reports: Mapped[List['PracticeReports']] = relationship('PracticeReports', back_populates='assignment')


class Resources(Base):
    __tablename__ = 'resources'
    __table_args__ = (
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='resources_ibfk_1'),
        Index('uploaded_by', 'uploaded_by')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    uploaded_by: Mapped[int] = mapped_column(INTEGER(11))
    title: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    file_path: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    type: Mapped[Optional[str]] = mapped_column(ENUM('template', 'instruction', 'example'))

    users: Mapped['Users'] = relationship('Users', back_populates='resources')


class PracticeEvaluations(Base):
    __tablename__ = 'practice_evaluations'
    __table_args__ = (
        ForeignKeyConstraint(['assignment_id'], ['practice_assignments.id'], ondelete='CASCADE', name='practice_evaluations_ibfk_1'),
        ForeignKeyConstraint(['evaluator_id'], ['users.id'], name='practice_evaluations_ibfk_2'),
        Index('assignment_id', 'assignment_id'),
        Index('evaluator_id', 'evaluator_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    assignment_id: Mapped[int] = mapped_column(INTEGER(11))
    evaluator_id: Mapped[int] = mapped_column(INTEGER(11))
    grade: Mapped[Optional[str]] = mapped_column(String(10, 'utf8mb4_unicode_ci'))
    comments: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    assignment: Mapped['PracticeAssignments'] = relationship('PracticeAssignments', back_populates='practice_evaluations')
    evaluator: Mapped['Users'] = relationship('Users', back_populates='practice_evaluations')


class PracticeReports(Base):
    __tablename__ = 'practice_reports'
    __table_args__ = (
        ForeignKeyConstraint(['assignment_id'], ['practice_assignments.id'], ondelete='CASCADE', name='practice_reports_ibfk_1'),
        Index('assignment_id', 'assignment_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    assignment_id: Mapped[int] = mapped_column(INTEGER(11))
    title: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    file_path: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    github_link: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    photo_url: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    assignment: Mapped['PracticeAssignments'] = relationship('PracticeAssignments', back_populates='practice_reports')
