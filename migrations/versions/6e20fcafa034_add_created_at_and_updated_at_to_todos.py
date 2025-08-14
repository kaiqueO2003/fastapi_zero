"""add created_at and updated_at to todos

Revision ID: 6e20fcafa034
Revises: c073738a177e
Create Date: 2025-08-14 20:14:38.266033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e20fcafa034'
down_revision: Union[str, Sequence[str], None] = 'c073738a177e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Criar tabela temporária com os novos campos
    op.create_table(
        'todos_temp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('state', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # 2. Copiar dados da tabela antiga para a temporária, com timestamps atuais
    op.execute("""
        INSERT INTO todos_temp (id, title, description, state, user_id, created_at, updated_at)
        SELECT id, title, description, state, user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM todos
    """)

    # 3. Apagar tabela antiga
    op.drop_table('todos')

    # 4. Renomear tabela temporária para o nome original
    op.rename_table('todos_temp', 'todos')


def downgrade() -> None:
    """Downgrade schema."""
    # Apagar as colunas adicionadas recriando a tabela antiga
    op.create_table(
        'todos_temp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('state', sa.String, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
    )

    # Copiar os dados de volta (sem created_at e updated_at)
    op.execute("""
        INSERT INTO todos_temp (id, title, description, state, user_id)
        SELECT id, title, description, state, user_id
        FROM todos
    """)

    op.drop_table('todos')
    op.rename_table('todos_temp', 'todos')
