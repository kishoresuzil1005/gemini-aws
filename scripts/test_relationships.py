from app.database import SessionLocal
from app.services.graph.aws_relationship_builder import AWSRelationshipBuilder

db = SessionLocal()
builder = AWSRelationshipBuilder(db)
rels = builder.build()
for r in rels:
    print(r)
