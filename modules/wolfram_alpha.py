from util.hook import *
from util import web

@hook(cmds=['wa'], ex='wa 1 mile in feet', args=True)
def wa(code, input):
    """Wolfram Alpha search"""
    query = input.group(2)
    uri = 'http://tumbolia.appspot.com/wa/'
    try:
        answer = web.get(uri + web.quote(query), timeout=10).read()
    except:
        return code.say('It seems WolframAlpha took too long to respond!')

    if answer and 'json stringified precioussss' not in answer:
        answer = answer.strip('\n').split(';')
        for i in range(len(answer)):
            answer[i] = answer[i].replace('|', '').strip()
        answer = '{purple}{b}WolframAlpha: {c}{b}' + ' - '.join(answer).replace('\\', '').replace('->', ': ')
        while '  ' in answer:
            answer = answer.replace('  ', ' ')
        return code.say(web.htmlescape(answer))
    else:
        return code.reply('{red}Sorry, no result.')