from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.schemas import BookQueryParams

class BookRepository:
    def __init__(self, collection=None):
        self.collection = collection

    async def get_all(self, params: BookQueryParams) -> tuple[List[Dict[str, Any]], int]:
        filter_query = {}
        if params.status:
            filter_query["status"] = params.status
        if params.author:
            filter_query["author"] = {"$regex": params.author, "$options": "i"}

        total_count = await self.collection.count_documents(filter_query)
        cursor = self.collection.find(filter_query)

        if params.sort_by:
            sort_direction = 1 if params.sort_order == "asc" else -1
            cursor = cursor.sort(params.sort_by, sort_direction)
            
        cursor = cursor.skip(params.offset).limit(params.limit)
        docs = await cursor.to_list(length=params.limit)
        
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
            
        return docs, total_count

    async def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return None
            
        doc = await self.collection.find_one({"_id": obj_id})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def add(self, book_data: dict) -> Dict[str, Any]:
        data_to_insert = book_data.copy()
        
        if "id" in data_to_insert:
            del data_to_insert["id"]
            
        result = await self.collection.insert_one(data_to_insert)
        
        book_data["id"] = str(result.inserted_id)
        
        if "_id" in book_data:
            del book_data["_id"]
            
        return book_data

    async def delete(self, book_id: str) -> bool:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return False
            
        result = await self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0