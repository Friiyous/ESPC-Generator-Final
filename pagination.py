"""
Système de pagination pour les grandes listes
"""

def paginate_list(data, page=1, per_page=20):
    """
    Paginate a list of data
    
    Args:
        data: List of items to paginate
        page: Current page number (1-based)
        per_page: Number of items per page
    
    Returns:
        dict: Paginated data with pagination info
    """
    if not data:
        return {
            "items": [],
            "total": 0,
            "pages": 0,
            "current_page": page,
            "per_page": per_page,
            "has_next": False,
            "has_prev": False
        }
    
    total = len(data)
    pages = (total + per_page - 1) // per_page
    
    # Validate page number
    page = max(1, min(page, pages))
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    items = data[start_idx:end_idx]
    
    return {
        "items": items,
        "total": total,
        "pages": pages,
        "current_page": page,
        "per_page": per_page,
        "has_next": page < pages,
        "has_prev": page > 1
    }

def get_pagination_controls(current_page, total_pages, per_page=20):
    """
    Generate pagination controls for Streamlit
    
    Args:
        current_page: Current page number
        total_pages: Total number of pages
        per_page: Items per page
    
    Returns:
        dict: Pagination controls configuration
    """
    if total_pages <= 1:
        return None
    
    controls = {
        "current_page": current_page,
        "total_pages": total_pages,
        "per_page": per_page,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "start_range": max(1, current_page - 2),
        "end_range": min(total_pages, current_page + 2)
    }
    
    return controls
