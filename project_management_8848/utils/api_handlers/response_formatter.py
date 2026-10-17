# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe

# Most specific first: DoesNotExistError subclasses ValidationError.
ERROR_STATUS_CODES = (
	(frappe.PermissionError, 403),
	(frappe.DoesNotExistError, 404),
	(frappe.ValidationError, 400),
)


def api_response(status: bool = True, code: int = 200, message: str = "", data=None, errors=None) -> dict:
	"""
	Build the standard response envelope returned by every whitelisted endpoint in this app.

	Parameters:
		status (bool, optional): Success flag. Default True.
		code (int, optional): HTTP status code; also set on the actual response. Default 200.
		message (str, optional): Human-readable message, safe to show in the UI.
		data (object | list | None, optional): Payload on success.
		errors (object | list | None, optional): Error detail on failure.

	Returns:
		dict: {"status", "status_code", "message", "data", "errors"}
	"""
	frappe.local.response["http_status_code"] = code
	return {
		"status": status,
		"status_code": code,
		"message": message,
		"data": data,
		"errors": errors,
	}


def api_error(exc: frappe.ValidationError) -> dict:
	"""
	Translate a Frappe validation or permission error into the standard failure envelope.
	The queued msgprint is cleared so the client shows one message, not a popup plus the envelope.

	Parameters:
		exc (frappe.ValidationError, required): The caught exception (PermissionError and
			DoesNotExistError are subclasses).

	Returns:
		dict: Failure envelope with a matching HTTP status code.
	"""
	frappe.clear_messages()
	code = next(code for exc_type, code in ERROR_STATUS_CODES if isinstance(exc, exc_type))
	message = frappe.utils.strip_html(str(exc))
	return api_response(status=False, code=code, message=message, errors={"type": type(exc).__name__})
