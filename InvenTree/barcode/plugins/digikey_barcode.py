# -*- coding: utf-8 -*-

"""
DigiKey barcode decoding
"""

from barcode.barcode import BarcodePlugin


class DigikeyBarcodePlugin(BarcodePlugin):

    PLUGIN_NAME = "DigikeyBarcode"

    def validate(self):
        """
        TODO: Validation of Digikey barcodes.
        """

        return False