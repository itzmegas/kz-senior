"""Strict, non-executing AMXX v3 / AMX v8 inspector (32-bit, non-compact).

Specification: alliedmodders/amxmodx@8fc12670ea86470a0bfed4c35db5de73d3a39e8a.
amx.cpp:131-279 (enum), 508-775 (formats), 2095-2098 (JREL),
2508-2521 (SWITCH); amx.h:263-281; amxdbg.h:63-123; amxxfile.cpp.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import zlib


REVISION = '8fc12670ea86470a0bfed4c35db5de73d3a39e8a'
AMXX_SHA = '8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e'
AMX_SHA = 'd5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433'
REGIONS = [('cmdDetailed', 95108, 95376), ('fwCmdStart', 99728, 100076),
           ('calcStrafes', 182596, 192488)]
INTEREST = set('g_flFrameGain g_iFrameWSAD g_iFrameDirection g_iFrameStrafe '
               'g_iFrameCount g_iStrafeFrames g_flStrafeGain g_flStrafeLoss '
               'g_flStrafeEfficiency g_iStrafeOverlaps g_iStrafeDesync '
               'g_flStrafeAngle'.split())


class Invalid(ValueError):
    """An explicit structural or bytecode inconsistency; never resynchronize."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unpack_container(raw, expected_sha=None, expected_image_sha=None):
    if expected_sha is not None:
        require(sha(raw) == expected_sha, 'AMXX SHA-256 mismatch')
    require(len(raw) >= 24, 'truncated AMXX header')
    magic, version, count = struct.unpack_from('<IHB', raw)
    require(magic == 0x414d5858, 'AMXX magic mismatch')
    require(version == 0x300 and count == 1, 'only single-entry AMXX v3 supported')
    cell, disk, size, memory, offset = struct.unpack_from('<BIIII', raw, 7)
    require(cell == 4 and offset == 24 and disk == len(raw) - offset,
            'invalid AMXX entry bounds/cell size')
    require(56 <= size <= 32 * 1024 * 1024 and memory >= 56,
            'invalid AMXX image/memory size (32 MiB safety limit)')
    try:
        stream = zlib.decompressobj()
        im = stream.decompress(raw[offset:], size + 1)
    except zlib.error as exc:
        raise Invalid(f'zlib decompression failed: {exc}') from exc
    require(stream.eof and not stream.unused_data and not stream.unconsumed_tail
            and len(im) == size, 'zlib stream length/termination mismatch')
    if expected_image_sha is not None:
        require(sha(im) == expected_image_sha, 'AMX SHA-256 mismatch')
    h = Header.parse(im)
    require(h.stp == memory, 'AMXX memory size differs from AMX stp')
    return im


@dataclass(frozen=True)
class Header:
    size: int
    magic: int
    version: int
    vm: int
    flags: int
    defsize: int
    cod: int
    dat: int
    hea: int
    stp: int
    cip: int
    publics: int
    natives: int
    libraries: int
    pubvars: int
    tags: int
    nametable: int

    @classmethod
    def parse(cls, im):
        require(len(im) >= 56, 'truncated AMX header')
        h = cls(*struct.unpack_from('<iHBBhh11i', im))
        require(h.magic == 0xf1e0, 'AMX magic mismatch')
        require(h.version == h.vm == 8 and h.defsize == 8, 'unsupported AMX format')
        require(h.flags in (0, 2), 'unsupported AMX flags (compact/relocated/etc.)')
        require(56 <= h.cod <= h.dat <= h.hea == h.size <= len(im)
                and h.stp >= h.hea, 'inconsistent AMX segment bounds')
        require(all(x % 4 == 0 for x in (h.cod, h.dat, h.hea, h.stp)),
                'unaligned AMX segments')
        tables = [h.publics, h.natives, h.libraries, h.pubvars, h.tags, h.nametable]
        require(tables[0] >= 56 and tables == sorted(tables)
                and tables[-1] + 2 <= h.cod
                and all((b - a) % 8 == 0 for a, b in zip(tables, tables[1:])),
                'invalid AMX definition table bounds')
        require(h.cip == -1 or 0 <= h.cip < h.dat - h.cod and h.cip % 4 == 0,
                'invalid AMX entrypoint')
        return h

    def c_to_i(self, c):
        require(0 <= c < self.dat - self.cod, 'C offset outside code')
        return self.cod + c

    def d_to_i(self, d):
        require(0 <= d < self.hea - self.dat, 'D offset outside initialized data')
        return self.dat + d


