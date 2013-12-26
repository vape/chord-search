from flask import request, url_for

def url_for_other_page(page):
    args = request.args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)
