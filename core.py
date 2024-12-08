import skia
import os
from thefuzz import fuzz as tf
from rapidfuzz import fuzz as rf
from aiohttp import web
from glob import glob
from copydetect import CopyDetector
import numpy as np
import json
from jinja2 import Template
import pdfkit
import shutil

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'c'}

# Value for `transformation_factor`
# 0 < k <= 1: Compression factor, diluting the 40-50% and maintains for higher percentages.
# k > 1:      Expansion factor, creating a higher amount of percentage values.
# k <= 0:     Inverts the percentage values, NOT SUITABLE!
# Recommended ranges: 0.7 up to 0.9
# Recommended value for `least_plagiarism`: 30%
TF_FACTOR = 1
LEAST_PLG = 30.0



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For beginners learning C, there are many features in the standard libraries that they 
# might not encounter or fully appreciate until they have more experience. Below is a 
# categorized list of functions, macros, and tokens from the C Standard Library that are 
# less commonly used by beginners:
CItems: dict[str, list[str]] = {
    "Preprocessor Macros": [
        "__LINE__", "__FILE__", "__DATE__", "__TIME__", "MAX", "MIN",
        "CHAR_BIT", "MB_CUR_MAX", "FLT_EPSILON", "DBL_MAX", "LDBL_MIN"
    ],
    "Preprocessor Directives": [
        "#define", "#undef", "#include",
        "#if", "#elif", "#else", "#endif", "#ifdef", "#ifndef",
        "#pragma", "#error", "#line"
    ],
    "Keywords": [
        "register", "extern", "static", "volatile", "restrict", "_Bool", "_Complex", 
        "_Imaginary", "goto", "continue", "alignas", "alignof", "_Atomic", 
        "thread_local", "_Noreturn", "typedef", "enum", "union", "sizeof", 
        "inline", "_Static_assert", "_Generic"
    ],
    "Type-Related Features": [
        "alignof", "alignas", "atomic_load", "atomic_store", "static_assert"
    ],
    "Input/Output Functions": [
        "tmpfile", "setbuf", "setvbuf", "vprintf", "vsprintf", "sprintf", "snprintf", "freopen"
    ],
    "String and Character Functions": [
        "strtok", "strxfrm", "strcoll", "memmove", "memset", 
        "isalnum", "ispunct", "isgraph", "strncpy", "strncat",
        "memcpy", "strstr", "memchr", "memcmp", "strpbrk",
        "strspn", "strcspn", "strtok_r", "strrev"
    ],
    "Wide Characters": [
        "wprintf", "fwprintf", "wcscmp", "wcslen", "wmemcpy", "iswalpha", "iswdigit"
    ],
    "Math Functions": [
        "fmod", "modf", "hypot", "lgamma", "nan", "isnan", "isinf"
    ],
    "Complex Numbers": [
        "cabs", "carg", "creal", "cimag", "cpow"
    ],
    "Time Functions": [
        "difftime", "strftime", "clock", "mktime"
    ],
    "Memory Management": [
        "aligned_alloc", "reallocarray", "bsearch", "qsort", "memset"
    ],
    "Localization": [
        "setlocale", "localeconv"
    ],
    "Signals and Error Handling": [
        "signal", "raise", "strerror", "exit", "_Exit"
    ],
    "Multithreading": [
        "thrd_create", "mtx_lock", "mtx_unlock", "cnd_wait", "cnd_signal"
    ],
    "Windows.h": [
        "SetConsoleTextAttribute", "GetStdHandle", "CONSOLE_SCREEN_BUFFER_INFO",
        "FillConsoleOutputCharacter",  "FillConsoleOutputAttribute", "SetConsoleCursorPosition",
        "SetConsoleMode", "GetConsoleMode", "system"
    ],
}


