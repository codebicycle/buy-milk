"""empty message

Revision ID: 337195d88dcd
Revises: b312a7e62440
Create Date: 2017-07-13 19:57:49.790462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '337195d88dcd'
down_revision = 'b312a7e62440'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('url_token', sa.String(length=25), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'url_token')
    # ### end Alembic commands ###