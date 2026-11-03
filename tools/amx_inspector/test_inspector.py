import hashlib
import struct
import unittest
import zlib

from tools.amx_inspector import inspector as a


def cells(*values):
    return struct.pack('<' + 'i' * len(values), *values)


def image(code=b'', data=b''):
    cod = 60
    dat = cod + len(code)
    hea = dat + len(data)
    return (struct.pack('<iHBBhh11i', hea, 0xf1e0, 8, 8, 0, 8,
                        cod, dat, hea, hea + 64, -1,
                        56, 56, 56, 56, 56, 56) + b'\x1f\0\0\0' + code + data)


def container(im):
    compressed = zlib.compress(im)
    return struct.pack('<IHBBIIII', 0x414d5858, 0x300, 1, 4,
                       len(compressed), len(im), len(im) + 64, 24) + compressed


class ContainerTests(unittest.TestCase):
    def test_valid_and_coordinates(self):
        im = image(cells(46, 48), cells(7))
        raw = container(im)
        got = a.unpack_container(raw, hashlib.sha256(raw).hexdigest(),
                                 hashlib.sha256(im).hexdigest())
        h = a.Header.parse(got)
        self.assertEqual(got, im)
        self.assertEqual((h.c_to_i(4), h.d_to_i(0)), (64, 68))

    def test_bad_container_magic(self):
        with self.assertRaisesRegex(a.Invalid, 'magic'):
            a.unpack_container(b'BAD!' + container(image())[4:])

    def test_bad_hashes(self):
        raw = container(image())
        for args in [('0' * 64, None), (None, '0' * 64)]:
            with self.subTest(args=args), self.assertRaisesRegex(a.Invalid, 'SHA-256'):
                a.unpack_container(raw, *args)

    def test_bad_compression(self):
        raw = container(image())
        with self.assertRaisesRegex(a.Invalid, 'zlib'):
            a.unpack_container(raw[:24] + b'x' * (len(raw) - 24))

    def test_truncated_and_trailing_stream(self):
        raw = container(image())
        with self.assertRaises(a.Invalid):
            a.unpack_container(raw[:-1])
        with self.assertRaises(a.Invalid):
            a.unpack_container(raw + b'junk')

    def test_invalid_headers(self):
        for offset, fmt, value in [(4, '<H', 0), (6, '<B', 9),
                                   (8, '<h', 4), (10, '<h', 12),
                                   (16, '<i', 12), (32, '<i', 1000)]:
            im = bytearray(image(cells(46)))
            struct.pack_into(fmt, im, offset, value)
            with self.subTest(offset=offset), self.assertRaises(a.Invalid):
                a.Header.parse(im)


