from common.fsm import FSM, Transition
from payments.models import Charge

S = Charge.Status
CHARGE_FSM = FSM(
    [
        Transition(S.PENDING, S.PAID, "pay"),
        Transition(S.PENDING, S.EXPIRED, "expire"),
        Transition(S.PENDING, S.FAILED, "fail"),
        Transition(S.EXPIRED, S.PAID, "pay"),
        Transition(S.PAID, S.REFUNDED, "refund"),
    ]
)
