from flask import request, url_for

def url_for_other_page(page, sort=None):
    args = request.args.copy()
    args['p'] = page
    if sort:
        args['s'] = sort
    return url_for(request.endpoint, **args)