class DecodeTests(unittest.TestCase):
    def decode(self, *words, natives=0):
        code = cells(*words)
        result = a.decode(code, 0, len(code))
        a.validate(result, len(code), natives)
        return result

    def test_known_signed_frame(self):
        ins = self.decode(46, 3, -12, 48)
        self.assertEqual((ins[1].spec.name, ins[1].operands, ins[1].length),
                         ('LOAD_S_PRI', (-12,), 8))
        self.assertEqual(ins[1].spec.types, ('FRM',))

    def test_unknown(self):
        with self.assertRaisesRegex(a.Invalid, 'C=0.*opcode=145'):
            a.decode(cells(145), 0, 4)

    def test_truncated(self):
        with self.assertRaisesRegex(a.Invalid, 'truncated'):
            a.decode(cells(11), 0, 4)

    def test_absolute_call_and_jump(self):
        ins = self.decode(49, 16, 51, 16, 48)
        self.assertEqual([i.targets for i in ins[:2]], [(16,), (16,)])

    def test_relative_signed_jump(self):
        ins = self.decode(46, 52, -12)
        self.assertEqual(ins[1].targets, (0,))

    def test_native(self):
        self.assertEqual(self.decode(123, 0, natives=1)[0].operands, (0,))
        with self.assertRaisesRegex(a.Invalid, 'native'):
            self.decode(123, 1, natives=1)
        with self.assertRaisesRegex(a.Invalid, 'native'):
            self.decode(123, -1, natives=1)

    def test_switch_and_table(self):
        ins = self.decode(129, 12, 48, 130, 1, 8, -7, 8)
        self.assertEqual(ins[2].length, 20)
        self.assertEqual(ins[2].targets, (8, 8))
        self.assertEqual(ins[2].operands, (1, 8, -7, 8))

    def test_switch_requires_table(self):
        with self.assertRaisesRegex(a.Invalid, 'CASETBL'):
            self.decode(129, 8, 48)

    def test_executable_target_cannot_be_table(self):
        with self.assertRaisesRegex(a.Invalid, 'table'):
            self.decode(51, 8, 130, 0, 0)

    def test_invalid_case_count_and_truncation(self):
        for words in [(130, -1, 0), (130, 2, 0), (130,)]:
            with self.subTest(words=words), self.assertRaises(a.Invalid):
                a.decode(cells(*words), 0, len(words) * 4)

    def test_out_of_range_and_unaligned_targets(self):
        for target in [-4, 8, 2, 4]:
            with self.subTest(target=target), self.assertRaises(a.Invalid):
                self.decode(51, target)

    def test_outside_region_requires_independent_boundary(self):
        code = cells(49, 12, 48, 46, 48)
        local = a.decode(code, 0, 8)
        with self.assertRaisesRegex(a.Invalid, 'unestablished'):
            a.validate(local, len(code), 0)
        global_map = a.decode(code, 0, len(code))
        a.validate(local, len(code), 0, {i.c: i for i in global_map})

    def test_no_sysreq_n_and_direct_native_is_not_index(self):
        self.assertEqual(a.ISA[135].name, 'SYSREQ_D')
        self.assertNotIn('SYSREQ_N', [s.name for s in a.ISA.values()])
        self.assertEqual(self.decode(135, 123456)[0].operands, (123456,))

    def test_external_switch_table_targets_must_be_validated(self):
        code = cells(129, 12, 48, 130, 0, 10)
        global_map = {i.c: i for i in a.decode(code, 0, len(code))}
        with self.assertRaisesRegex(a.Invalid, 'boundary'):
            a.validate(a.decode(code, 0, 8), len(code), 0, global_map)

    def test_static_debug_symbol_uses_data_not_frame(self):
        sym = dict(name='static_value', address=8, ident=1, vclass=2,
                   start=0, end=32)
        data = a.decode(cells(1, 8), 0, 8)[0]
        frame = a.decode(cells(3, 8), 0, 8)[0]
        self.assertEqual(a.references(data, [sym])[0]['coordinate'], 'D')
        self.assertEqual(a.references(frame, [sym]), [])

    def test_native_call_flow_metadata(self):
        self.assertTrue(a.ISA[123].flow)

    def test_inline_debug_and_two_operand_format(self):
        ins = self.decode(124, 4, 0, 125, 10, 20, 136, 1, 48)
        self.assertEqual([i.length for i in ins], [12, 12, 8, 4])

    def test_fallthrough_into_table_rejected(self):
        with self.assertRaisesRegex(a.Invalid, 'fallthrough'):
            self.decode(134, 130, 0, 0)

    def test_enum_anchors(self):
        self.assertEqual(len(a.NAMES), 145)
        self.assertEqual([(a.ISA[n].name, a.ISA[n].length) for n in (46, 49, 117, 138)],
                         [('PROC', 4), ('CALL', 8), ('MOVS', 8), ('FLOAT_MUL', 4)])

    def test_control_register_cip_write_is_indirect_jump(self):
        ins = self.decode(32, 6, 48)
        self.assertTrue(ins[0].spec.flow)
        blocks = a.basic_blocks(ins, {i.c: i for i in ins})
        self.assertTrue(blocks[0]['indirect_unresolved'])
        self.assertEqual(blocks[0]['successors_C'], [])


class TargetTests(unittest.TestCase):
    def test_pinned_target_progression_and_reproducibility(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[2] / 'reference/kz_jump_stats.amxx'
        raw = path.read_bytes()
        before = hashlib.sha256(raw).hexdigest()
        first = a.analyze(raw)
        self.assertEqual(first, a.analyze(raw))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
        import json
        report = json.loads(first['validation.json'])
        self.assertEqual(report['status'], 'validated')
        self.assertEqual([r['instructions'] for r in report['regions']], [42, 55, 1729])
        self.assertEqual([r['bytes'] for r in report['regions']], [268, 348, 9892])


if __name__ == '__main__':
    unittest.main()
