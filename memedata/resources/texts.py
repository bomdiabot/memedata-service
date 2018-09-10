import datetime as dt

from flask import (
    request,
    abort,
)
from flask_restful import (
    Resource,
)
from marshmallow import (
    ValidationError,
)

from webargs.fields import (
    DelimitedList,
    Date,
    Integer,
    Str,
)
from webargs import validate
from webargs.flaskparser import parser
from sqlalchemy import func

from memedata.models import Text, Tag
from memedata.serializers import TextSchema, TagSchema
from memedata.database import db
from memedata.util import mk_errors, fmt_validation_error_messages, flatten

class TextRes(Resource):
    @staticmethod
    def get_text(uid):
        text = Text.query.get(uid)
        if text is None:
            abort(mk_errors(404, '{} doest not exist'.format(uid)))
        return text

    def get(self, uid):
        text = TextRes.get_text(uid)
        return TextSchema().dump(text)

    def put(self, uid):
        text = TextRes.get_text(uid)
        try:
            schema = TextSchema()
            text = schema.load(request.values, instance=text, partial=True)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return schema.dump(text)

    def delete(self, uid):
        text = TextRes.get_text(uid)
        db.session.delete(text)
        db.session.commit()
        return '', 204

def get_tags(contents):
    tags = Tag.query.filter(Tag.content.in_(contents)).all()
    found_contents = {t.content for t in tags}
    not_found_contents = set(contents) - found_contents
    new_tags = [Tag(c) for c in not_found_contents]
    #adding new tags to database
    db.session.add_all(new_tags)
    db.session.commit()
    tags.extend(new_tags)
    return tags

def serialize_tags(tags):
    return TagSchema(many=True).dump(tags)

@parser.error_handler
def handle_request_parsing_error(error, *args):
    try:
        if not isinstance(error, list):
            error = [error]
        messages = fmt_validation_error_messages(error)
    except:
        raise ValidationError
    abort(mk_errors(400, messages))

class TextsRes(Resource):
    POST_MAX_N_TAGS = 16

    POST_ARGS = {
        'tags': DelimitedList(Str()),
        'content': Str(),
    }

    TAGS_BLACKLIST = {
        'generated',
        'background',
        'meme',
        'captioned',
    }

    GET_MAX_N_RESULTS = 100

    GET_ARGS = {
        'any_tags': DelimitedList(Str()),
        'all_tags': DelimitedList(Str()),
        'date_from': Date(),
        'date_to': Date(),
        'max_n_results': \
            Integer(validate=lambda n: n >= 0, missing=GET_MAX_N_RESULTS),
    }

    @staticmethod
    def parse_post_args(req):
        args = parser.parse(TextsRes.POST_ARGS, req)
        if 'tags' in args:
            if len(args['tags']) > TextsRes.POST_MAX_N_TAGS:
                raise ValidationError(
                    'too many tags (limit={})'.format(TextsRes.POST_MAX_N_TAGS))
            for tag in args['tags']:
                if tag in TextsRes.TAGS_BLACKLIST:
                    raise ValidationError(
                        '"{}" is blacklisted'.format(tag))
            args['tags'] = serialize_tags(get_tags(args['tags']))
        return args

    @staticmethod
    def parse_get_args(req):
        args = parser.parse(TextsRes.GET_ARGS, req)
        TextsRes.filter_texts(args)
        return args

    @staticmethod
    def filter_texts(args):
        query = Text.query
        if 'date_to' in args:
            query = query.filter(
                func.DATE(Text.created_at) <= args['date_to'])
        if 'date_from' in args:
            query = query.filter(
                func.DATE(Text.created_at) >= args['date_from'])
        if 'all_tags' in args:
            tags = Tag.query.filter(Tag.content.in_(args['all_tags'])).all()
            #dirty hack TODO: get a better solution
            for t in tags:
                query = query.filter(Text.tags.contains(t))
        elif 'any_tags' in args:
            query = query.join(Tag, Text.tags).join(
                Tag.query.join(Text, Tag.texts).filter(
                    Tag.content.in_(args['any_tags'])))
        texts = query.limit(args['max_n_results']).all()
        return texts

    def post(self):
        try:
            args = TextsRes.parse_post_args(request)
            text = TextSchema().load(args)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return TextSchema().dump(text), 201

    def get(self):
        try:
            args = TextsRes.parse_get_args(request)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        texts = TextsRes.filter_texts(args)
        return TextSchema(many=True).dump(texts)
