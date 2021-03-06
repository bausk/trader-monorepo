"""

Revision ID: 26910f250a09
Revises: 68aea307b476
Create Date: 2020-05-17 21:32:21.110876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "26910f250a09"
down_revision = "68aea307b476"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "live_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=True),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("config_json", sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "backtest_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("config_json", sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(
            ["strategy_id"],
            ["strategies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "strategies", sa.Column("live_session_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "strategies", "live_sessions", ["live_session_id"], ["id"]
    )
    op.drop_column("strategies", "is_live")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "strategies",
        sa.Column("is_live", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "strategies", type_="foreignkey")
    op.drop_column("strategies", "live_session_id")
    op.drop_table("backtest_sessions")
    op.drop_table("live_sessions")
    # ### end Alembic commands ###
