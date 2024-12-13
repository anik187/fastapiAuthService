# class ApiResponse:
#     def __init__(self, status_code, data, message) -> None:
#         self.status_code = status_code
#         self.data = data
#         self.message = message
#         self.success = status_code < 400


def ApiResponse(status_code, data, message):
    return dict(status_code=status_code, data=data, message=message)
