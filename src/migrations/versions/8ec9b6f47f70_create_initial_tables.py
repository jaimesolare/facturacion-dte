"""Create initial tables

Revision ID: 8ec9b6f47f70
Revises: 
Create Date: 2025-10-28 14:40:12.917840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ec9b6f47f70'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'dtes',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('codigo_generacion', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('numero_control', sa.String(), nullable=False),
        sa.Column('sello_recepcion', sa.String(), nullable=True),
        sa.Column('tipo_dte', sa.String(), nullable=False),
        sa.Column('estado', sa.String(), nullable=False),
        sa.Column('documento_json', sa.JSON(), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_recepcion_mh', sa.DateTime(), nullable=True),
        sa.Column('receptor_nit', sa.String(), nullable=True),
        sa.Column('monto_total', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dtes_codigo_generacion'), 'dtes', ['codigo_generacion'], unique=True)
    op.create_index(op.f('ix_dtes_numero_control'), 'dtes', ['numero_control'], unique=True)
    op.create_index(op.f('ix_dtes_sello_recepcion'), 'dtes', ['sello_recepcion'], unique=False)
    op.create_index(op.f('ix_dtes_tipo_dte'), 'dtes', ['tipo_dte'], unique=False)
    op.create_index(op.f('ix_dtes_estado'), 'dtes', ['estado'], unique=False)
    op.create_index(op.f('ix_dtes_receptor_nit'), 'dtes', ['receptor_nit'], unique=False)
    op.create_index(op.f('ix_dtes_monto_total'), 'dtes', ['monto_total'], unique=False)

    op.create_table(
        'eventos',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dte_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_evento', sa.String(), nullable=False),
        sa.Column('sello_recepcion_evento', sa.String(), nullable=True),
        sa.Column('evento_json', sa.JSON(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['dte_id'], ['dtes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_eventos_tipo_evento'), 'eventos', ['tipo_evento'], unique=False)

    op.create_table(
        'credenciales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ambiente', sa.String(), nullable=False),
        sa.Column('nit_usuario', sa.String(), nullable=False),
        sa.Column('api_password_encrypted', sa.String(), nullable=False),
        sa.Column('certificado_privado_encrypted', sa.String(), nullable=False),
        sa.Column('certificado_publico', sa.String(), nullable=False),
        sa.Column('token_jwt', sa.String(), nullable=True),
        sa.Column('token_expiracion', sa-DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ambiente')
    )


def downgrade() -> None:
    op.drop_table('credenciales')
    op.drop_index(op.f('ix_eventos_tipo_evento'), table_name='eventos')
    op.drop_table('eventos')
    op.drop_index(op.f('ix_dtes_monto_total'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_receptor_nit'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_estado'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_tipo_dte'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_sello_recepcion'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_numero_control'), table_name='dtes')
    op.drop_index(op.f('ix_dtes_codigo_generacion'), table_name='dtes')
    op.drop_table('dtes')
