import re
from util import web
from util.hook import *


@hook(cmds=['kernel', 'kern'])
def kernel(code, input):
    """ kernel - Gets the latest kernel versions from kernel.org """
    data = web.text('https://www.kernel.org/finger_banner')
    data = re.findall(r'The latest (.*?) version of the Linux kernel is: (.*)', data)
    kernel_versions = ["{b}%s{b} - %s" % (item[0], item[1].strip()) for item in data]
    code.say("Latest kernels: %s" % ", ".join(kernel_versions))
