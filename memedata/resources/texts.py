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
from flask_jwt_extended import (
    jwt_required,
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
from memedata.util import (
    mk_errors,
    fmt_validation_error_messages,
    flatten,
    filter_fields,
)
from memedata import config

if config.ignore_jwt_texts:
    #dummy decorator
    jwt_required = lambda x: x

class TextRes(Resource):
    GET_ARGS = {
        'fields': DelimitedList(Str()),
    }

    @staticmethod
    def get_text(text_id):
        text = Text.query.get(text_id)
        if text is None:
            abort(mk_errors(404, '{} doest not exist'.format(text_id)))
        return text

    @staticmethod
    def parse_get_args(req):
        args = parser.parse(
            TextRes.GET_ARGS, req, locations=('querystring', ))
        return args

    @jwt_required
    def get(self, text_id):
        """
        Return text resource.

        .. :quickref: Get Text; Get text.

        **Example request**:

        .. sourcecode:: http

	    GET /texts/1 HTTP/1.1
	    Host: example.com
	    Accept: application/json

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "text": {
                    "content": "Bom dia!",
                    "text_id": 1,
                    "tags": [
                        "bomdia"
                    ],
                    "updated_at": null,
                    "created_at": "2018-09-15T22:53:26+00:00"
                }
            }

        :param int text_id: id of text resource.
        :resheader Content-Type: application/json
        :status 200: text found
        :returns: :class:`memedata.models.Text`
        """
        text = TextRes.get_text(text_id)
        try:
            args = TextRes.parse_get_args(request)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        obj = TextSchema().dump(text)
        return filter_fields(obj, args.get('fields'))

    @jwt_required
    def put(self, text_id):
        """
        Update text resource.

        .. :quickref: Put Text; Update text.

        **Example request**:

        .. sourcecode:: http

	    PUT /texts/1 HTTP/1.1
	    Host: example.com
	    Accept: application/json

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "text": {
                    "content": "Updated text",
                    "text_id": 1,
                    "tags": [
                        "bomdia"
                    ],
                    "updated_at": "2018-09-16T23:00:13+00:00"
                    "created_at": "2018-09-15T22:53:26+00:00"
                }
            }

        :param int text_id: id of text resource.
        :form content: the text contents
        :form tags: comma-separated list of tags
        :resheader Content-Type: application/json
        :status 200: text updated
        :returns: :class:`memedata.models.Text`
        """
        text = TextRes.get_text(text_id)
        try:
            schema = TextSchema()
            text = schema.load(request.values, instance=text, partial=True)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return schema.dump(text)

    @jwt_required
    def delete(self, text_id):
        """
        Delete text resource.

        .. :quickref: Delete Text; Remove text.

        **Example request**:

        .. sourcecode:: http

	    DELETE /texts/1 HTTP/1.1
	    Host: example.com

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 204 NO CONTENT

        :param int text_id: id of text resource.
        :status 204: text deleted
        """
        text = TextRes.get_text(text_id)
        db.session.delete(text)
        db.session.commit()
        return '', 204

def get_tags(contents):
    #TODO: get a more performant solution for this
    schema = TagSchema()
    for content in contents:
        tag1 = schema.load({'content': content})
        tag2 = Tag.query.filter_by(content=tag1.content).first()
        if tag2 is None:
            db.session.add(tag1)
    db.session.commit()
    tags = Tag.query.filter(Tag.content.in_(contents)).all()
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
    }

    GET_MAX_N_RESULTS = 1000

    GET_ARGS = {
        'any_tags': DelimitedList(Str()),
        'all_tags': DelimitedList(Str()),
        'no_tags': DelimitedList(Str()),
        'date_from': Date(),
        'date_to': Date(),
        'max_n_results': \
            Integer(validate=lambda n: n >= 0, missing=GET_MAX_N_RESULTS),
        'offset': \
            Integer(validate=lambda n: n >= 0, missing=0),
        'fields': DelimitedList(Str()),
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
    def filter_texts(args):
        #sorting in decreasing order by creation time
        query = Text.query.order_by(-Text.created_at)
        if 'date_to' in args:
            query = query.filter(
                func.DATE(Text.created_at) <= args['date_to'])
        if 'date_from' in args:
            query = query.filter(
                func.DATE(Text.created_at) >= args['date_from'])
        if 'all_tags' in args:
            tags = Tag.query.filter(Tag.content.in_(args['all_tags'])).all()
            if len(tags) < len(args['all_tags']):
                return [], None
            #dirty hack TODO: get a better solution
            for t in tags:
                query = query.filter(Text.tags.contains(t))
        elif 'any_tags' in args:
            query = query.join(Tag, Text.tags).join(
                Tag.query.join(Text, Tag.texts).filter(
                    Tag.content.in_(args['any_tags'])))
        if 'no_tags' in args:
            tags = Tag.query.filter(Tag.content.in_(args['no_tags'])).all()
            #new dirty hack TODO: get a better solution
            for t in tags:
                query = query.filter(~Text.tags.contains(t))

        query = query.offset(args['offset'])
        if query.count() <= args['max_n_results']:
            offset = None
        else:
            offset = args['offset'] + args['max_n_results']
        texts = query.limit(args['max_n_results']).all()

        return texts, offset

    @staticmethod
    def parse_get_args(req):
        args = parser.parse(
            TextsRes.GET_ARGS, req, locations=('querystring', ))
        return args

    @jwt_required
    def post(self):
        """
        Create new text resource.

        .. :quickref: Text creation; Create new text.

        **Example request**:

        .. sourcecode:: http

	    POST /texts HTTP/1.1
	    Host: example.com
	    Accept: application/json

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 201 CREATED
	    Content-Type: application/json

            {
                "text": {
                    "content": "Bom dia!",
                    "text_id": 1,
                    "tags": [
                        "bomdia"
                    ],
                    "updated_at": null,
                    "created_at": "2018-09-15T22:53:26+00:00"
                },
            }


        :form content: the text contents (required)
        :form tags: comma-separated list of tags
        :resheader Content-Type: application/json
        :status 201: resource created
        :returns: :class:`memedata.models.Text`
        """
        try:
            args = TextsRes.parse_post_args(request)
            text = TextSchema().load(args)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return TextSchema().dump(text), 201

    @jwt_required
    def get(self):
        """
        Return collection of texts.

        .. :quickref: Texts collection; Get collection of texts.

        **Example request**:

        .. sourcecode:: http

	    GET /texts HTTP/1.1
	    Host: example.com
	    Accept: application/json

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "texts": [
                    {
                        "content": "Bom dia!",
                        "text_id": 1,
                        "tags": [
                            "bomdia"
                        ],
                        "updated_at": null,
                        "created_at": "2018-09-15T22:53:26+00:00"
                    },
                    {
                        "content": "Eu adoro as manhãs",
                        "text_id": 32,
                        "tags": [
                            "jesus",
                            "sexta"
                        ],
                        "updated_at": null,
                        "created_at": "2018-09-15T22:53:26+00:00"
                    },
                ],
                "offset": 2
            }


        :query string fields: comma-separated list of fields to get for each text.
        :query string date_from: only texts created after specified date (inclusive).
        :query string date_to: only texts created before specified date.
        :query string any_tags: texts with at least one tags in specified list.
        :query string all_tags: texts only containing all specified tags.
        :query string no_tags: texts only not containing any of specified tags.
        :query int offset: pagination offset to start getting results
        :query int max_n_results: maximum number of results to return.
        :resheader Content-Type: application/json
        :status 200: texts found
        :returns: :class:`memedata.models.Text`
        """
        try:
            args = TextsRes.parse_get_args(request)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        texts, offset = TextsRes.filter_texts(args)
        objs = TextSchema(many=True).dump(texts)
        objs = filter_fields(objs, args.get('fields'))
        objs['offset'] = offset
        return objs
