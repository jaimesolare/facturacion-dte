"""Crear tabla para control de series y correlativos

Revision ID: 9a7b8c6d5e4f
Revises: 8ec9b6f47f70
Create Date: 2025-11-08 19:55:12.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a7b8c6d5e4f'
down_revision = '8ec9b6f47f70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'series',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo_dte', sa.String(length=2), nullable=False, comment="Tipo de DTE, ej: '01' para Factura"),
        sa.Column('serie', sa.String(length=10), nullable=False, comment="Serie para este tipo de DTE, ej: 'FAC-001'"),
        sa.Column('correlativo_actual', sa.Integer(), nullable=False, server_default='0', comment="Último correlativo utilizado para esta serie"),
        sa.UniqueConstraint('tipo_dte', 'serie', name='uq_tipo_dte_serie')
    )
    op.create_index(op.f('ix_series_tipo_dte'), 'series', ['tipo_dte'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_series_tipo_dte'), table_name='series')
    op.drop_table('series')
