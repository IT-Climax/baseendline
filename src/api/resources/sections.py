from flask import request, jsonify
from flask_restful import Resource
from ...db.async_core import get_async_session
from ...db.models.model import Section
from ...db.msSchemas.schemas import section_schema, sections_schema
from ...db.core import db
from sqlalchemy.future import select


class SectionResource(Resource):
    """Handle individual section operations"""

    def get(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404
        return {'id': section.id, 'name': section.title}, 200

    def put(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404

        data = request.get_json()
        if not data or 'name' not in data:
            return {'message': 'Missing name in request'}, 400
        # Check uniqueness constraint (optional but good to add)
        if Section.query.filter(Section.name == data['name'], Section.id != section_id).first():
            return {'message': 'Another section with this name already exists'}, 400

        section.name = data['name']
        db.session.commit()
        return section.serialize(), 200

    def delete(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404

        db.session.delete(section)
        db.session.commit()
        return {'message': 'Section deleted successfully'}, 200


class SectionListResource(Resource):
    """Handle collection of sections"""

    # def get(self):
    #     sections = Section.query.all()
    #     total_sections = Section.query.count()
    #     section_list = [{'id': section.id, 'name': section.title} for section in sections]
    #     return {'total': total_sections, 'Sections': section_list}, 200
    async def get(self):
        async with get_async_session() as session:
            result = await session.execute(select(Section))
            sections = await result.scalars().all()
            data = sections_schema.dump(sections)  # Serialize to JSON-compatible dict
            return {'sections': data}, 200

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {'message': 'Missing name in request'}, 400

        if Section.query.filter_by(name=data['name']).first():
            return {'message': 'Section name already exists'}, 400

        new_section = Section(name=data['name'])
        db.session.add(new_section)
        db.session.commit()
        return new_section.serialize(), 201
