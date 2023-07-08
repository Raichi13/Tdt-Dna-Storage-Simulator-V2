from encoder_base import EncoderBase
from encoder_base import EncoderBase

class DefaultEncoder(EncoderBase):
    def __init__(self, file_path: str, bytes_per_oligo: int, address_size: int, encode_type: int) -> None:
        super().__init__(file_path, bytes_per_oligo, address_size, encode_type)

    def encode(self):
        identified_data = super().get_identified_data(self.ecc_interval)
        return identified_data
