"""Comprobaciones del parche sin la ROM: el IPS esta bien formado, no escribe
en 0x454F46 ("EOF") y cubre justo los 256 KB de la MegaROM. Lo que necesita tu
volcado (aplicarlo y comprobar el sha256 del resultado) es `make verifica`
(tools/verifica.py)."""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools"))
import ips  # noqa: E402

IPS = os.path.join(RAIZ, "ips", "twinbee_enhanced_msx2.ips")


class Parche(unittest.TestCase):
    def setUp(self):
        self.p = open(IPS, "rb").read()

    def test_formato(self):
        self.assertEqual(self.p[:5], b"PATCH")
        self.assertEqual(self.p[-3:], b"EOF")
        i, fin = 5, 0
        while self.p[i:i + 3] != b"EOF":
            off = int.from_bytes(self.p[i:i + 3], "big")
            self.assertNotEqual(off, 0x454F46)
            tam = int.from_bytes(self.p[i + 3:i + 5], "big")
            if tam == 0:
                n = int.from_bytes(self.p[i + 5:i + 7], "big")
                i += 8
            else:
                n = tam
                i += 5 + tam
            fin = max(fin, off + n)
        self.assertEqual(i, len(self.p) - 3)
        self.assertEqual(fin, 256 * 1024)


if __name__ == "__main__":
    unittest.main()
