"""Parche IPS de Twin Plas Plas: de la ROM original de Twin Bee (Konami, 1986,
32 KB) a la MegaROM del port (256 KB, Konami SCC).

  python port/haz_ips.py crea  ORIGINAL.rom PORT.rom SALIDA.ips
  python port/haz_ips.py aplica ORIGINAL.rom PARCHE.ips SALIDA.rom

`crea` comprueba al final que aplicar el parche da PORT.rom byte a byte.
Formato IPS: "PATCH", registros (desplazamiento de 3 bytes, tamano de 2; tamano
0 = RLE: cuantos de 2 bytes y el byte), "EOF". Todo lo que va mas alla del
original se escribe entero (algunos parcheadores no rellenan los huecos), las
rachas de 9 o mas bytes iguales van como RLE y ningun registro empieza en
0x454F46 ("EOF").
"""
import hashlib
import sys
from pathlib import Path

EOF_ = 0x454F46
MAX = 0xFFFF


def tramos(orig, nuevo):
    """(desplazamiento, bytes) de lo que hay que escribir."""
    n = len(nuevo)
    out, i = [], 0
    while i < n:
        if i < len(orig) and orig[i] == nuevo[i]:
            i += 1
            continue
        j = i
        # se junta mientras haya diferencias o huecos de menos de 6 bytes iguales
        while j < n:
            if j >= len(orig) or orig[j] != nuevo[j]:
                j += 1
                continue
            k = j
            while k < min(n, len(orig)) and orig[k] == nuevo[k] and k - j < 6:
                k += 1
            if k - j >= 6 or k >= n:
                break
            j = k
        out.append((i, nuevo[i:j]))
        i = j
    return out


def registros(desde, datos):
    """Parte un tramo en registros normales y RLE."""
    k = 0
    while k < len(datos):
        r = k
        while r < len(datos) and datos[r] == datos[k] and r - k < MAX:
            r += 1
        if r - k >= 9:
            yield desde + k, None, (r - k, datos[k])
            k = r
            continue
        e = k
        while e < len(datos) and e - k < MAX:
            r = e
            while r < len(datos) and datos[r] == datos[e] and r - e < 9:
                r += 1
            if r - e >= 9:
                break
            e += 1
        yield desde + k, datos[k:e], None
        k = e


def crea(orig_p, port_p, salida):
    orig = Path(orig_p).read_bytes()
    nuevo = Path(port_p).read_bytes()
    assert len(nuevo) >= len(orig)
    ips = bytearray(b"PATCH")
    n_reg = 0
    for desde, datos in tramos(orig, nuevo):
        for off, normal, rle in registros(desde, datos):
            if off == EOF_:                  # nunca un registro en "EOF"
                raise SystemExit("un registro caeria en 0x454F46")
            ips += off.to_bytes(3, "big")
            if rle:
                ips += b"\0\0" + rle[0].to_bytes(2, "big") + bytes([rle[1]])
            else:
                ips += len(normal).to_bytes(2, "big") + normal
            n_reg += 1
    ips += b"EOF"
    Path(salida).write_bytes(bytes(ips))
    res = aplica_bytes(orig, bytes(ips))
    assert res == nuevo, "aplicar el parche NO da la ROM del port"
    print(f"{salida}: {len(ips)} bytes, {n_reg} registros; aplicado a la original da {port_p} "
          f"(sha1 {hashlib.sha1(res).hexdigest()})")


def aplica_bytes(orig, ips):
    assert ips[:5] == b"PATCH", "no es un IPS"
    r, p = bytearray(orig), 5
    while ips[p:p + 3] != b"EOF":
        off = int.from_bytes(ips[p:p + 3], "big")
        tam = int.from_bytes(ips[p + 3:p + 5], "big")
        p += 5
        if tam == 0:
            cuantos = int.from_bytes(ips[p:p + 2], "big")
            datos = ips[p + 2:p + 3] * cuantos
            p += 3
        else:
            datos = ips[p:p + tam]
            p += tam
        if len(r) < off + len(datos):
            r += bytes(off + len(datos) - len(r))
        r[off:off + len(datos)] = datos
    return bytes(r)


def aplica(orig_p, ips_p, salida):
    res = aplica_bytes(Path(orig_p).read_bytes(), Path(ips_p).read_bytes())
    Path(salida).write_bytes(res)
    print(f"{salida}: {len(res)} bytes, sha1 {hashlib.sha1(res).hexdigest()}")


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] not in ("crea", "aplica"):
        sys.exit(__doc__)
    (crea if sys.argv[1] == "crea" else aplica)(*sys.argv[2:])
