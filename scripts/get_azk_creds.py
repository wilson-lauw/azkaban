from subprocess import getoutput

def get_password(user):
    cmd = 'cat /azkaban/conf/azkaban-users.xml|grep username=\\"{}\\"'.format(user)
    r = getoutput(cmd)
    password = list(filter(lambda l:'password=' in l, r.split()))[0].replace('password=', '').replace('"', '')

    return password