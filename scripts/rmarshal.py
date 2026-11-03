"""Lector mínimo y seguro del formato Ruby Marshal 4.8 (solo lee datos, no ejecuta nada)."""
import struct

class RObj:
    def __init__(self, cls): self.cls = cls; self.ivars = {}
    def __repr__(self): return f"<{self.cls} {list(self.ivars)}>"
    def get(self, k, d=None): return self.ivars.get('@' + k, d)

class Sym(str): pass

class Reader:
    def __init__(self, data):
        self.d = data; self.p = 0; self.syms = []; self.objs = []
    def byte(self):
        b = self.d[self.p]; self.p += 1; return b
    def long(self):
        c = struct.unpack('b', bytes([self.byte()]))[0]
        if c == 0: return 0
        if 5 < c < 128: return c - 5
        if -129 < c < -5: return c + 5
        if c > 0:
            x = 0
            for i in range(c): x |= self.byte() << (8 * i)
            return x
        c = -c; x = -1
        for i in range(c):
            x &= ~(0xff << (8 * i)); x |= self.byte() << (8 * i)
        return x
    def raw(self):
        n = self.long(); s = self.d[self.p:self.p + n]; self.p += n; return s
    def sym(self):
        t = chr(self.byte())
        if t == ':':
            s = Sym(self.raw().decode('utf-8', 'replace')); self.syms.append(s); return s
        if t == ';': return self.syms[self.long()]
        if t == 'I':
            s = self.sym(); n = self.long()
            for _ in range(n): self.sym(); self.load()
            return s
        raise ValueError('sym ' + t)
    def reg(self, o): self.objs.append(o); return o
    def load(self):
        t = chr(self.byte())
        if t == '0': return None
        if t == 'T': return True
        if t == 'F': return False
        if t == 'i': return self.long()
        if t in ':;': self.p -= 1; return self.sym()
        if t == '@': return self.objs[self.long()]
        if t == '"':
            return self.reg(self.raw().decode('utf-8', 'replace'))
        if t == 'I':
            idx = len(self.objs); v = self.load(); n = self.long()
            for _ in range(n): self.sym(); self.load()
            return v
        if t == '[':
            a = self.reg([]); n = self.long()
            for _ in range(n): a.append(self.load())
            return a
        if t in '{}':
            h = self.reg({}); n = self.long()
            for _ in range(n):
                k = self.load(); v = self.load()
                try: h[k] = v
                except TypeError: h[repr(k)] = v
            if t == '}': self.load()
            return h
        if t == 'o':
            cls = self.sym(); o = self.reg(RObj(cls)); n = self.long()
            for _ in range(n):
                k = self.sym(); o.ivars[k] = self.load()
            return o
        if t == 'S':
            cls = self.sym(); o = self.reg(RObj(cls)); n = self.long()
            for _ in range(n):
                k = self.sym(); o.ivars['@' + k] = self.load()
            return o
        if t == 'f':
            s = self.raw().decode(); return self.reg(float(s.replace('inf', 'Infinity')) if s not in ('nan',) else float('nan'))
        if t == 'l':
            sign = chr(self.byte()); n = self.long() * 2
            x = int.from_bytes(self.d[self.p:self.p + n], 'little'); self.p += n
            return self.reg(x if sign == '+' else -x)
        if t == 'u':
            cls = self.sym(); return self.reg(('userdump', cls, self.raw()))
        if t == 'U':
            cls = self.sym(); o = self.reg(RObj(cls)); o.ivars['@_data'] = self.load(); return o
        if t in 'cm':
            return self.reg(('class', self.raw().decode()))
        if t == 'e':
            self.sym(); return self.load()
        if t == 'C':
            self.sym(); return self.load()
        if t == '/':
            s = self.raw(); self.byte(); return self.reg(('regexp', s))
        raise ValueError(f'tipo desconocido {t!r} en {self.p}')

def load(path):
    data = open(path, 'rb').read()
    assert data[:2] == b'\x04\x08'
    r = Reader(data); r.p = 2
    return r.load()
