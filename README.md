# Outlast Head Bob Remover

A tool to remove head bobbing in **Outlast (2013)** by modifying the `OLGame.upk` file.

This project includes a graphical patcher that allows players to disable head bobbing by modifying the camera animation data stored in the original game package.

## Requirements

- A legitimate installation of **Outlast (2013)** from Steam. This project is an unofficial fan-made modification and does not include or distribute any game files.
- Windows 10/11.
- Python 3.8 or higher with tkinter (the official python.org installer already includes it).

## How to install

1. Close Outlast

2. Extract **Outlast-Head-Bob-Remover.zip** to:
   `Steam\steamapps\common\Outlast\OLGame\CookedPCConsole\`
   (`OLGame.upk` must be next to the patcher).

3. Run **Outlast-Head-Bob-Remover.exe**

4. Choose the options and click **Apply Changes**

5. Open the game

6. To return to the original, use **Restore Original File**

## Technical Overview

Outlast retrieves the camera's position and rotation directly from the `Hero-Camera` bone of the current animation using:

- `Mesh.GetBoneLocation`
- `Mesh.GetBoneQuaternion`

There is no in-game configuration option to disable head bobbing. The camera movement is embedded in the animation keyframes of the 360 animations contained in the `03_Hero.Hero-01_AS` AnimSet inside `OLGame.upk`.

The patcher locates the `Hero-Camera` bone through `TrackBoneNames`, identifies the translation and rotation tracks of each `AnimSequence`, and makes the selected keyframes constant by using the average translation and average rotation quaternion.

The patcher:

- Preserves the original keyframe sizes, offsets, and timing.
- Modifies only the selected animations.
- Uses the average translation and rotation to eliminate camera movement caused by head bobbing.
- Automatically creates an `OLGame.upk.backup` file containing the original game package.

The original game file can be restored using the patcher's restoration option.

## Credits

### Native UE3 decompression (Python)

The patcher includes a native Python implementation of UE3 package decompression (based on Gildor's PackageUnpack algorithm) that handles:

- **zlib** (CompressionFlags=1) — Python's built-in `zlib`
- **LZO** (CompressionFlags=2, used by Outlast) — built-in LZO1X decoder, pure Python, no C compiler needed. The optional `minilzo` package is used when present because it is faster.

### Outlast

Outlast (2013), including its original game assets and files, is the property of its respective copyright holders, including Red Barrels.

This project is an unofficial fan-made modification and is not affiliated with, endorsed by, or sponsored by Red Barrels.

## License

The original code and documentation developed for this project are licensed under the **MIT License**.

Third-party tools and game assets are not covered by this license and remain subject to their respective owners' terms and licenses.

See `LICENSE` for details.
