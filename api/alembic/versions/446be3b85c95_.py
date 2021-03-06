"""

Revision ID: 446be3b85c95
Revises: 
Create Date: 2020-03-09 21:25:09.721459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "446be3b85c95"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
