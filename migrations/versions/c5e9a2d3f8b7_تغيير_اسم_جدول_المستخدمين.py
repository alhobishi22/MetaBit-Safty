"""تغيير اسم جدول المستخدمين

Revision ID: c5e9a2d3f8b7
Revises: 8224d9de3aa9
Create Date: 2025-03-18 01:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError


# revision identifiers, used by Alembic.
revision = 'c5e9a2d3f8b7'
down_revision = '8224d9de3aa9'
branch_labels = None
depends_on = None


def upgrade():
    # تغيير اسم جدول المستخدمين من user إلى users
    try:
        op.rename_table('user', 'users')
        
        # تحديث مفتاح أجنبي في جدول التقارير
        with op.batch_alter_table('report') as batch_op:
            batch_op.drop_constraint('fk_report_user_id_user', type_='foreignkey')
            batch_op.create_foreign_key('fk_report_user_id_users', 'users', ['user_id'], ['id'])
    except ProgrammingError:
        # في حالة عدم وجود الجدول أصلاً، نتجاهل الخطأ
        pass


def downgrade():
    try:
        # إعادة اسم الجدول إلى user
        with op.batch_alter_table('report') as batch_op:
            batch_op.drop_constraint('fk_report_user_id_users', type_='foreignkey')
            batch_op.create_foreign_key('fk_report_user_id_user', 'user', ['user_id'], ['id'])
        
        op.rename_table('users', 'user')
    except ProgrammingError:
        # في حالة عدم وجود الجدول، نتجاهل الخطأ
        pass
