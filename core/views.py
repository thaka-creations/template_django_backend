import re

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.error_formater import format_error


class BaseView(APIView):
    """
    A base API view that provides standard POST and PUT methods,
    error handling, and permission enforcement.
    """

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response({"error": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)

    def handle_error(self, error) -> Response:
        """
        Handles errors and returns a standardized error response.
        """
        return Response(
            {"error": format_error(error)}, status=status.HTTP_400_BAD_REQUEST
        )

    def handle_success(self, data) -> Response:
        """
        Handles successful operations and returns a standardized success response.
        """
        return Response({"message": data}, status=status.HTTP_200_OK)

    def handle_not_found(self, message: str) -> Response:
        """
        Handles not found errors and returns a standardized not found response.
        """
        return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)

    def handle_integrity_error(self, error: str) -> Response:
        """
        Handles integrity errors and returns a standardized integrity error response.
        """
        error_message = str(error)
        # Map field names to user-friendly error messages
        # Dynamically generate unique field error messages based on model unique fields
        unique_fields = {}
        for field in getattr(self.model_class._meta, "fields", []):
            if getattr(field, "unique", False):
                field_name = field.name
                # Use a generic message, but include the verbose name dynamically
                unique_fields[
                    field_name
                ] = f"A {self.verbose_name} with this {field.verbose_name} already exists."
        # Add common fields that may not be in model fields (for flexibility)
        for field in ["phone", "email", "code", "name"]:
            if field not in unique_fields:
                unique_fields[
                    field
                ] = f"A {self.verbose_name} with this {field} already exists."
        for field, message in unique_fields.items():
            if (
                f"{self.model_class._meta.db_table}.{field}" in error_message
                or re.search(rf"unique.*{field}", error_message, re.IGNORECASE)
            ):
                return self.handle_error(message)
        return self.handle_error(error_message)

    def post(self, request, *args, **kwargs):
        """
        Handles HTTP POST requests to create a new instance.
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return self.handle_error(serializer.errors)
        try:
            serializer.save()
            return self.handle_success(f"{self.verbose_name} created successfully")
        except Exception as exc:
            return self.handle_integrity_error(exc)

    def put(self, request, *args, **kwargs):
        """
        Handles HTTP PUT requests to update an existing instance.
        """
        try:
            instance = self.model_class.objects.get(id=request.data.get("id"))
        except self.model_class.DoesNotExist:
            return self.handle_not_found(f"{self.verbose_name} not found")
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return self.handle_error(serializer.errors)
        try:
            serializer.save()
            return self.handle_success(f"{self.verbose_name} updated successfully")
        except Exception as exc:
            return self.handle_integrity_error(exc)