def cstring(data, offset, end):
    require(0 <= offset < end <= len(data), 'string offset outside table')
    stop = data.find(b'\0', offset, end)
    require(stop >= 0, 'unterminated string')
    return data[offset:stop].decode('ascii', errors='backslashreplace'), stop + 1


def definitions(im, h):
    out = {}
    for name, start, end in zip(
            ('publics', 'natives', 'libraries', 'pubvars', 'tags'),
            (h.publics, h.natives, h.libraries, h.pubvars, h.tags),
            (h.natives, h.libraries, h.pubvars, h.tags, h.nametable)):
        entries = []
        for pos in range(start, end, 8):
            address, offset = struct.unpack_from('<II', im, pos)
            require(h.nametable + 2 <= offset < h.cod, 'definition name outside nametable')
            text, _ = cstring(im, offset, h.cod)
            entries.append({'address': address, 'name': text})
        out[name] = entries
    return out


def debug_info(im, h):
    require(h.flags & 2, 'debug symbols required for target analysis')
    base = h.size
    require(base + 22 <= len(im), 'truncated debug header')
    size, magic, version, vm, flags, *counts = struct.unpack_from('<iHBB7h', im, base)
    require(magic == 0xf1ef and version == vm == 8 and flags == 0,
            'invalid debug format')
    end = base + size
    require(end == len(im) and all(n >= 0 for n in counts), 'invalid debug bounds/counts')
    p = base + 22

    def take(fmt):
        nonlocal p
        n = struct.calcsize(fmt)
        require(p + n <= end, f'truncated debug record I={p}')
        values = struct.unpack_from(fmt, im, p)
        p += n
        return values

    def name():
        nonlocal p
        text, p = cstring(im, p, end)
        return text

    files, lines, symbols, tags, machines, states = [], [], [], [], [], []
    for _ in range(counts[0]):
        files.append({'C': take('<I')[0], 'name': name()})
    for _ in range(counts[1]):
        address, line = take('<Ii')
        require(address < h.dat - h.cod, 'debug line outside code')
        lines.append({'C': address, 'line_zero_based': line})
    for _ in range(counts[2]):
        address, tag, start, stop, ident, vclass, dims = take('<ihIIBBh')
        require(0 <= start <= stop <= h.dat - h.cod and dims >= 0,
                'invalid debug symbol scope/dimensions')
        symbol = dict(address=address, tag=tag, start=start, end=stop,
                      ident=ident, vclass=vclass, name=name())
        symbol['dimensions'] = [take('<hI') for _ in range(dims)]
        symbols.append(symbol)
    for _ in range(counts[3]):
        tags.append({'tag': take('<h')[0], 'name': name()})
    for _ in range(counts[4]):
        ident, address = take('<hI')
        machines.append({'id': ident, 'D': address, 'name': name()})
    for _ in range(counts[5]):
        ident, machine = take('<hh')
        states.append({'id': ident, 'machine': machine, 'name': name()})
    require(not any(im[p:end]), f'nonzero unparsed debug tail I={p}')
    return dict(files=files, lines=lines, symbols=symbols, tags=tags,
                machines=machines, states=states, zero_padding=end - p)