# Helper function to process similarity
def process_similarity(Programs, TransformationFactor=1, LeastPlagiarism=30.0):
    TotalCodePrograms = len(Programs)
    Caches = []
    Tokenizes = []
    Scores = [
        [
            [
                [0 for _ in range(6)] for _ in range(TotalCodePrograms - 1)
            ] for _ in range(TotalCodePrograms)
        ] for _ in range(TotalCodePrograms)
    ]

    for program in Programs:
        with open(program, 'r', encoding='utf-8') as f:
            Tokenizes.append(f.readlines())
        with open(program, 'r', encoding='utf-8') as f:
            Caches.append("".join(f.readlines()))

    for i in range(TotalCodePrograms):
        for j in range(TotalCodePrograms):
            for k in range(TotalCodePrograms - 1):
                try:
                    Scores[i][j][k][0] = sum([
                        tf.token_set_ratio(Caches[i], Caches[j]),
                        rf.token_set_ratio(Caches[i], Caches[j])
                    ]) / 2
                    Scores[i][j][k][1] = sum([
                        tf.ratio(Caches[i], Caches[j]),
                        rf.ratio(Caches[i], Caches[j])
                    ]) / 2
                    Scores[i][j][k][2] = sum([
                        tf.token_sort_ratio(Caches[i], Caches[j]),
                        rf.token_sort_ratio(Caches[i], Caches[j])
                    ]) / 2
                    Scores[i][j][k][3] = sum([
                        tf.QRatio(Caches[i], Caches[j]),
                        rf.QRatio(Caches[i], Caches[j])
                    ]) / 2
                    Scores[i][j][k][4] = tf.UQRatio(Caches[i], Caches[j])
                    Scores[i][j][k][5] = pow(
                        (
                            (
                                (Scores[i][j][k][1] + Scores[i][j][k][2] +
                                ((Scores[i][j][k][3] + Scores[i][j][k][4]) / 2)) / 3 +
                                Scores[i][j][k][0]
                            ) / 2
                        ), TransformationFactor
                    )
                except IndexError:
                    continue

    results = []
    seen_pairs = set()  # Set to track unique pairs of programs

    for i in range(TotalCodePrograms):
        for j in range(i + 1, TotalCodePrograms):
            for k in range(TotalCodePrograms - 1):
                if (i == j or j == k or i == k) and (TotalCodePrograms > 2):
                    continue

                # Create a sorted tuple to represent the unique pair
                pair = tuple(sorted([Programs[i], Programs[j]]))

                if pair in seen_pairs:
                    continue  # Skip duplicates

                seen_pairs.add(pair)  # Add pair to the set

                results.append({
                    "score": Scores[i][j][k][5],
                    "program1": Programs[i].replace(UPLOAD_FOLDER+'/', ''),
                    "program2": Programs[j].replace(UPLOAD_FOLDER+'/', ''),
                })


    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    return {
        "total_programs": TotalCodePrograms,
        "results": sorted_results
    }


def process_ai_detection(request):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    Programs = glob(UPLOAD_FOLDER + '/*.c')

    TotalCodePrograms: int = len(Programs)
    Caches: list[str] = []
    Tokenizes: list[list] = []

    # Load programs and tokenize
    for program in Programs:
        with open(program, 'r', encoding='utf-8') as f:
            Tokenizes.append(f.readlines())
        with open(program, 'r', encoding='utf-8') as f:
            Caches.append("".join(f.readlines()))

    payload = {"programs": []}

    for item in range(TotalCodePrograms):
        program_data = {
            "filename": Programs[item].replace(UPLOAD_FOLDER + '/', ''),
            "lines": len(Tokenizes[item]),
            "categories": []
        }

        def generate_section_data(title, key):
            count_founded = 0
            found_keys = set()
            found_items = []

            for line, code_snippet in enumerate(Tokenizes[item]):
                for key_item in CItems[key]:
                    if key_item in code_snippet:
                        found_items.append({
                            "line": line,
                            "snippet": code_snippet.strip(),
                            "highlight": key_item
                        })
                        count_founded += 1
                        found_keys.add(key_item)

            if count_founded > 0:
                return {
                    "title": title,
                    "found_count": count_founded,
                    "targets": list(CItems[key]),
                    "found_targets": list(found_keys),
                    "found_items": found_items
                }
            return None

        # Add categories
        categories = [
            ("Preprocessor Macros", "Preprocessor Macros"),
            ("Preprocessor Directives", "Preprocessor Directives"),
            ("Keywords", "Keywords"),
            ("Type-Related Features", "Type-Related Features"),
            ("Input/Output Functions", "Input/Output Functions"),
            ("String and Character Functions", "String and Character Functions"),
            ("Wide Characters", "Wide Characters"),
            ("Math Functions", "Math Functions"),
            ("Complex Numbers", "Complex Numbers"),
            ("Time Functions", "Time Functions"),
            ("Memory Management", "Memory Management"),
            ("Localization", "Localization"),
            ("Signals and Error Handling", "Signals and Error Handling"),
            ("Multithreading", "Multithreading"),
            ("Windows.h", "Windows.h"),
        ]

        for title, key in categories:
            section_data = generate_section_data(title, key)
            if section_data:
                program_data["categories"].append(section_data)

        payload["programs"].append(program_data)

    return web.json_response(payload)

