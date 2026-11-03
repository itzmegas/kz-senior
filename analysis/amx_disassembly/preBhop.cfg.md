# preBhop: complete mechanical CFG

Static decode of C[164904,171748); 1,123 instructions, 93 call-split blocks.
See [the report](../../docs/13-kz-rush-previous-speed-correction.md) for symbolic predicates and alias limits.

This table describes instruction/register predicates, not physical gameplay. Calls have normal fallthrough; native/BOUNDS faults are outside normal CFG edges. Read/write columns list explicit operations, not an exhaustive pointee analysis. Exact instructions, symbol candidates and native names are in [the JSON](preBhop.blocks.json). Every row is [V] decoded bytes; semantic p* effects assume ordinary native contracts.

| Block C (end exclusive) | Predicate / exit | Explicit loads / address operations | Explicit writes | Successors C | Effect on p* | Evidence |
|---|---|---|---|---|---|---|
| 164904–164984 | `JZER [166756]` | ADDR_ALT -64; LOAD_S_PRI 12 | FILL 64 | [164984, 166756] | unchanged by explicit speed-reference store | [V] JSON block 164904 |
| 164984–165024 | `JZER [165076]` | LOAD_S_PRI 12 | — | [165024, 165076] | unchanged by explicit speed-reference store | [V] JSON block 164984 |
| 165024–165060 | `JZER [165076]` | LOAD_S_PRI 12 | — | [165060, 165076] | unchanged by explicit speed-reference store | [V] JSON block 165024 |
| 165060–165076 | `JUMP [165080]` | — | — | [165080] | unchanged by explicit speed-reference store | [V] JSON block 165060 |
| 165076–165080 | `ZERO_PRI []` | — | — | [165080] | unchanged by explicit speed-reference store | [V] JSON block 165076 |
| 165080–165088 | `JZER [165624]` | — | — | [165088, 165624] | unchanged by explicit speed-reference store | [V] JSON block 165080 |
| 165088–165132 | `SYSREQ_C [28]` | PUSHADDR -64 | — | [165132] | unchanged by explicit speed-reference store | [V] JSON block 165088 |
| 165132–165348 | `CALL [1128]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I ; LOAD_S_PRI 12 | STOR_I  | [165348] | unchanged by explicit speed-reference store | [V] JSON block 165132 |
| 165348–165360 | `JZER [165480]` | — | — | [165360, 165480] | unchanged by explicit speed-reference store | [V] JSON block 165348 |
| 165360–165480 | `JUMP [165616]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12 | STOR_I  | [165616] | unchanged by explicit speed-reference store | [V] JSON block 165360 |
| 165480–165616 | `STOR_I []` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I  | STOR_I  | [165616] | unchanged by explicit speed-reference store | [V] JSON block 165480 |
| 165616–165624 | `JUMP [166748]` | — | — | [166748] | unchanged by explicit speed-reference store | [V] JSON block 165616 |
| 165624–165668 | `SYSREQ_C [28]` | PUSHADDR -64 | — | [165668] | unchanged by explicit speed-reference store | [V] JSON block 165624 |
| 165668–165804 | `JZER [166280]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12 | STOR_I  | [165804, 166280] | unchanged by explicit speed-reference store | [V] JSON block 165668 |
| 165804–165924 | `CALL [1128]` | LOAD_S_PRI 12; LOAD_I ; LOAD_I ; LOAD_S_PRI 12 | — | [165924] | unchanged by explicit speed-reference store | [V] JSON block 165804 |
| 165924–165936 | `JZER [166096]` | — | — | [165936, 166096] | unchanged by explicit speed-reference store | [V] JSON block 165924 |
| 165936–166072 | `SYSREQ_C [18]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12 | — | [166072] | unchanged by explicit speed-reference store | [V] JSON block 165936 |
| 166072–166096 | `JUMP [166272]` | — | STOR_I  | [166272] | unchanged by explicit speed-reference store | [V] JSON block 166072 |
| 166096–166256 | `SYSREQ_C [18]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I  | — | [166256] | unchanged by explicit speed-reference store | [V] JSON block 166096 |
| 166256–166272 | `STOR_I []` | — | STOR_I  | [166272] | unchanged by explicit speed-reference store | [V] JSON block 166256 |
| 166272–166280 | `JUMP [166748]` | — | — | [166748] | unchanged by explicit speed-reference store | [V] JSON block 166272 |
| 166280–166400 | `SYSREQ_C [18]` | LOAD_S_PRI 12; LOAD_I ; LOAD_I ; LOAD_S_PRI 12 | — | [166400] | unchanged by explicit speed-reference store | [V] JSON block 166280 |
| 166400–166440 | `CALL [1128]` | — | — | [166440] | unchanged by explicit speed-reference store | [V] JSON block 166400 |
| 166440–166452 | `JZER [166612]` | — | — | [166452, 166612] | unchanged by explicit speed-reference store | [V] JSON block 166440 |
| 166452–166588 | `SYSREQ_C [18]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12 | — | [166588] | unchanged by explicit speed-reference store | [V] JSON block 166452 |
| 166588–166612 | `JUMP [166748]` | — | STOR_I  | [166748] | unchanged by explicit speed-reference store | [V] JSON block 166588 |
| 166612–166748 | `STOR_I []` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I  | STOR_I  | [166748] | unchanged by explicit speed-reference store | [V] JSON block 166612 |
| 166748–166756 | `JUMP [167284]` | — | — | [167284] | unchanged by explicit speed-reference store | [V] JSON block 166748 |
| 166756–166800 | `SYSREQ_C [28]` | PUSHADDR -64 | — | [166800] | unchanged by explicit speed-reference store | [V] JSON block 166756 |
| 166800–167016 | `CALL [1128]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I ; LOAD_S_PRI 12 | STOR_I  | [167016] | unchanged by explicit speed-reference store | [V] JSON block 166800 |
| 167016–167028 | `JZER [167148]` | — | — | [167028, 167148] | unchanged by explicit speed-reference store | [V] JSON block 167016 |
| 167028–167148 | `JUMP [167284]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12 | STOR_I  | [167284] | unchanged by explicit speed-reference store | [V] JSON block 167028 |
| 167148–167284 | `STOR_I []` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_I ; LOAD_I  | STOR_I  | [167284] | unchanged by explicit speed-reference store | [V] JSON block 167148 |
| 167284–167340 | `SYSREQ_C [33]` | PUSHADDR -68; PUSH_S 12 | — | [167340] | unchanged by explicit speed-reference store | [V] JSON block 167284 |
| 167340–167392 | `SYSREQ_C [17]` | LOAD_S_PRI -68 | — | [167392] | unchanged by explicit speed-reference store | [V] JSON block 167340 |
| 167392–167452 | `SYSREQ_C [17]` | LOAD_S_PRI -68; LOAD_S_ALT -68 | STOR_S_PRI -68 | [167452] | unchanged by explicit speed-reference store | [V] JSON block 167392 |
| 167452–167496 | `CALL [380]` | — | — | [167496] | unchanged by explicit speed-reference store | [V] JSON block 167452 |
| 167496–167516 | `SYSREQ_C [19]` | — | — | [167516] | unchanged by explicit speed-reference store | [V] JSON block 167496 |
| 167516–167552 | `JZER [167720]` | LOAD_S_PRI 28 | STOR_S_PRI -68 | [167552, 167720] | unchanged by explicit speed-reference store | [V] JSON block 167516 |
| 167552–167704 | `SYSREQ_C [28]` | LOAD_S_PRI 12; PUSHADDR 16; LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | — | [167704] | unchanged by explicit speed-reference store | [V] JSON block 167552 |
| 167704–167720 | `JUMP [169048]` | — | — | [169048] | unchanged by explicit speed-reference store | [V] JSON block 167704 |
| 167720–167772 | `CALL [1300]` | LREF_S_PRI 20; LOAD_S_PRI -68 | — | [167772] | unchanged by explicit speed-reference store | [V] JSON block 167720 |
| 167772–167784 | `JZER [168720]` | — | — | [167784, 168720] | unchanged by explicit speed-reference store | [V] JSON block 167772 |
| 167784–167832 | `JZER [168108]` | LOAD_S_PRI 12 | — | [167832, 168108] | unchanged by explicit speed-reference store | [V] JSON block 167784 |
| 167832–168032 | `SYSREQ_C [28]` | LOAD_S_PRI 12; PUSHADDR -68; PUSH_S 20; LOAD_S_PRI 12; LOAD_S_PRI 12; PUSHADDR -64; LOAD_S_PRI 12; LOAD_I  | — | [168032] | unchanged by explicit speed-reference store | [V] JSON block 167832 |
| 168032–168108 | `JUMP [168712]` | LOAD_PRI 455504; LOAD_PRI 455508; LOAD_PRI 455512 | STOR_PRI 376888; STOR_PRI 376892; STOR_PRI 376896 | [168712] | unchanged by explicit speed-reference store | [V] JSON block 168032 |
| 168108–168156 | `CALL [684]` | LOAD_S_PRI -68; LOAD_S_ALT 24 | — | [168156] | unchanged by explicit speed-reference store | [V] JSON block 168108 |
| 168156–168168 | `JZER [168444]` | — | — | [168168, 168444] | unchanged by explicit speed-reference store | [V] JSON block 168156 |
| 168168–168368 | `SYSREQ_C [28]` | LOAD_S_PRI 12; PUSHADDR -68; PUSH_S 20; LOAD_S_PRI 12; LOAD_S_PRI 12; PUSHADDR -64; LOAD_S_PRI 12; LOAD_I  | — | [168368] | unchanged by explicit speed-reference store | [V] JSON block 168168 |
| 168368–168444 | `JUMP [168712]` | LOAD_PRI 455528; LOAD_PRI 455532; LOAD_PRI 455536 | STOR_PRI 376888; STOR_PRI 376892; STOR_PRI 376896 | [168712] | unchanged by explicit speed-reference store | [V] JSON block 168368 |
| 168444–168644 | `SYSREQ_C [28]` | LOAD_S_PRI 12; PUSHADDR -68; PUSH_S 20; LOAD_S_PRI 12; LOAD_S_PRI 12; PUSHADDR -64; LOAD_S_PRI 12; LOAD_I  | — | [168644] | unchanged by explicit speed-reference store | [V] JSON block 168444 |
| 168644–168712 | `STOR_PRI [376896]` | LOAD_PRI 455516; LOAD_PRI 455520; LOAD_PRI 455524 | STOR_PRI 376888; STOR_PRI 376892; STOR_PRI 376896 | [168712] | unchanged by explicit speed-reference store | [V] JSON block 168644 |
| 168712–168720 | `JUMP [169048]` | — | — | [169048] | unchanged by explicit speed-reference store | [V] JSON block 168712 |
| 168720–168764 | `SYSREQ_C [17]` | LOAD_S_PRI -68 | — | [168764] | unchanged by explicit speed-reference store | [V] JSON block 168720 |
| 168764–168980 | `SYSREQ_C [28]` | LOAD_S_PRI 12; PUSHADDR -68; PUSH_S 20; LOAD_S_PRI 12; LOAD_S_PRI 12; PUSHADDR -64; LOAD_S_PRI 12; LOAD_I  | SREF_S_PRI 20 | [168980] | p* ← floatmul(0.8f,M) | [V] JSON block 168764 |
| 168980–169048 | `STOR_PRI [376896]` | LOAD_PRI 455516; LOAD_PRI 455520; LOAD_PRI 455524 | STOR_PRI 376888; STOR_PRI 376892; STOR_PRI 376896 | [169048] | unchanged by explicit speed-reference store | [V] JSON block 168980 |
| 169048–169068 | `JZER [170036]` | LOAD_S_PRI 28 | — | [169068, 170036] | unchanged by explicit speed-reference store | [V] JSON block 169048 |
| 169068–169188 | `SYSREQ_C [28]` | PUSHADDR 16; LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | — | [169188] | unchanged by explicit speed-reference store | [V] JSON block 169068 |
| 169188–169268 | `SYSREQ_C [21]` | LOAD_S_PRI 16; LOAD_S_PRI 12 | — | [169268] | unchanged by explicit speed-reference store | [V] JSON block 169188 |
| 169268–169312 | `CALL [684]` | — | — | [169312] | unchanged by explicit speed-reference store | [V] JSON block 169268 |
| 169312–169324 | `JZER [169552]` | — | — | [169324, 169552] | unchanged by explicit speed-reference store | [V] JSON block 169312 |
| 169324–169396 | `SYSREQ_C [21]` | LOAD_S_PRI 16; LOAD_S_PRI 12 | — | [169396] | unchanged by explicit speed-reference store | [V] JSON block 169324 |
| 169396–169528 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | STOR_I  | [169528] | unchanged by explicit speed-reference store | [V] JSON block 169396 |
| 169528–169552 | `JUMP [170028]` | — | — | [170028] | unchanged by explicit speed-reference store | [V] JSON block 169528 |
| 169552–169624 | `SYSREQ_C [21]` | LOAD_S_PRI 16; LOAD_S_PRI 12 | — | [169624] | unchanged by explicit speed-reference store | [V] JSON block 169552 |
| 169624–169668 | `CALL [1128]` | — | — | [169668] | unchanged by explicit speed-reference store | [V] JSON block 169624 |
| 169668–169680 | `JZER [169908]` | — | — | [169680, 169908] | unchanged by explicit speed-reference store | [V] JSON block 169668 |
| 169680–169752 | `SYSREQ_C [21]` | LOAD_S_PRI 16; LOAD_S_PRI 12 | — | [169752] | unchanged by explicit speed-reference store | [V] JSON block 169680 |
| 169752–169884 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | STOR_I  | [169884] | unchanged by explicit speed-reference store | [V] JSON block 169752 |
| 169884–169908 | `JUMP [170028]` | — | — | [170028] | unchanged by explicit speed-reference store | [V] JSON block 169884 |
| 169908–170020 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | — | [170020] | unchanged by explicit speed-reference store | [V] JSON block 169908 |
| 170020–170028 | `STACK [20]` | — | — | [170028] | unchanged by explicit speed-reference store | [V] JSON block 170020 |
| 170028–170036 | `JUMP [171036]` | — | — | [171036] | unchanged by explicit speed-reference store | [V] JSON block 170028 |
| 170036–170196 | `SYSREQ_C [28]` | PUSH_S 20; LOAD_S_PRI 12; LOAD_S_PRI 12; PUSHADDR -64; LOAD_S_PRI 12; LOAD_I  | — | [170196] | unchanged by explicit speed-reference store | [V] JSON block 170036 |
| 170196–170276 | `SYSREQ_C [21]` | LREF_S_PRI 20; LOAD_S_PRI 12 | — | [170276] | unchanged by explicit speed-reference store | [V] JSON block 170196 |
| 170276–170320 | `CALL [684]` | — | — | [170320] | unchanged by explicit speed-reference store | [V] JSON block 170276 |
| 170320–170332 | `JZER [170560]` | — | — | [170332, 170560] | unchanged by explicit speed-reference store | [V] JSON block 170320 |
| 170332–170404 | `SYSREQ_C [21]` | LREF_S_PRI 20; LOAD_S_PRI 12 | — | [170404] | unchanged by explicit speed-reference store | [V] JSON block 170332 |
| 170404–170536 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | STOR_I  | [170536] | unchanged by explicit speed-reference store | [V] JSON block 170404 |
| 170536–170560 | `JUMP [171036]` | — | — | [171036] | unchanged by explicit speed-reference store | [V] JSON block 170536 |
| 170560–170632 | `SYSREQ_C [21]` | LREF_S_PRI 20; LOAD_S_PRI 12 | — | [170632] | unchanged by explicit speed-reference store | [V] JSON block 170560 |
| 170632–170676 | `CALL [1128]` | — | — | [170676] | unchanged by explicit speed-reference store | [V] JSON block 170632 |
| 170676–170688 | `JZER [170916]` | — | — | [170688, 170916] | unchanged by explicit speed-reference store | [V] JSON block 170676 |
| 170688–170760 | `SYSREQ_C [21]` | LREF_S_PRI 20; LOAD_S_PRI 12 | — | [170760] | unchanged by explicit speed-reference store | [V] JSON block 170688 |
| 170760–170892 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | STOR_I  | [170892] | unchanged by explicit speed-reference store | [V] JSON block 170760 |
| 170892–170916 | `JUMP [171036]` | — | — | [171036] | unchanged by explicit speed-reference store | [V] JSON block 170892 |
| 170916–171028 | `SYSREQ_C [28]` | LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I  | — | [171028] | unchanged by explicit speed-reference store | [V] JSON block 170916 |
| 171028–171036 | `STACK [20]` | — | — | [171036] | unchanged by explicit speed-reference store | [V] JSON block 171028 |
| 171036–171280 | `JZER [171376]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_S_PRI 28 | STOR_I ; STOR_I  | [171280, 171376] | unchanged by explicit speed-reference store | [V] JSON block 171036 |
| 171280–171376 | `JUMP [171468]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 16 | STOR_I  | [171468] | unchanged by explicit speed-reference store | [V] JSON block 171280 |
| 171376–171468 | `STOR_I []` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LREF_S_PRI 20 | STOR_I  | [171468] | unchanged by explicit speed-reference store | [V] JSON block 171376 |
| 171468–171724 | `CALL [464]` | LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 32; LOAD_S_PRI 12; LOAD_S_PRI 12; LOAD_I ; LOAD_S_PRI 12; LOAD_S_PRI 12 | STOR_I ; INC_I  | [171724] | unchanged by explicit speed-reference store | [V] JSON block 171468 |
| 171724–171748 | `RETN []` | — | STOR_I  | [] | unchanged by explicit speed-reference store | [V] JSON block 171724 |

## Register predicate key

`JZER`: PRI=0; `JNZ`: PRI!=0; signed comparison jumps compare PRI to ALT. `JUMP` has only its target; `RETN` exits. A call-split block ends at CALL/SYSREQ_C, not necessarily at a source-language branch. Float comparisons are CALLs to compiled operators; see report §5. All pre-correction entry branches reconverge at C167284. There is only one normal return, C171744.
