"""add 99k users

Revision ID: f2567dd682e6
Revises:
Create Date: 2024-03-17 09:27:16.413072

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2567dd682e6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "99_users_dataset",
        sa.Column("identifierHash", sa.BigInteger, nullable=False),
        sa.Column("type", sa.String),
        sa.Column("country", sa.String),
        sa.Column("language", sa.String),
        sa.Column("socialNbFollowers", sa.Integer),
        sa.Column("socialNbFollows", sa.Integer),
        sa.Column("socialProductsLiked", sa.Integer),
        sa.Column("productsListed", sa.Integer),
        sa.Column("productsSold", sa.Integer),
        sa.Column("productsPassRate", sa.Float),
        sa.Column("productsWished", sa.Integer),
        sa.Column("productsBought", sa.Integer),
        sa.Column("gender", sa.String),
        sa.Column("civilityGenderId", sa.Integer),
        sa.Column("civilityTitle", sa.String),
        sa.Column("hasAnyApp", sa.Boolean),
        sa.Column("hasAndroidApp", sa.Boolean),
        sa.Column("hasIosApp", sa.Boolean),
        sa.Column("hasProfilePicture", sa.Boolean),
        sa.Column("daysSinceLastLogin", sa.Integer),
        sa.Column("seniority", sa.Integer),
        sa.Column("seniorityAsMonths", sa.Float),
        sa.Column("seniorityAsYears", sa.Float),
        sa.Column("countryCode", sa.String),
    )


def downgrade() -> None:
    op.drop_table("99_users_dataset")
