import uuid
from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from app.schemas import BookRequest, BookResponse, PaginatedBookResponse
from app.services import BookService

def _book_to_dict(book) -> dict:
    """Convert a book object (dict) to an API-friendly format"""
    return {
        "id": str(book["id"]),
        "title": book["title"],
        "author": book["author"],
        "description": book.get("description", ""),
        "year": book["year"],
        "status": book["status"],
    }

class HealthResource(Resource):
    def get(self):
        """
        Health check endpoint
        ---
        tags:
          - Health
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
        """
        return {"status": "ok"}, 200

class BookListResource(Resource):
    def get(self):
        """
        Get a paginated list of books
        ---
        tags:
          - Books
        parameters:
          - name: status
            in: query
            type: string
            enum: [available, issued]
            required: false
            description: Filter by status
          - name: author
            in: query
            type: string
            required: false
            description: Filter by author
          - name: limit
            in: query
            type: integer
            default: 10
            description: Number of books per page
          - name: offset
            in: query
            type: integer
            default: 0
            description: Number of books to skip
        responses:
          200:
            description: List of books successfully retrieved
            schema:
              $ref: '#/definitions/PaginatedBookResponse'
        """
        status = request.args.get("status")
        author = request.args.get("author")
        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)

        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        result = BookService.get_all_books(
            status=status,
            author=author,
            limit=limit,
            offset=offset
        )

        if isinstance(result, dict) and "items" in result:
            result["items"] = [_book_to_dict(book) for book in result["items"]]
            return result, 200
        
        return [_book_to_dict(book) for book in result], 200

    def post(self):
        """
        Create a new book
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/BookRequest'
        responses:
          201:
            description: Book created successfully
            schema:
              $ref: '#/definitions/BookResponse'
          422:
            description: Validation error
        """
        data = request.get_json(force=True)
        try:
            book_request = BookRequest(**data)
        except ValidationError as e:
            errors = [
                {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
                for err in e.errors()
            ]
            return {"errors": errors}, 422

        new_book = BookService.create_book(book_request.model_dump())
        return _book_to_dict(new_book), 201

class BookResource(Resource):
    def get(self, book_id):
        """
        Get a book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            format: uuid
            required: true
            description: UUID of the book
        responses:
          200:
            description: Book found
            schema:
              $ref: '#/definitions/BookResponse'
          404:
            description: Book not found
        """
        try:
            uuid.UUID(book_id)
        except ValueError:
            return {"message": "Invalid book ID format"}, 400

        book = BookService.get_book_by_id(book_id)
        if not book:
            return {"message": "Book not found"}, 404
            
        return _book_to_dict(book), 200

    def delete(self, book_id):
        """
        Delete a book by ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            format: uuid
            required: true
        responses:
          200:
            description: Book deleted successfully
          404:
            description: Book not found
        """
        try:
            uuid.UUID(book_id)
        except ValueError:
            return {"message": "Invalid book ID format"}, 400

        success = BookService.delete_book(book_id)
        if not success:
            return {"message": "Book not found"}, 404
            
        return {"message": "Book deleted successfully"}, 200