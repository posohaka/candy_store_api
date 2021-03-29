"""empty message

Revision ID: 584d317140a4
Revises: 
Create Date: 2021-03-29 07:57:34.131635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '584d317140a4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('couriers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('courier_type', sa.String(length=10), nullable=True),
    sa.Column('regions', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('working_hours', sa.ARRAY(sa.String(length=30)), nullable=True),
    sa.Column('count_delivery', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deliveries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('region', sa.Integer(), nullable=True),
    sa.Column('delivery_hours', sa.ARRAY(sa.String(length=30)), nullable=True),
    sa.Column('courier_id', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('finish_date', sa.DateTime(), nullable=True),
    sa.Column('delivery_time', sa.Float(), nullable=True),
    sa.Column('delivery_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ),
    sa.ForeignKeyConstraint(['delivery_id'], ['deliveries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.drop_table('deliveries')
    op.drop_table('couriers')
    # ### end Alembic commands ###
