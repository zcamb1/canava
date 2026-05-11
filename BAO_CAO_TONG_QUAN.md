import re
import json
from pathlib import Path


class DFCTranslatorExtractor:

    def init(self):
        self.sections = {}

    # ====================================
    # SPLIT SECTIONS
    # ====================================
    def split_sections(self, text):

        self.sections = {}

        current_section = None

        for line in text.splitlines():

            line = line.rstrip()

            section_match = re.match(r'^\[(.+?)\]', line)

            if section_match:

                current_section = section_match.group(1)

                self.sections[current_section] = []

            if current_section:
                self.sections[current_section].append(line)

        return self.sections

    # ====================================
    # EXTRACT ALL
    # ====================================
    def extract(self):

        translations = {}

        if "DEVICES" in self.sections:
            self.extract_devices(
                self.sections["DEVICES"],
                translations
            )

        if "SCENES" in self.sections:
            self.extract_scenes(
                self.sections["SCENES"],
                translations
            )

        if "CONVERSATIONS" in self.sections:
            self.extract_conversations(
                self.sections["CONVERSATIONS"],
                translations
            )

        return translations

    # ====================================
    # DEVICES
    # ====================================
    def extract_devices(self, lines, translations):

        for line in lines:

            line = line.strip()

            # location
            m = re.match(
                r'(location_\d+):\s*"([^"]+)"',
                line
            )

            if m:
                translations[f'{m.group(1)}.name'] = m.group(2)
                continue

            # room
            m = re.match(
                r'(room_\d+):\s*"([^"]+)"',
                line
            )

            if m:
                translations[f'{m.group(1)}.name'] = m.group(2)
                continue

            # device
            m = re.match(
                r'(device_\d+):\s*([^,]+),\s*"([^"]+)"(?:,\s*"([^"]+)")?',
                line
            )

            if m:

                device_id = m.group(1)

                device_name = m.group(3)

                translations[f'{device_id}.name'] = device_name

    # ====================================
    # SCENES
    # ====================================
    def extract_scenes(self, lines, translations):

        for line in lines:

            line = line.strip()

            # location
            m = re.match(
                r'(location_\d+):\s*"([^"]+)"',
                line
            )

            if m:
                translations[f'{m.group(1)}.name'] = m.group(2)
                continue

            # scene
            m = re.match(
                r'(scene_\d+):\s*"([^"]+)"',
                line
            )

            if m:
                translations[f'{m.group(1)}.name'] = m.group(2)

    # ====================================
    # CONVERSATIONS
    # ====================================
    def extract_conversations(self, lines, translations):

        idx = 1

        for line in lines:

            line = line.strip()

            m = re.match(
                r'User:\s*(.+)',
                line
            )

            if m:

                translations[
                    f'conversation.user.{idx}'
                ] = m.group(1)

                idx += 1


# ========================================
# RENDER TRANSLATED FILE
# ========================================
def render_translated_text(text, translated):

    output_lines = []

    conversation_idx = 1

    for line in text.splitlines():

        stripped = line.strip()

        # LOCATION
        m = re.match(
            r'(location_\d+):\s*"([^"]+)"',
            stripped
        )

        if m:

            key = f"{m.group(1)}.name"

            if key in translated:
            line = re.sub(
                    r'"([^"]+)"',
                    f'"{translated[key]}"',
                    line,
                    count=1
                )

        # ROOM
        m = re.match(
            r'(room_\d+):\s*"([^"]+)"',
            stripped
        )

        if m:

            key = f"{m.group(1)}.name"

            if key in translated:

                line = re.sub(
                    r'"([^"]+)"',
                    f'"{translated[key]}"',
                    line,
                    count=1
                )

        # DEVICE
        m = re.match(
            r'(device_\d+):\s*([^,]+),\s*"([^"]+)"(?:,\s*"([^"]+)")?',
            stripped
        )

        if m:

            key = f"{m.group(1)}.name"

            if key in translated:

                line = re.sub(
                    r'"([^"]+)"',
                    f'"{translated[key]}"',
                    line,
                    count=1
                )

        # SCENE
        m = re.match(
            r'(scene_\d+):\s*"([^"]+)"',
            stripped
        )

        if m:

            key = f"{m.group(1)}.name"

            if key in translated:

                line = re.sub(
                    r'"([^"]+)"',
                    f'"{translated[key]}"',
                    line,
                    count=1
                )

        # USER CONVERSATION
        m = re.match(
            r'User:\s*(.+)',
            stripped
        )

        if m:

            key = f"conversation.user.{conversation_idx}"

            if key in translated:

                line = re.sub(
                    r'User:\s*(.+)',
                    f'User: {translated[key]}',
                    line
                )

            conversation_idx += 1

        output_lines.append(line)

    return "\n".join(output_lines)


# ========================================
# FOLDER CONFIG
# ========================================

INPUT_FOLDER = "input_md"
EXTRACT_FOLDER = "translation_json"
TRANSLATED_FOLDER = "translated_json"
OUTPUT_FOLDER = "output_md"

Path(EXTRACT_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

# ========================================
# STEP 1 - EXTRACT ALL MD
# ========================================

parser = DFCTranslatorExtractor()

md_files = Path(INPUT_FOLDER).glob("*.md")

for md_file in md_files:

    print(f"Extracting: {md_file.name}")

    text = md_file.read_text(
        encoding="utf-8"
    )

    parser.split_sections(text)

    extracted = parser.extract()

    output_json_path = (
        Path(EXTRACT_FOLDER) /
        f"{md_file.stem}.json"
    )

    with open(output_json_path, "w", encoding="utf-8") as f:

        json.dump(
            extracted,
            f,
            indent=4,
            ensure_ascii=False
        )

print("\nEXTRACTION DONE")


# ========================================
# STEP 2 - RENDER BACK
# ========================================

translated_files = Path(TRANSLATED_FOLDER).glob("*.json")

for translated_file in translated_files:

    print(f"Rendering: {translated_file.name}")

    original_md_path = (
        Path(INPUT_FOLDER) /
        f"{translated_file.stem}.md"
    )

    if not original_md_path.exists():
        continue

    original_text = original_md_path.read_text(
        encoding="utf-8"
    )

    translated_json = json.loads(
        translated_file.read_text(
            encoding="utf-8"
        )
    )

    rendered_text = render_translated_text(
        original_text,
        translated_json
    )

    output_md_path = (
        Path(OUTPUT_FOLDER) /
        f"{translated_file.stem}.md"
    )

    output_md_path.write_text(
        rendered_text,
        encoding="utf-8"
    )

print("\nRENDER DONE")
