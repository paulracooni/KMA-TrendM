import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
sys.path.append("/app")

from tasks import task_trendm


task_trendm.delay().get(
    propagate             = False,
    disable_sync_subtasks = False, )


# python ./tests/task_trendm_test.py