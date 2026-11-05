from common.fsm import FSM, Transition
from orders.models import Order

S = Order.Status
ORDER_FSM = FSM(
    [
        Transition(S.PENDING_PAYMENT, S.PAID, "pay"),
        Transition(S.PENDING_PAYMENT, S.EXPIRED, "expire"),
        Transition(S.EXPIRED, S.PAID, "pay_late"),
        Transition(S.EXPIRED, S.PENDING_PAYMENT, "renew_payment"),
        Transition(S.PAID, S.REFUNDED, "refund"),
        # As transições abaixo serão acionadas pelo app de parceiros.
        Transition(S.PAID, S.IN_PRODUCTION, "start_production"),
        Transition(S.IN_PRODUCTION, S.REFUNDED, "refund"),
        Transition(S.IN_PRODUCTION, S.SHIPPED, "ship"),
        Transition(S.SHIPPED, S.REFUNDED, "refund"),
        Transition(S.SHIPPED, S.DELIVERED, "deliver"),
        Transition(S.DELIVERED, S.REFUNDED, "refund"),
    ]
)