class CustomDetector(CopyDetector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def my_html(self, output_mode="save"):
        if len(self.similarity_matrix) == 0:
            return

        code_list = self.get_copied_code_list()
        scores=self.similarity_matrix[:,:,0][self.similarity_matrix[:,:,0]!=-1]
        
        # render template with jinja and save as html
        with open("templates/report.html", encoding="utf-8") as template_fp:
            template = Template(template_fp.read())

        flagged = self.similarity_matrix[:,:,0] > self.conf.display_t
        flagged_file_count = np.sum(np.any(flagged, axis=1))

        formatted_conf = json.dumps(self.conf.to_json(), indent=4)
        output = template.render(config_params=formatted_conf,
                                 version=1.0,
                                 test_count=len(self.test_files),
                                 test_files=self.test_files,
                                 compare_count=len(self.ref_files),
                                 compare_files=self.ref_files,
                                 flagged_file_count=flagged_file_count,
                                 code_list=code_list)

        with open('static/result.html', "w", encoding="utf-8") as report_f:
            report_f.write(output)

def generate_pdf_file(pdf_file, config_params, version, test_count, compare_count, code_list):
    stream = skia.FILEWStream(pdf_file)
    with skia.PDF.MakeDocument(stream) as document:
        # A4 page size
        A4_WIDTH = 595
        A4_HEIGHT = 842

        # Function to draw text with wrapping
        def draw_wrapped_text(canvas, text, x, y, max_width, paint, font):
            lines = []
            current_line = ""
            words = text.split()
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if font.measureText(test_line) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            # Draw each line
            line_height = font.getSpacing()
            for line in lines:
                canvas.drawString(line, x, y, font, paint)
                y += line_height

        # Render each page
        with document.page(A4_WIDTH, A4_HEIGHT) as canvas:
            # Setup font and paint
            header_font = skia.Font(skia.Typeface('Arial'), 16)
            text_font = skia.Font(skia.Typeface('Arial'), 12)
            text_paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)

            # Margins and positions
            margin = 50
            line_y = margin

            # Render header
            canvas.drawString("Matched Code Report", margin, line_y, header_font, text_paint)
            line_y += 30

            # Render configuration and version
            draw_wrapped_text(
                canvas,
                f"Configuration Parameters: {config_params}",
                margin,
                line_y,
                A4_WIDTH - 2 * margin,
                text_paint,
                text_font,
            )
            line_y += 20
            canvas.drawString(f"Version: {version}", margin, line_y, text_font, text_paint)
            line_y += 20
            canvas.drawString(f"Test Files Count: {test_count}", margin, line_y, text_font, text_paint)
            line_y += 20
            canvas.drawString(f"Comparison Files Count: {compare_count}", margin, line_y, text_font, text_paint)
            line_y += 30

            # Render code list
            for index, code in enumerate(code_list, start=1):
                if line_y > A4_HEIGHT - margin:  # Start a new page if out of space
                    line_y = margin
                    with document.page(A4_WIDTH, A4_HEIGHT) as canvas:
                        pass

                # Render each code comparison
                canvas.drawString(
                    f"Test File: {code[2]} ({code[0]*100:.2f}%)", margin, line_y, text_font, text_paint
                )
                line_y += 20
                canvas.drawString(
                    f"Reference File: {code[3]} ({code[1]*100:.2f}%)", margin, line_y, text_font, text_paint
                )
                line_y += 20
                canvas.drawString(f"Token Overlap: {code[6]}", margin, line_y, text_font, text_paint)
                line_y += 20

                # Matched code columns
                canvas.drawString("Matched Code (Test):", margin, line_y, text_font, text_paint)
                canvas.drawString("Matched Code (Reference):", A4_WIDTH // 2, line_y, text_font, text_paint)
                line_y += 20
                draw_wrapped_text(
                    canvas, code[4], margin, line_y, (A4_WIDTH // 2) - margin, text_paint, text_font
                )
                draw_wrapped_text(
                    canvas, code[5], A4_WIDTH // 2, line_y, (A4_WIDTH // 2) - margin, text_paint, text_font
                )
                line_y += 50

    print(f"PDF saved to {pdf_file}")

def compare(program1, program2):
    pdf_path = 'static' + '/result.pdf'
    html_path = 'static' + '/result.html'

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(html_path):
        os.remove(html_path)
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Remove any existing .c files in the OUTPUT_FOLDER
    for file in glob(OUTPUT_FOLDER + '/*.c'):
        os.remove(file)

    program1_path = UPLOAD_FOLDER + '/' + program1
    program2_path = UPLOAD_FOLDER + '/' + program2
    os.system(f'cp "{program1_path}" "{OUTPUT_FOLDER}"')
    os.system(f'cp "{program2_path}" "{OUTPUT_FOLDER}"')

    # Initialize the detector
    detector = CustomDetector(test_dirs=[OUTPUT_FOLDER], extensions=['c'], out_file=html_path, autoopen=False)
    detector.run()
    detector.my_html()
    # code_list = detector.get_copied_code_list()
    # formatted_conf = json.dumps(detector.conf.to_json(), indent=4)
    # generate_pdf_file('static/result.pdf', formatted_conf, 1.0, len(detector.test_files), len(detector.ref_files), code_list)

    pdfkit.from_file(html_path, pdf_path)

    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)