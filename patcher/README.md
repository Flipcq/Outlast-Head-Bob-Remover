# Outlast Head Bob Remover

Removes **Head Bob** (camera sway) from Outlast, with an option to also remove
**breathing** sway when Miles is standing still.

The patcher edits `OLGame.upk` in the `CookedPCConsole` folder, creates a backup
of the original file, and allows you to restore everything later.

---

## 1. How to use

1. Close Outlast
2. Copy **Outlast-HeadBob-Remover.exe** to:
   `...\Steam\steamapps\common\Outlast\OLGame\CookedPCConsole\`
   (`OLGame.upk` must be next to the patcher).
3. Run ****Outlast-HeadBob-Remover.exe**
4. Choose the options and click **Apply Changes**
5. Open the game
6. To return to the original, use **Restore Original File**

### Requirements

- Windows 10/11
- The **Outlast** (2013) game from Steam, with the original `OLGame.upk`

---

## 2. Interface options

### Remove breathing Head Bob? (recommended)

Removes camera sway when Miles is **standing still**, crouching, leaning,
in bed, in the closet, or holding the camera. Without this option, the idle
(breathing) sway continues.

### Removal mode

| Mode                     | What it removes                                                                                            | Approx. animations |
| ------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------ |
| **Walk + Run (default)** | Normal walk/run cycles: forward, backward, strafes, and water variants.                                    | 12                 |
| **Walk + Run (all)**     | Every animation with `walk` or `run` in the name: crouching, limping, injured, stairs, jumps, transitions. | 51                 |
| **Walk only**            | All walk animations (`walk`).                                                                              | 41                 |
| **Run only**             | All run animations (`run`).                                                                                | 10                 |
| **All animations**       | All 360 Miles animations (idle, walk, run, crouch, jumps, falls, interactions, fatalities).                | 360                |

Counts are from the PC `OLGame.upk` (Outlast + Whistleblower). The patcher shows
the actual count after applying.

---

## 3. Backup and safety

- On first application, the patcher creates **`OLGame.upk.backup`** with the
  original file, and creates it only **once** (never overwrites an existing backup).
- If a backup already exists, it is used as a clean source: applying again with
  another mode **does not** stack patches. The patcher **automatically restores
  `OLGame.upk` from the backup** before applying the new configuration, so you
  do not need to click "Restore Original File" when switching modes.
- If the backup is missing but `OLGame.upk` appears to be modified
  (an entire group of animations without sway), the patcher **refuses** to create
  a backup and asks you to verify the files on Steam.
- `Restore Original File` renames `OLGame.upk.backup` back to `OLGame.upk`,
  replacing the modified file, and deletes the state record.
- The game must be closed to write/restore (otherwise Windows locks the file).

Files created in the folder:

```
OLGame.upk              -> modified package (or original restored)
OLGame.upk.backup       -> copy of the original OLGame.upk
OLGame.headbob.json     -> record of the applied patch (options and count)
```

---

## 4. About OLGame.upk compression

Outlast's `OLGame.upk` is a compressed UE3 package (LZO). The patcher can
decompress it natively in Python, with **no external tool and no C compiler**:

- **zlib** (CompressionFlags=1) — Python's built-in `zlib`
- **LZO** (CompressionFlags=2, used by Outlast) — built-in LZO1X decoder
  (`_lzo1x_decompress`, pure Python). If the optional `minilzo` package is
  installed (`pip install minilzo`), it is used instead because it is faster;
  both produce identical output.

The process:

1. Reads the UE3 compressed-chunk table from the package header
2. Decompresses each chunk (zlib or LZO) and reconstructs the full package
3. Rebuilds the header: clears the `PKG_StoreCompressed` flag, zeroes
   `CompressionFlags`/`CompressedChunks.Num`, removes the chunk table
4. Writes the result (~85 MB instead of ~64 MB)

The decompressed file is a valid UE3 package that the game engine loads
normally (same type used by cooked mods in UDK).

Real measurement of the PC `OLGame.upk` (Outlast + Whistleblower): 64,747,498
bytes (LZO, 83 chunks) -> 85,630,236 bytes, in about 2-3 seconds with the
built-in decoder.

The final file is larger (~85 MB instead of ~64 MB); this is normal.
The backup keeps the original compressed file, so `Restore` returns the game
to factory state if something does not work.

---

## 5. Command line (advanced)

```bat
python Outlast-HeadBob-Remover.py --cli --package OLGame.upk --analyze
python Outlast-HeadBob-Remover.py --cli --package OLGame.upk --mode default --breathing --output OLGame.patched
python Outlast-HeadBob-Remover.py --cli --package OLGame.upk --mode walk_run_all --apply
python Outlast-HeadBob-Remover.py --cli --package OLGame.upk --restore
```

`--output` does not modify the original file; `--apply` uses the backup flow.

---

## 6. How Head Bob works in Outlast (technical summary)

1. `OLPlayerController.GetPlayerViewPoint()` calls `OLHero.GetCamera()`.
2. `OLHeroCamera` (native class) updates the view by reading **directly the
   `Hero-Camera` bone from the animation**: `Mesh.GetBoneLocation("Hero-Camera")`
   and `Mesh.GetBoneQuaternion("Hero-Camera")`.
3. Therefore the sway does not come from a configuration variable: it is recorded
   in the **keyframes** of the `AnimSequence` entries of the `03_Hero.Hero-01_AS`
   AnimSet.
4. The patcher locates the AnimSet inside `OLGame.upk` (seekfree package
   containing the animations), finds the `Hero-Camera` bone index in
   `TrackBoneNames`, and flattens the translation and rotation keyframes of that
   bone only for the chosen animations.
5. In the skeleton (`RefSkeleton` of `Miles_beheaded`), the `Hero-Camera` is a
   child of `Hero-Root` (index 0), **not** of the head/neck. For this reason the
   body animation does not move the camera: all visible oscillation comes from
   the camera's local track, and flattening it removes Head Bob completely
   without freezing the body.

Format used (UE3 per-track compression, Outlast):

- `CompressedTrackOffsets`: 4 integers per bone: `transOffset, transKeys,
  rotOffset, rotKeys`.
- Each translation/rotation key occupies **12 bytes** (3 floats; for rotation
  the W is reconstructed).
- When `keys > 1`, after the keys comes an array of `keys` bytes with the times
  (aligned to 4 bytes). The patcher **does not change** sizes or times.
- Translation and rotation are replaced by the average (translation) / normalized
  average quaternion (rotation), maintaining the camera's base position and
  orientation and eliminating the oscillation.

Note: 5 fatality animations (`player_fatality_xplod_*` and
`player_grab_fatality_groom`) use a different track layout; they are safely
ignored (reported as `skipped_layout` by the command line).

---

## 7. Troubleshooting

- **Decompression**: `OLGame.upk` (LZO) is decompressed automatically by the
  built-in Python decoder, so `minilzo` is **not** required.
- **`minilzo` is optional**: install it (`pip install minilzo`) only if you
  want slightly faster decompression. On Windows that needs a C compiler
  (Visual Studio Build Tools), which is why the pure Python path exists.
- **Could not write/restore**: close the game (and Steam) and try again;
  Windows keeps the file open while the game is running.
- **`OLGame.upk appears to be already modified`**: restore via Steam (Verify
  integrity of game files) and apply again.

---

## 8. Developer self test

`tests/test_patcher.py` validates the whole pipeline (package reader, camera
track detection, LZO/zlib decompression, patch/verify, backup, restore and
CLI) **without** the real game file: it builds a synthetic UE3 package with
the same layout as `OLGame.upk` (see `tests/synth_pkg.py`) and includes hand
crafted LZO1X streams for the built-in decoder.

```bat
python tests/test_patcher.py
```

If `OLGame/OLGame.upk` exists in the repository root, an extra section runs
against the real package (360 animations, 5 fatality tracks skipped); with no
game file that section is simply skipped. Every line should print `ok` and
end with `ALL CHECKS PASSED`.

---

## 9. Disclaimer

Unofficial mod, not affiliated with Red Barrels. Use at your own risk.
Always keep the backup (`OLGame.upk.backup`) while testing.
