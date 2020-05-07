from main import *


class RegionResource(Resource):
    def get(self, region_id):
        abort_if_region_not_found(region_id)
        session = db_session.create_session()
        region = session.query(Region).get(region_id)
        return jsonify({'region': region.to_dict(
            only=('id', 'name', 'cases',
                  'cured', 'deaths'))})


class RegionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        regions = session.query(Region).all()
        return jsonify({'regions': [item.to_dict(
            only=('id', 'name')) for item in regions]})


def abort_if_region_not_found(region_id):
    session = db_session.create_session()
    region = session.query(Region).get(region_id)
    if not region:
        abort(404, message=f"Region {region_id} not found")
