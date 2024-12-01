import os
from thefuzz import fuzz as tf
from rapidfuzz import fuzz as rf
from aiohttp import web
from glob import glob

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

