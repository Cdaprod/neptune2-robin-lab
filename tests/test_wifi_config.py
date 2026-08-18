import unittest
from neptune_robin.wifi_config import patch_config


class WifiConfigTests(unittest.TestCase):
    def test_patch_existing(self):
        source = (
            ">CFG_WIFI_MODE 1 # mode\n"
            ">CFG_WIFI_AP_NAME old\n"
            ">CFG_WIFI_KEY_CODE oldpass\n"
            ">CFG_CLOUD_ENABLE 1\n"
            ">WISI_LIST_SCAN 0\n"
            ">DISABLE_WIFI 1\n"
        )
        values = {
            "CFG_WIFI_MODE": "0",
            "CFG_WIFI_AP_NAME": "cda_Lab",
            "CFG_WIFI_KEY_CODE": "secret",
            "CFG_CLOUD_ENABLE": "0",
            "WISI_LIST_SCAN": "1",
            "DISABLE_WIFI": "0",
        }
        out = patch_config(source, values)
        self.assertIn(">CFG_WIFI_MODE 0 # mode", out)
        self.assertIn(">CFG_WIFI_AP_NAME cda_Lab", out)
        self.assertIn(">CFG_WIFI_KEY_CODE secret", out)
        self.assertIn(">CFG_CLOUD_ENABLE 0", out)
        self.assertIn(">WISI_LIST_SCAN 1", out)
        self.assertIn(">DISABLE_WIFI 0", out)

    def test_append_missing(self):
        out = patch_config("# machine config\n", {"DISABLE_WIFI": "0"})
        self.assertIn(">DISABLE_WIFI 0", out)


if __name__ == "__main__":
    unittest.main()
