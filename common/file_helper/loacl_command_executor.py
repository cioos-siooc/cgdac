from subprocess import Popen, PIPE


def execute_local_command(parallel, un_commit_list, result_cache, timeout=None):
    if parallel:
        for command in un_commit_list:
            with Popen(command, shell=True, stdout=PIPE, stderr=PIPE) as popen_res:
                popen_res.wait(timeout=timeout)
                out = popen_res.stdout.readlines()
                result_cache.append((out, popen_res.returncode))

    else:
        the_comment = ";".join(un_commit_list)
        with Popen(the_comment, shell=True, stdout=PIPE, stderr=PIPE) as popen_res:
            popen_res.wait(timeout=timeout)
            out = popen_res.stdout.readlines()
            result_cache.append((out, popen_res.returncode))
