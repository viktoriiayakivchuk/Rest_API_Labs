from flask import Flask, redirect
from flask_restful import Api
from flasgger import Swagger
from werkzeug.exceptions import HTTPException

from app.api import HealthResource, BookListResource, BookResource

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Library Management API (Lab 5)",
        "description": "REST API on Flask-RESTful with detailed Swagger documentation",
        "version": "1.0.0",
    },
    "basePath": "/",
    "definitions": {
        "BookRequest": {
            "type": "object",
            "required": ["title", "author", "year", "status"],
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 100, "example": "The Great Gatsby"},
                "author": {"type": "string", "minLength": 2, "maxLength": 100, "example": "F. Scott Fitzgerald"},
                "description": {"type": "string", "maxLength": 400, "example": "A novel about the American dream"},
                "year": {"type": "integer", "minimum": 1, "example": 1925},
                "status": {"$ref": "#/definitions/BookStatus"}
            },
        },
        "BookResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "year": {"type": "integer"},
                "status": {"$ref": "#/definitions/BookStatus"},
            },
        },
        "BookStatus": {
            "type": "string",
            "enum": ["available", "issued", "borrowed"],
            "example": "available"
        },
        "PaginatedBookResponse": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/BookResponse"}
                },
                "total": {"type": "integer", "example": 1},
                "limit": {"type": "integer", "example": 10},
                "offset": {"type": "integer", "example": 0},
                "next_page": {"type": "string", "x-nullable": True, "example": "/books?limit=10&offset=10"},
                "prev_page": {"type": "string", "x-nullable": True, "example": None}
            }
        },
        "ValidationError": {
            "type": "object",
            "properties": {
                "loc": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["body", "year"]
                },
                "msg": {"type": "string", "example": "Year cannot be greater than the current year"},
                "type": {"type": "string", "example": "value_error"}
            }
        }
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

app = Flask(__name__)
api = Api(app)

swagger = Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

api.add_resource(HealthResource, "/health")
api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<string:book_id>")

@app.route("/")
def root():
    return redirect("/apidocs/")

@app.errorhandler(HTTPException)
def handle_http_exception(exc):
    return {"detail": exc.description}, exc.code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)