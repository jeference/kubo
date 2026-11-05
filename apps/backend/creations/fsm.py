from common.fsm import FSM, Transition
from creations.models import Creation, ProviderTask

S = Creation.Status
CREATION_FSM = FSM(
    [
        Transition(S.GENERATING_IMAGE, S.AWAITING_APPROVAL, "image_ready"),
        Transition(S.GENERATING_IMAGE, S.IMAGE_FAILED, "image_failed"),
        Transition(S.IMAGE_FAILED, S.GENERATING_IMAGE, "retry"),
        Transition(S.AWAITING_APPROVAL, S.GENERATING_MODEL, "approve"),
        Transition(S.AWAITING_APPROVAL, S.READY, "reuse_model"),
        Transition(S.GENERATING_MODEL, S.READY, "model_ready"),
        Transition(S.GENERATING_MODEL, S.MODEL_FAILED, "model_failed"),
        Transition(S.MODEL_FAILED, S.GENERATING_MODEL, "retry"),
        Transition(S.MODEL_FAILED, S.AWAITING_APPROVAL, "back"),
        Transition(S.READY, S.AWAITING_APPROVAL, "back"),
    ]
)

T = ProviderTask.Status
TASK_ACTIVE = (T.QUEUED, T.RUNNING, T.WAITING_PROVIDER)
