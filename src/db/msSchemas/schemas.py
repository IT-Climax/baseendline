from ..core import ma
from ..models import Section


class SectionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Section
        load_instance = True  # deserialize to model instances
        include_relationships = True  # if you want to include related fields
        # optionally exclude fields or specify only certain fields

    # If you want to include nested questions, define nested schema (optional)
    # questions = ma.Nested('QuestionBaseSchema', many=True)


section_schema = SectionSchema()
sections_schema = SectionSchema(many=True)
