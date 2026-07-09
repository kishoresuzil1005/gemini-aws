DIAGNOSIS_TEMPLATE = """
## User Question

{question}

## Intent

{intent}

## Resources

{resources}

## Cloud Relationships

{relationships}

## Metadata

{metadata}

## AWS Documentation

{documents}

Answer the question.
"""

MIGRATION_TEMPLATE = """
Migration Request

Question:

{question}

Resources:

{resources}

Provide:

- Architecture
- Risks
- Terraform Mapping
- Estimated Cost
"""
