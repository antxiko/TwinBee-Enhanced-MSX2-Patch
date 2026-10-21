"""Aplica el parche a tu volcado y comprueba las dos sumas: la del volcado (el
Twin Bee que espera el parche) y la de la MegaROM resultante. Sin el volcado
falla: es la prueba de verdad del parche.

Uso: python tools/verifica.py [twinbee.rom]
"""
import hashlib
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools"))
import ips  # noqa: E402

SHA_ORIGINAL = "02bdce8ceafe6af05a45b61a689e78807551df663afd152090f7cd9cac827dd4"
SHA_MEJORADA = "c16979326e8df9277f8ab34850683559fd7eb4e412645b1459cbde865bae4f67"


def main(rom):
    if not os.path.exists(rom):
        sys.exit(f"falta el volcado {rom}")
    orig = open(rom, "rb").read()
    h = hashlib.sha256(orig).hexdigest()
    if h != SHA_ORIGINAL:
        sys.exit(f"{rom}: sha256 {h}, no es el Twin Bee que espera el parche")
    res = ips.aplica_bytes(orig, open(os.path.join(RAIZ, "ips", "twinbee_enhanced_msx2.ips"), "rb").read())
    h = hashlib.sha256(res).hexdigest()
    if len(res) != 256 * 1024 or h != SHA_MEJORADA:
        sys.exit(f"el resultado no es la MegaROM esperada ({len(res)} bytes, sha256 {h})")
    print(f"ok: {rom} -> MegaROM de {len(res)} bytes, sha256 {h}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "twinbee.rom"))
