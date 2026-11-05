from common.serializers import GlobalIdSerializer
from payments.models import Charge


class ChargeSerializer(GlobalIdSerializer):
    class Meta:
        model = Charge
        fields = [
            "id",
            "status",
            "amount_cents",
            "pix_br_code",
            "pix_qr_base64",
            "expires_at",
            "paid_at",
        ]
        read_only_fields = fields
