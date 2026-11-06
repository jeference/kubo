from common.fsm import FSM, Transition
from creations.models import Creation, ProviderTask

S = Creation.Status
CREATION_FSM = FSM(
    [
        Transition(S.GENERATING_IMAGE, S.READY, "image_ready"),
        Transition(S.GENERATING_IMAGE, S.IMAGE_FAILED, "image_failed"),
        Transition(S.IMAGE_FAILED, S.GENERATING_IMAGE, "retry"),
    ]
)

T = ProviderTask.Status
TASK_ACTIVE = (T.QUEUED, T.RUNNING)
