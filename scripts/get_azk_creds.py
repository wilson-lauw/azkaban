from subprocess import check_output

def get_password(user):
    cmd = 'cat /common/conf/azkaban-users.xml|grep username=\\"{}\\"'.format(user)
    r = check_output(cmd, shell=True)
    password = list(filter(lambda l:'password=' in l, r.split()))[0].replace('password=', '').replace('"', '')

    return password