from bson import ObjectId
from typing import Any, Dict, Union, List

def serialize_doc(doc: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
    """
    Serializa um documento MongoDB ou lista, convertendo ObjectId para string.
    Suporta documentos aninhados e listas.
    """
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if not isinstance(doc, dict):
        return str(doc) if isinstance(doc, ObjectId) else doc
    
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) for item in value]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value
    return result
