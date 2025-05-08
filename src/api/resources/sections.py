from flask import request, Blueprint
from flask_restful import Resource, Api
from ...db.models.model import Section
from ...db.core import db

# # Blueprint for section routes
# sections_bp = Blueprint('sections', __name__)
# api = Api(sections_bp)


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

    def get(self):
        sections = Section.query.all()
        total_sections = Section.query.count()
        section_list = [{'id': section.id, 'name': section.title} for section in sections]
        return {'total': total_sections, 'Sections': section_list}, 200

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


# # Register resources with the API inside the blueprint
# api.add_resource(SectionListResource, '/sections')
# api.add_resource(SectionResource, '/sections/<int:section_id>')