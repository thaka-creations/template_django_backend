import graphene
from django.core.paginator import Paginator


class PageInfoWithResolvers(graphene.ObjectType):
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()
    current_page = graphene.Int()
    total_pages = graphene.Int()
    total_count = graphene.Int()
    per_page = graphene.Int()

    def __init__(self, data):
        self._data = data

    def resolve_has_next_page(self, info):
        return self._data.get("has_next_page")

    def resolve_has_previous_page(self, info):
        return self._data.get("has_previous_page")

    def resolve_current_page(self, info):
        return self._data.get("current_page")

    def resolve_total_pages(self, info):
        return self._data.get("total_pages")

    def resolve_total_count(self, info):
        return self._data.get("total_count")

    def resolve_per_page(self, info):
        return self._data.get("per_page")


class PaginationMixin:
    """Mixin class to handle pagination logic"""

    @staticmethod
    def get_page_info(queryset, page, per_page):
        """
        Generate pagination info from queryset

        Args:
            queryset: Django QuerySet to paginate
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            tuple: (page_object, page_info_object)
        """
        # Validate and sanitize inputs
        try:
            page = max(1, int(page)) if page is not None else 1
            per_page = max(1, min(int(per_page), 100)) if per_page is not None else 10
        except (ValueError, TypeError):
            page = 1
            per_page = 10

        # Create paginator
        paginator = Paginator(queryset, per_page)

        # Handle page out of range - get the last page instead of raising error
        if page > paginator.num_pages and paginator.num_pages > 0:
            page = paginator.num_pages

        # Get page object
        page_obj = paginator.get_page(page)

        # Build page data
        page_data = {
            "has_next_page": page_obj.has_next(),
            "has_previous_page": page_obj.has_previous(),
            "current_page": page,  # Use the actual page we're returning
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "per_page": per_page,
        }

        return page_obj, PageInfoWithResolvers(page_data)
