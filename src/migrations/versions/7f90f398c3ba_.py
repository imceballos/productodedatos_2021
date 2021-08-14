"""empty message

Revision ID: 7f90f398c3ba
Revises: 
Create Date: 2021-08-12 21:11:54.633033

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7f90f398c3ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('classification_result',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('id_mother_image', mysql.INTEGER(display_width=11), nullable=True),
    sa.Column('box', sa.String(length=64), server_default=sa.text("''"), nullable=False),
    sa.Column('confidence', sa.Float(asdecimal=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entry_images',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('image_array', mysql.LONGTEXT(), nullable=True),
    sa.Column('confidence', sa.Float(asdecimal=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('entry_images')
    op.drop_table('classification_result')
    # ### end Alembic commands ###
