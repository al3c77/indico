"""Add abstracts tables

Revision ID: 2ce1756a2f12
Revises: 5596683819c9
Create Date: 2016-08-22 14:57:28.005919
"""

import sqlalchemy as sa
from alembic import op
from indico.core.db.sqlalchemy import UTCDateTime, PyIntEnum
from indico.modules.events.abstracts.models.persons import AuthorType
from indico.modules.events.abstracts.models.reviews import ReviewAction
from indico.modules.users.models.users import UserTitle
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2ce1756a2f12'
down_revision = '5596683819c9'


def upgrade():
    op.drop_constraint('fk_contributions_abstract_id_abstracts', 'contributions', schema='events')
    op.drop_constraint('fk_abstract_field_values_abstract_id_abstracts', 'abstract_field_values',
                       schema='event_abstracts')
    op.drop_constraint('fk_judgments_abstract_id_abstracts', 'judgments', schema='event_abstracts')

    op.rename_table('abstracts', 'legacy_abstracts', schema='event_abstracts')
    op.execute('''
        ALTER INDEX event_abstracts.ix_abstracts_accepted_track_id RENAME TO ix_legacy_abstracts_accepted_track_id;
        ALTER INDEX event_abstracts.ix_abstracts_accepted_type_id RENAME TO ix_legacy_abstracts_accepted_type_id;
        ALTER INDEX event_abstracts.ix_abstracts_event_id RENAME TO ix_legacy_abstracts_event_id;
        ALTER INDEX event_abstracts.ix_abstracts_type_id RENAME TO ix_legacy_abstracts_type_id;
        ALTER SEQUENCE event_abstracts.abstracts_id_seq RENAME TO legacy_abstracts_id_seq;
        ALTER TABLE event_abstracts.legacy_abstracts RENAME CONSTRAINT pk_abstracts TO pk_legacy_abstracts;
        ALTER TABLE event_abstracts.legacy_abstracts RENAME CONSTRAINT
            fk_abstracts_accepted_type_id_contribution_types TO fk_legacy_abstracts_accepted_type_id_contribution_types;
        ALTER TABLE event_abstracts.legacy_abstracts RENAME CONSTRAINT
            fk_abstracts_event_id_events TO fk_legacy_abstracts_event_id_events;
        ALTER TABLE event_abstracts.legacy_abstracts RENAME CONSTRAINT
            fk_abstracts_type_id_contribution_types TO fk_legacy_abstracts_type_id_contribution_types;
        ALTER TABLE event_abstracts.legacy_abstracts RENAME CONSTRAINT
            uq_abstracts_friendly_id_event_id TO uq_legacy_abstracts_friendly_id_event_id;
    ''')

    op.create_table(
        'abstracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('friendly_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False, index=True),
        sa.Column('type_id', sa.Integer(), nullable=True, index=True),
        sa.Column('final_track_id', sa.Integer(), nullable=True, index=True),
        sa.Column('final_type_id', sa.Integer(), nullable=True, index=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.events.id']),
        sa.ForeignKeyConstraint(['final_type_id'], ['events.contribution_types.id']),
        sa.ForeignKeyConstraint(['type_id'], ['events.contribution_types.id']),
        sa.ForeignKeyConstraint(['final_track_id'], ['events.tracks.id']),
        sa.UniqueConstraint('friendly_id', 'event_id'),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )

    op.create_table(
        'email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('include_authors', sa.Boolean(), nullable=False),
        sa.Column('include_submitter', sa.Boolean(), nullable=False),
        sa.Column('include_coauthors', sa.Boolean(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('reply_to_address', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False, index=True),
        sa.Column('extra_cc_emails', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('stop_on_match', sa.Boolean(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('conditions', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.events.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )

    op.create_table(
        'abstract_person_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('abstract_id', sa.Integer(), nullable=False, index=True),
        sa.Column('person_id', sa.Integer(), nullable=False, index=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('title', PyIntEnum(UserTitle), nullable=True),
        sa.Column('affiliation', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_speaker', sa.Boolean(), nullable=False),
        sa.Column('author_type', PyIntEnum(AuthorType), nullable=False),
        sa.ForeignKeyConstraint(['abstract_id'], ['event_abstracts.abstracts.id']),
        sa.ForeignKeyConstraint(['person_id'], ['events.persons.id']),
        sa.UniqueConstraint('person_id', 'abstract_id'),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )

    op.create_table(
        'abstract_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('abstract_id', sa.Integer(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('modified_by_id', sa.Integer(), nullable=True, index=True),
        sa.Column('created_dt', UTCDateTime, nullable=False),
        sa.Column('modified_dt', UTCDateTime, nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['abstract_id'], ['event_abstracts.abstracts.id']),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.users.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )

    op.create_table(
        'abstract_review_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False, index=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.events.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )

    op.create_table(
        'abstract_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('abstract_id', sa.Integer(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('track_id', sa.Integer(), nullable=True, index=True),
        sa.Column('created_dt', UTCDateTime, nullable=False),
        sa.Column('modified_dt', UTCDateTime, nullable=True),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('proposed_action', PyIntEnum(ReviewAction), nullable=False),
        sa.Column('proposed_track_id', sa.Integer(), nullable=True, index=True),
        sa.Column('proposed_contribution_type_id', sa.Integer(), nullable=True, index=True),
        sa.ForeignKeyConstraint(['abstract_id'], ['event_abstracts.abstracts.id']),
        sa.ForeignKeyConstraint(['proposed_track_id'], ['events.tracks.id']),
        sa.ForeignKeyConstraint(['proposed_contribution_type_id'], ['events.contribution_types.id']),
        sa.ForeignKeyConstraint(['track_id'], ['events.tracks.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('abstract_id', 'user_id', 'track_id'),
        schema='event_abstracts'
    )

    op.create_table(
        'abstract_review_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False, index=True),
        sa.Column('review_id', sa.Integer(), nullable=False, index=True),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['event_abstracts.abstract_review_questions.id']),
        sa.ForeignKeyConstraint(['review_id'], ['event_abstracts.abstract_reviews.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id'),
        schema='event_abstracts'
    )
    op.create_table(
        'track_abstract_reviewers',
        sa.Column('user_id', sa.Integer(), nullable=False, autoincrement=False, index=True),
        sa.Column('track_id', sa.Integer(), nullable=False, autoincrement=False, index=True),
        sa.ForeignKeyConstraint(['track_id'], ['events.tracks.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.users.id']),
        sa.PrimaryKeyConstraint('user_id', 'track_id'),
        schema='events'
    )
    op.create_table(
        'email_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('abstract_id', sa.Integer(), nullable=False, index=True),
        sa.Column('email_template_id', sa.Integer(), nullable=True, index=True),
        sa.Column('sent_dt', UTCDateTime, nullable=False),
        sa.Column('recipients', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['abstract_id'], ['event_abstracts.abstracts.id']),
        sa.ForeignKeyConstraint(['email_template_id'], ['event_abstracts.email_templates.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='event_abstracts'
    )


def downgrade():
    op.drop_table('email_logs', schema='event_abstracts')
    op.drop_table('track_abstract_reviewers', schema='events')
    op.drop_table('abstract_review_ratings', schema='event_abstracts')
    op.drop_table('abstract_reviews', schema='event_abstracts')
    op.drop_table('abstract_review_questions', schema='event_abstracts')
    op.drop_table('abstract_comments', schema='event_abstracts')
    op.drop_table('abstract_person_links', schema='event_abstracts')
    op.drop_table('email_templates', schema='event_abstracts')
    op.drop_table('abstracts', schema='event_abstracts')
    op.rename_table('legacy_abstracts', 'abstracts', schema='event_abstracts')
    op.execute('''
        ALTER INDEX event_abstracts.ix_legacy_abstracts_accepted_track_id RENAME TO ix_abstracts_accepted_track_id;
        ALTER INDEX event_abstracts.ix_legacy_abstracts_accepted_type_id RENAME TO ix_abstracts_accepted_type_id;
        ALTER INDEX event_abstracts.ix_legacy_abstracts_event_id RENAME TO ix_abstracts_event_id;
        ALTER INDEX event_abstracts.ix_legacy_abstracts_type_id RENAME TO ix_abstracts_type_id;
        ALTER SEQUENCE event_abstracts.legacy_abstracts_id_seq RENAME TO abstracts_id_seq;
        ALTER TABLE event_abstracts.abstracts RENAME CONSTRAINT pk_legacy_abstracts TO pk_abstracts;
        ALTER TABLE event_abstracts.abstracts RENAME CONSTRAINT
            fk_legacy_abstracts_accepted_type_id_contribution_types TO fk_abstracts_accepted_type_id_contribution_types;
        ALTER TABLE event_abstracts.abstracts RENAME CONSTRAINT
            fk_legacy_abstracts_event_id_events TO fk_abstracts_event_id_events;
        ALTER TABLE event_abstracts.abstracts RENAME CONSTRAINT
            fk_legacy_abstracts_type_id_contribution_types TO fk_abstracts_type_id_contribution_types;
        ALTER TABLE event_abstracts.abstracts RENAME CONSTRAINT
            uq_legacy_abstracts_friendly_id_event_id TO uq_abstracts_friendly_id_event_id;
    ''')

    op.create_foreign_key(None,
                          'judgments', 'abstracts',
                          ['abstract_id'], ['id'],
                          source_schema='event_abstracts', referent_schema='event_abstracts')
    op.create_foreign_key(None,
                          'abstract_field_values', 'abstracts',
                          ['abstract_id'], ['id'],
                          source_schema='event_abstracts', referent_schema='event_abstracts')
    op.create_foreign_key(None,
                          'contributions', 'abstracts',
                          ['abstract_id'], ['id'],
                          source_schema='events', referent_schema='event_abstracts')
