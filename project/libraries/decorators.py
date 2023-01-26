import functools


def logger(event_name):
    def decorator(function):
        @functools.wraps(function)
        async def handler(*args, **kwargs):
            end_process = await function(*args, **kwargs)
            await args[0].insert_into_logger(user_id=end_process["id"], event=event_name)
            return end_process

        return handler

    return decorator