# Numeric ordering is the pinned AMXX enum, not a modern Pawn/SourcePawn table.
NAMES = '''NONE LOAD_PRI LOAD_ALT LOAD_S_PRI LOAD_S_ALT LREF_PRI LREF_ALT
LREF_S_PRI LREF_S_ALT LOAD_I LODB_I CONST_PRI CONST_ALT ADDR_PRI ADDR_ALT
STOR_PRI STOR_ALT STOR_S_PRI STOR_S_ALT SREF_PRI SREF_ALT SREF_S_PRI SREF_S_ALT
STOR_I STRB_I LIDX LIDX_B IDXADDR IDXADDR_B ALIGN_PRI ALIGN_ALT LCTRL SCTRL
MOVE_PRI MOVE_ALT XCHG PUSH_PRI PUSH_ALT PUSH_R PUSH_C PUSH PUSH_S POP_PRI
POP_ALT STACK HEAP PROC RET RETN CALL CALL_PRI JUMP JREL JZER JNZ JEQ JNEQ
JLESS JLEQ JGRTR JGEQ JSLESS JSLEQ JSGRTR JSGEQ SHL SHR SSHR SHL_C_PRI SHL_C_ALT
SHR_C_PRI SHR_C_ALT SMUL SDIV SDIV_ALT UMUL UDIV UDIV_ALT ADD SUB SUB_ALT AND OR
XOR NOT NEG INVERT ADD_C SMUL_C ZERO_PRI ZERO_ALT ZERO ZERO_S SIGN_PRI SIGN_ALT
EQ NEQ LESS LEQ GRTR GEQ SLESS SLEQ SGRTR SGEQ EQ_C_PRI EQ_C_ALT INC_PRI INC_ALT
INC INC_S INC_I DEC_PRI DEC_ALT DEC DEC_S DEC_I MOVS CMPS FILL HALT BOUNDS
SYSREQ_PRI SYSREQ_C FILE LINE SYMBOL SRANGE JUMP_PRI SWITCH CASETBL SWAP_PRI
SWAP_ALT PUSHADDR NOP SYSREQ_D SYMTAG BREAK FLOAT_MUL FLOAT_DIV FLOAT_ADD
FLOAT_SUB FLOAT_TO FLOAT_ROUND FLOAT_CMP'''.split()
ONE = set('''LOAD_PRI LOAD_ALT LOAD_S_PRI LOAD_S_ALT LREF_PRI LREF_ALT
LREF_S_PRI LREF_S_ALT LODB_I CONST_PRI CONST_ALT ADDR_PRI ADDR_ALT STOR_PRI
STOR_ALT STOR_S_PRI STOR_S_ALT SREF_PRI SREF_ALT SREF_S_PRI SREF_S_ALT STRB_I
LIDX_B IDXADDR_B ALIGN_PRI ALIGN_ALT LCTRL SCTRL PUSH_R PUSH_C PUSH PUSH_S
STACK HEAP JREL SHL_C_PRI SHL_C_ALT SHR_C_PRI SHR_C_ALT ADD_C SMUL_C ZERO
ZERO_S EQ_C_PRI EQ_C_ALT INC INC_S DEC DEC_S MOVS CMPS FILL HALT BOUNDS
PUSHADDR SYSREQ_D SYSREQ_C SYMTAG'''.split())
ABSOLUTE = set('CALL JUMP JZER JNZ JEQ JNEQ JLESS JLEQ JGRTR JGEQ JSLESS JSLEQ JSGRTR JSGEQ SWITCH'.split())
DATA = set('LOAD_PRI LOAD_ALT LREF_PRI LREF_ALT STOR_PRI STOR_ALT SREF_PRI SREF_ALT PUSH ZERO INC DEC'.split())
FRAME = set('LOAD_S_PRI LOAD_S_ALT LREF_S_PRI LREF_S_ALT ADDR_PRI ADDR_ALT STOR_S_PRI STOR_S_ALT SREF_S_PRI SREF_S_ALT PUSH_S ZERO_S INC_S DEC_S PUSHADDR'.split())
TERMINAL = set('RET RETN HALT JUMP JREL JUMP_PRI SWITCH'.split())
INDIRECT = set('CALL_PRI JUMP_PRI SYSREQ_PRI SYSREQ_D'.split())


@dataclass(frozen=True)
class Op:
    number: int
    name: str
    types: tuple
    length: object
    flow: bool
    rule: str


def make_isa():
    result = {}
    for num, name in enumerate(NAMES[1:], 1):
        types = ('cell',) if name in ONE else ()
        rule = 'fixed'
        if name in ABSOLUTE:
            types, rule = ('C',), 'absolute C target'
        elif name == 'JREL':
            types, rule = ('displacement',), 'C + 8 + signed displacement'
        elif name in DATA:
            types = ('D',)
        elif name in FRAME:
            types = ('FRM',)
        elif name == 'SYSREQ_C':
            types = ('native_index',)
        elif name == 'SYSREQ_D':
            types, rule = ('native_pointer',), 'runtime direct pointer; not an index'
        elif name == 'SCTRL':
            types, rule = ('control_register',), 'register 6 writes CIP from PRI (indirect jump); amx.cpp:1984-2005'
        elif name in ('LINE', 'SRANGE'):
            types = ('cell', 'cell')
        elif name in ('FILE', 'SYMBOL'):
            types, rule = ('byte_count', 'payload'), '8 + byte_count; opaque obsolete debug payload'
        elif name == 'CASETBL':
            types, rule = ('count', 'default_C', 'value/C pairs'), '4 * (3 + 2 * count); non-executable'
        variable = name in ('FILE', 'SYMBOL', 'CASETBL')
        result[num] = Op(num, name, types, None if variable else 4 * (1 + len(types)),
                         name in ABSOLUTE | TERMINAL | INDIRECT | {'SYSREQ_C', 'SCTRL'}, rule)
    return result


