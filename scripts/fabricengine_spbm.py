"""Shared SPBM port descriptions for FabricEngine device types."""

SPBM_LOOPBACK = "Reserved for internal loopback in SPBM mode"

# 4220 high-mode last SFP+ ports are not reserved; bandwidth is capped instead.
SPBM_4220_HIGH = (
    "SPBM high bandwidth mode: UNI-NNI and NNI-UNI bandwidth limited to 1 Gbps"
)
