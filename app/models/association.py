from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

# Define the association table
file_document = Table(
    'file_document',
    Base.metadata,
    Column('file_id', Integer, ForeignKey('uploaded_files.id'), primary_key=True),
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True)
) 