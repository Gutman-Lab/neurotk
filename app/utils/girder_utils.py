"""Functions that utilize the girder client. This could be wrappers 
around girder API requests or more complex functions. These should be 
become incorporated in the dsa-helpers Python library at a later date 
and become deprecated here.
"""

from girder_client import GirderClient


def get_item_annotation_docs(
    gc: GirderClient, item_id: str, with_elements: bool = False
) -> list[dict]:
    """
    Get all annotation documents for an item.

    Args:
        gc: The girder client to use.
        item_id: The item id to get annotations for.
        with_elements: Whether to include the annotation elements.

    Returns:
        A list of annotation documents.

    """
    if with_elements:
        # Get the documents with elements.
        return gc.get(f"annotation/item/{item_id}")
    else:
        # Get the documents without elements.
        return gc.get("annotation", parameters={"itemId": item_id, "limit": 0})
