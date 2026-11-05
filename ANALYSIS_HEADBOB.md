# ANALYSIS_HEADBOB.md

Technical Analysis of Head Bob in Outlast (2013) and the Removal Patcher
========================================================================

License: MIT (see `LICENSE` in the project root).
Original technical documentation for the Outlast-Headbob-Remover project.

---

## 1. Context

Outlast (2013), developed by Red Barrels and based on Unreal Engine 3,
has no in-game configuration option to disable the **Head Bob** (camera sway
during walking, running, breathing, and other animations).

This sway does not come from an engine variable or an .ini file: it is
recorded directly in the **keyframes** of the `Hero-Camera` bone within the
`AnimSequence` entries of the `03_Hero.Hero-01_AS` AnimSet, stored in the
`OLGame.upk` package (a seekfree package containing Miles Upshur's animations).

The patcher in this project removes Head Bob by modifying those keyframes,
without touching any other package data.

---

## 2. How the Game Reads the Camera

Relevant flow (technical summary):

1. `OLPlayerController.GetPlayerViewPoint()` calls `OLHero.GetCamera()` (native).
2. `OLHeroCamera.Update()` reads the `Hero-Camera` bone location and rotation
   directly from the current animation via:
   - `Mesh.GetBoneLocation("Hero-Camera")`
   - `Mesh.GetBoneQuaternion("Hero-Camera")`
3. The read position receives shakes and neck offsets, but the base sway
   (walk/run/idle) comes entirely from the keyframes of the bone's local track.

In the skeleton (`RefSkeleton` of `Miles_beheaded`), the `Hero-Camera` is a
child of `Hero-Root` (index 0), **not** of the head/neck. For this reason the
body animation does not move the camera: all visible oscillation comes from the
camera's local track, and flattening that track removes Head Bob completely
without freezing the body.

---

## 3. Data Format (UE3 per-track compression, Outlast)

Inside each `AnimSequence` of the AnimSet, animation tracks are organized by
bone. For each bone there is a `CompressedTrackOffsets` structure with 4
integers:

- `transOffset` — offset of the translation track
- `transKeys` — number of translation keys
- `rotOffset` — offset of the rotation track
- `rotKeys` — number of rotation keys

Each key (translation or rotation) occupies **12 bytes** (3 floats; for
rotation the W component is reconstructed). When `keys > 1`, after the keys
comes an array of `keys` bytes with the times (aligned to 4 bytes).

The patcher **does not change** sizes, offsets, or times. It only replaces:

- Translation: with the average (average) of the original keys.
- Rotation: with the normalized average quaternion of the original keys.

Thus the camera's base position and orientation are preserved, and the
oscillation is eliminated.

### Note on the export table (`Generations`)

The PC `OLGame.upk` is a cooked package where each export's `Generations`
array stores **one 4-byte int per generation**, while the standard UE3
`FGenerationInfo` used by editor packages is 8 bytes
(`ExportCount` + `NameCount`). Reading the wrong size shifts every following
record, so the AnimSet is never found.

The reader therefore auto-detects the layout: it walks the export table with
both sizes and keeps the one that validates (name/class indices inside their
tables and `SerialOffset` chained to the previous record's data). On the PC
package the result is unambiguous:

```
export_offset 313,437  export_count 14,449  depends_offset 1,296,325
4 bytes/generation: table ends exactly at depends_offset   <- used
8 bytes/generation: chain breaks at export 12,584          <- rejected
```

---

## 4. Target Animations

The patcher identifies the `Hero-Camera` via `TrackBoneNames` and processes
only the `AnimSequence` entries chosen by the user. There are approximately
**360 animations** in the PC `OLGame.upk` (Outlast + Whistleblower).

Available modes:

| Mode                 | What it removes                                                                                            | Approx. animations |
| -------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------ |
| Walk + Run (default) | Normal walk/run cycles: forward, backward, strafes, and water variants                                     | 12                 |
| Walk + Run (all)     | Every animation with `walk` or `run` in the name (crouching, limping, injured, stairs, jumps, transitions) | 51                 |
| Walk only            | All walk animations (`walk`)                                                                               | 41                 |
| Run only             | All run animations (`run`)                                                                                 | 10                 |
| All animations       | All 360 animations (idle, walk, run, crouch, jumps, falls, interactions, fatalities)                       | 360                |

Optionally, removal of the **breathing** sway (idle) can be included — when
Miles is standing still, crouching, leaning, in bed, in the closet, or holding
the camera.

**Note:** 5 fatality animations (`player_fatality_xplod_*` and
`player_grab_fatality_groom`) use a different track layout and are safely
ignored (reported as `skipped_layout` by the command line).

---

## 5. Patching Flow and Safety

1. **Verification:** The patcher loads `OLGame.upk` (decompressing with a native Python implementation of UE3 package decompression (based on Gildor's PackageUnpack algorithm) and checks whether it is already
   modified.
2. **Backup:** On first application, it creates `OLGame.upk.backup` with the
   original file. The backup is not overwritten on subsequent applications.
3. **Application:** It restores `OLGame.upk` from the backup (if one exists)
   so patches do not stack, applies the selected modifications, and writes the
   modified file.
4. **State:** It saves `OLGame.headbob.json` with the applied patch record
   (mode, options, animation count, and modified keys).
5. **Restoration:** `Restore Original File` renames the backup back to
   `OLGame.upk` and deletes the state record.

Files created in the game folder:

```
OLGame.upk           -> modified package (or original restored)
OLGame.upk.backup    -> copy of the original OLGame.upk
OLGame.headbob.json  -> record of the applied patch
```

The game must be closed to write/restore, because Windows locks the file while
the game is running.

---

## 6. OLGame.upk Compression

Outlast's `OLGame.upk` is a compressed UE3 package (LZO, CompressionFlags=2,
83 chunks in the PC build). The patcher decompresses it natively in Python
without any external tool and without a C compiler:

- **zlib** (CompressionFlags=1) — Python's built-in `zlib`
- **LZO** (CompressionFlags=2, used by Outlast) — built-in LZO1X decoder
  (`_lzo1x_decompress`), a faithful pure Python port of
  `lzo1x_decompress_safe()` (literal runs, M1/M2/M3/M4 back-references with
  overlapping copies and the `11 00 00` end marker). The optional `minilzo`
  C extension is used first when installed, only because it is faster; the
  output is identical.

The process:

1. Reads the UE3 compressed-chunk table from the package header
2. Decompresses each chunk (zlib or LZO) and reconstructs the full package
3. Rebuilds the header: clears the `PKG_StoreCompressed` flag, zeroes
   `CompressionFlags`/`CompressedChunks.Num`, removes the chunk table
4. Writes the result (~85 MB instead of ~64 MB)

Measured on the PC `OLGame.upk` (Outlast + Whistleblower):

```
64,747,498 bytes (LZO, 83 chunks, 683 blocks) -> 85,630,236 bytes  (~2 s)
```

The decompressed file is a valid UE3 package that the game engine loads
normally (same type used by cooked mods in UDK).

The backup keeps the original **compressed** file, so `Restore` returns the
game to its factory state if something does not work.

---

## 7. Project Files

```
Outlast-Headbob-Remover/
├── LICENSE                     -> MIT license for code and documentation
├── README.md                   -> Usage documentation (English)
├── main.py                     -> Python entry point (MIT license)
├── ANALYSIS_HEADBOB.md         -> This technical analysis (MIT license)
└── patcher/
    ├── Outlast-HeadBob-Remover.py    -> Graphical patcher (tkinter) + CLI
    ├── Outlast-HeadBob-Remover.ico   -> Application icon
    ├── Outlast-HeadBob-Remover.spec  -> PyInstaller spec (icon + minilzo)
    ├── build_exe.bat                 -> Builds the .exe with PyInstaller
    ├── README.md                     -> Patcher documentation (English)
    └── tests/
        ├── synth_pkg.py              -> Synthetic UE3 package builder
        └── test_patcher.py           -> End-to-end self test
```

---

## 8. Disclaimers

- Unofficial mod, not affiliated with Red Barrels. Use at your own risk.
- The UE3 decompression routine is an original Python implementation based on
  the publicly documented PackageUnpack algorithm by Konstantin Nosov
  (Gildor); no third-party binary is bundled or executed.
- `OLGame.upk` and Outlast assets are property of their respective copyright
  holders, including Red Barrels.
- Always keep the backup (`OLGame.upk.backup`) while testing.
