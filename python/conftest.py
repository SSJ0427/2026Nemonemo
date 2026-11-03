# python/ 폴더를 import 경로에 넣어 `import scanner` 가 되게 한다.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