ISA = make_isa()


@dataclass(frozen=True)
class Instruction:
    c: int
    spec: Op
    operands: tuple
    raw: bytes
    targets: tuple

    @property
    def length(self):
        return len(self.raw)


def unresolved_control(ins):
    return ins.spec.name in INDIRECT or ins.spec.name == 'SCTRL' and ins.operands == (6,)


def terminal(ins):
    return ins.spec.name in TERMINAL or ins.spec.name == 'SCTRL' and ins.operands == (6,)


def decode(code, start, end):
    require(0 <= start <= end <= len(code) and start % 4 == end % 4 == 0,
            'invalid code interval')
    out, c = [], start
    while c < end:
        opcode = struct.unpack_from('<I', code, c)[0]
        spec = ISA.get(opcode)

        def fail(reason):
            raise Invalid(f'C={c} bytes={code[c:min(c + 24, end)].hex()} '
                          f'opcode={opcode}: {reason}; amx.cpp:508-775')

        if spec is None:
            fail('unknown opcode')
        length = spec.length
        if length is None:
            if c + 8 > end:
                fail('truncated variable instruction')
            n = struct.unpack_from('<i', code, c + 4)[0]
            if n < 0:
                fail('negative variable instruction count')
            length = 4 * (3 + 2 * n) if spec.name == 'CASETBL' else 8 + n
            if length % 4:
                fail('unaligned obsolete debug payload')
        if c + length > end:
            fail('truncated instruction/operands')
        operands = struct.unpack_from('<' + 'i' * (length // 4 - 1), code, c + 4)
        targets = ()
        if spec.name in ABSOLUTE:
            targets = (operands[0],)
        elif spec.name == 'JREL':
            targets = (c + 8 + operands[0],)
        elif spec.name == 'CASETBL':
            targets = (operands[1],) + operands[3::2]
        out.append(Instruction(c, spec, operands, code[c:c + length], targets))
        c += length
    require(c == end, 'decoder did not end at exact boundary')
    return out


def validate(instructions, code_size, native_count, boundaries=None):
    known = boundaries if boundaries is not None else {i.c: i for i in instructions}
    checked = set()

    def check(ins):
        if ins.c in checked:
            return
        checked.add(ins.c)
        name = ins.spec.name

        def valid(condition, reason):
            require(condition, f'C={ins.c} bytes={ins.raw.hex()} '
                    f'opcode={ins.spec.number}:{name}: {reason}; amx.cpp:508-775,2508-2521')

        for target in ins.targets:
            valid(0 <= target < code_size, f'target C={target} outside code')
            valid(target in known, f'unestablished instruction boundary C={target}')
            is_table = known[target].spec.name == 'CASETBL'
            valid(is_table if name == 'SWITCH' else not is_table,
                  f'target C={target} must be CASETBL' if name == 'SWITCH'
                  else f'executable destination is a case table C={target}')
            if name == 'SWITCH':
                check(known[target])
        if name == 'SYSREQ_C':
            valid(0 <= ins.operands[0] < native_count, 'invalid native index')
    for ins in instructions:
        check(ins)
    # Physical fallthrough into a table cannot be executable, including after CALL.
    for ins in instructions:
        nxt = known.get(ins.c + ins.length)
        if not terminal(ins) and ins.spec.name != 'CASETBL' and nxt is not None:
            require(nxt.spec.name != 'CASETBL', f'C={ins.c} bytes={ins.raw.hex()} '
                    f'opcode={ins.spec.number}: fallthrough into case table; amx.cpp:2519-2521')


def references(ins, symbols):
    """Only exact-address evidence; no pointer propagation or array extent guesses."""
    name = ins.spec.name
    if not ins.operands:
        return []
    kind = ins.spec.types[0] if ins.spec.types else ''
    if kind not in ('D', 'FRM') and name not in ('CONST_PRI', 'CONST_ALT', 'PUSH_C'):
        return []
    out = []
    for sym in symbols:
        if sym['ident'] == 9 or sym['address'] != ins.operands[0]:
            continue
        # compiler/libpc300/sc.h:235-237: static=2 has D storage, local scope.
        local = sym['vclass'] == 1
        if sym['vclass'] != 0 and not sym['start'] <= ins.c < sym['end']:
            continue
        if kind == 'FRM' and not local or kind == 'D' and local:
            continue
        if kind not in ('D', 'FRM') and local:
            continue
        if name.startswith(('SREF', 'LREF')):
            effect, certainty = 'pointer-slot access; pointee unresolved', 'confirmed slot, candidate pointee'
        elif name.startswith(('ADDR', 'PUSHADDR')):
            effect, certainty = 'frame address formation', 'confirmed address'
        elif kind not in ('D', 'FRM'):
            effect, certainty = 'constant equals global D address; possible address materialization', 'candidate'
        elif name.startswith(('LOAD', 'PUSH')):
            effect, certainty = 'direct slot read', 'confirmed'
        elif name.startswith(('STOR', 'ZERO')):
            effect, certainty = 'direct slot write', 'confirmed'
        else:
            effect, certainty = 'direct slot read/write', 'confirmed'
        out.append(dict(C=ins.c, operation=name, operand=ins.operands[0],
                        coordinate='FRM' if local else 'D', symbol=sym['name'],
                        effect=effect, certainty=certainty))
    return out


def basic_blocks(instructions, known):
    executable = [i for i in instructions if i.spec.name != 'CASETBL']
    if not executable:
        return []
    local = {i.c for i in executable}
    leaders = {executable[0].c}
    for ins in executable:
        targets = known[ins.targets[0]].targets if ins.spec.name == 'SWITCH' else ins.targets
        leaders.update(t for t in targets if t in local)
        if ins.spec.flow and ins.c + ins.length in local:
            leaders.add(ins.c + ins.length)
    # Tables separate executable spans even when no branch names their successor.
    for ins in instructions:
        if ins.spec.name == 'CASETBL' and ins.c + ins.length in local:
            leaders.add(ins.c + ins.length)
    blocks = []
    for ins in executable:
        if ins.c in leaders:
            blocks.append({'start_C': ins.c, 'end_C': ins.c, 'instructions': []})
        blocks[-1]['instructions'].append(ins.c)
        blocks[-1]['end_C'] = ins.c + ins.length
    for block in blocks:
        last = known[block['instructions'][-1]]
        targets = known[last.targets[0]].targets if last.spec.name == 'SWITCH' else last.targets
        successors = list(targets) if last.spec.name != 'CALL' else []
        if not terminal(last):
            successors.append(last.c + last.length)
        block['successors_C'] = sorted(set(successors))
        block['calls_C'] = list(last.targets) if last.spec.name == 'CALL' else []
        block['indirect_unresolved'] = unresolved_control(last)
    return blocks


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + '\n'


def analyze(raw):
    im = unpack_container(raw, AMXX_SHA, AMX_SHA)
    h = Header.parse(im)
    require(len(im) == 1684270 and (h.cod, h.dat, h.hea, h.size, h.stp) ==
            (4912, 337028, 1576260, 1576260, 1592644), 'target identity coordinates mismatch')
    defs, debug = definitions(im, h), debug_info(im, h)
    code = im[h.cod:h.dat]
    artifacts, summary, all_refs = {}, [], []
    known = None
    for name, start, end in REGIONS:
        try:
            matches = [s for s in debug['symbols'] if s['name'] == name and s['ident'] == 9]
            require(len(matches) == 1 and matches[0]['address'] == start
                    and matches[0]['start'] == start and matches[0]['end'] == end,
                    f'{name}: debug boundary mismatch')
            local = decode(code, start, end)
            require(local[0].spec.name == 'PROC', f'{name}: entry is not PROC')
            # Only after decoding A: linear global format scan, solely for boundaries.
            # No semantic reconstruction or publication of other functions occurs.
            if known is None:
                global_instructions = decode(code, 0, len(code))
                known = {i.c: i for i in global_instructions}
            require(start in known and (end in known or end == len(code)),
                    f'{name}: unaligned debug interval')
            require(all(i.c in known and i.raw == known[i.c].raw for i in local),
                    f'{name}: local/global instruction map disagreement')
            validate(local, len(code), len(defs['natives']), known)
            require(terminal(local[-1]) or local[-1].spec.name == 'CASETBL',
                    f'{name}: debug end has executable fallthrough')
            refs, lines = [], [f'VALIDATED structural region {name} C=[{start},{end})',
                               'C:code-relative I:image-absolute D:data-relative FRM:signed frame-relative',
                               'Raw operands remain signed decimal cells; no metric semantics inferred.']
            for ins in local:
                refs_here = references(ins, debug['symbols'])
                refs.extend(dict(region=name, **ref) for ref in refs_here)
                annotations = [f"{r['symbol']} ({r['certainty']}: {r['effect']})" for r in refs_here]
                if ins.spec.name == 'SYSREQ_C':
                    annotations.append('native=' + defs['natives'][ins.operands[0]]['name'])
                for target in ins.targets:
                    scope = 'inside-region' if start <= target < end else 'outside-region/global-boundary'
                    names = [s['name'] for s in debug['symbols'] if s['ident'] == 9 and s['address'] == target]
                    annotations.append(f'target C={target} {scope} ' + ','.join(names))
                for row in debug['lines']:
                    if row['C'] == ins.c:
                        annotations.append(f"debug-line-zero-based={row['line_zero_based']}")
                lines.append((f'C={ins.c:06d} I={h.c_to_i(ins.c):07d} '
                             f'bytes={ins.raw.hex()} op={ins.spec.number}:{ins.spec.name} '
                             f'operands={list(ins.operands)} length={ins.length} '
                             + '; '.join(annotations)).rstrip())
            blocks = basic_blocks(local, known)
            artifacts[name + '.txt'] = '\n'.join(lines) + '\n'
            artifacts[name + '.blocks.json'] = json_text(blocks)
            all_refs.extend(refs)
            summary.append(dict(name=name, start_C=start, end_C=end, status='validated',
                                instructions=len(local), blocks=len(blocks), bytes=end-start,
                                control_targets=sum(len(i.targets) for i in local)))
        except Invalid as exc:
            artifacts[name + '.txt'] = f'INVALID / PARTIAL {name}\n{exc}\n'
            summary.append(dict(name=name, status='invalid', reason=str(exc)))
            break
    if known is not None:
        counts = Counter(i.spec.name for i in known.values())
        artifacts['opcodes.json'] = json_text({'scope': 'global boundary-only scan',
            'observed': {name: {'id': NAMES.index(name), 'count': counts[name]}
                         for name in sorted(counts)},
            'isa': [dict(id=s.number, name=s.name, length=s.length, operands=s.types,
                         flow=s.flow, rule=s.rule) for s in ISA.values()]})
    artifacts['symbols.json'] = json_text({'definitions': defs, 'debug': debug})
    artifacts['references.json'] = json_text({'scope': 'three requested regions only',
        'references': all_refs, 'interest_symbols': [s for s in debug['symbols'] if s['name'] in INTEREST],
        'not_observed': sorted(INTEREST - {r['symbol'] for r in all_refs}),
        'warning': 'Exact numeric constant matches are candidates, not demonstrated array accesses or data dependencies.'})
    artifacts['validation.json'] = json_text(dict(amxx_sha256=sha(raw), amx_sha256=sha(im),
        source_revision=REVISION, image_size=len(im), header=h.__dict__, regions=summary,
        global_boundary_count=len(known) if known is not None else 0,
        global_scan='formats and boundaries only; not global CFG validation',
        unresolved_indirect=[dict(C=i.c, opcode=i.spec.name) for i in (known or {}).values()
                             if unresolved_control(i)],
        status='validated' if len(summary) == 3 and all(s['status'] == 'validated' for s in summary) else 'blocked'))
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('reference/kz_jump_stats.amxx'),
                        help='read-only original AMXX; pinned identity is mandatory')
    parser.add_argument('--output', type=Path, default=Path('analysis/amx_disassembly'),
                        help='new output directory outside reference/ (must not already exist)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    protected = root / 'reference'
    output = args.output.resolve()
    try:
        require(not output.is_relative_to(protected.resolve()), 'output cannot be inside reference/')
        require(not output.exists(), 'output already exists; choose a new output directory')
        with args.input.open('rb') as source:
            raw = source.read()
        artifacts = analyze(raw)
        output.mkdir(parents=True, exist_ok=False)
        for name, text in artifacts.items():
            (output / name).write_text(text, encoding='utf-8')
        require(sha(args.input.read_bytes()) == AMXX_SHA, 'source changed during analysis')
        status = json.loads(artifacts['validation.json'])['status']
        print(f'{status}: {len(artifacts)} reproducible text artifacts in {args.output}')
        return 0 if status == 'validated' else 1
    except (Invalid, OSError) as exc:
        parser.exit(1, f'BLOCKED: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
