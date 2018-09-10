from marshmallow_sqlalchemy import (
    ModelSchema,
    field_for,
)
from marshmallow import (
    EXCLUDE,
    post_dump,
)

from memedata.database import db
from memedata.models import Text

class TextSchema(ModelSchema):
    content = field_for(Text, 'content', required=True)
    created_at = field_for(Text, 'created_at', dump_only=True)
    updated_at = field_for(Text, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Text
        sqla_session = db.session

    @staticmethod
    def get_envelope_key(many):
        return 'texts' if many else 'text'

    @post_dump(pass_many=True)
    def envelope(self, dct, many):
        return {TextSchema.get_envelope_key(many): dct}
