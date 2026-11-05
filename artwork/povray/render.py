"""Render the editable POV-Ray study without installing or changing system files."""
import argparse
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', default='rhyme-trap.pov', help='POV scene filename within this directory')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--width', type=int, default=1600)
    parser.add_argument('--height', type=int, default=1000)
    parser.add_argument('--clock', type=float, default=0.38)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--output', default=None, help='PNG filename within this directory')
    args = parser.parse_args()
    binary = shutil.which('povray')
    if not binary:
        parser.error('POV-Ray is not installed.')
    if args.width < 1 or args.height < 1 or args.threads < 1:
        parser.error('Dimensions and thread count must be positive.')
    name = args.output or ('preview.png' if args.preview else 'rhyme-trap.png')
    if Path(args.scene).name != args.scene or not args.scene.lower().endswith('.pov'):
        parser.error('--scene must be a POV filename, not a path.')
    if not (HERE / args.scene).is_file():
        parser.error('The requested scene does not exist.')
    if Path(name).name != name or not name.lower().endswith('.png'):
        parser.error('--output must be a PNG filename, not a path.')
    # Debian's POV-Ray policy permits cwd and home reads, but not /usr/share/fonts.
    # Copy only this known, redistributable font and its license into the project.
    font = HERE / 'DejaVuSerif.ttf'
    if not font.exists():
        original = Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
        if not original.exists():
            parser.error('Place DejaVuSerif.ttf and its license beside this script.')
        shutil.copyfile(original, font)
        license_path = Path('/usr/share/doc/fonts-dejavu-core/copyright')
        if license_path.exists():
            shutil.copyfile(license_path, HERE / 'LICENSE-DejaVu.txt')
    width, height = (800, 500) if args.preview else (args.width, args.height)
    command = [binary, f'+I{args.scene}', f'+O{name}', f'+W{width}', f'+H{height}',
               '+FN8', '-D', '-P', f'+WT{args.threads}', f'+K{args.clock}',
               '+Q7' if args.preview else '+Q9']
    command += ['-A'] if args.preview else ['+A0.12', '+AM2', '+R2', '-J']
    print('Rendering', HERE / name, flush=True)
    subprocess.run(command, cwd=HERE, check=True)


if __name__ == '__main__':
    main()
