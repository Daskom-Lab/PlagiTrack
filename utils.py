import os
from thefuzz import fuzz as tf
from rapidfuzz import fuzz as rf

UPLOAD_FOLDER = 'uploads'
CACHE_FOLDER = 'cache'
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


def process_similarity(TotalCodePrograms, Scores, Caches, TransformationFactor):
    for i in range(TotalCodePrograms):
        print(f"Analyzing candidate {i + 1} out of {TotalCodePrograms} candidates...", end = " ")
        
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
                
                except IndexError: continue
                


def process_detection(Programs, TransformationFactor=1, LeastPlagiarism=30.0):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CACHE_FOLDER, exist_ok=True)

    TotalCodePrograms: int = len(Programs)
    Caches: list[str] = []
    Tokenizes: list[list] = []
    Scores: list[list[list[list[float]]]] = [
        [
            [
                [0 for _ in range(6)] for _ in range(TotalCodePrograms - 1)
            ] for _ in range(TotalCodePrograms)
        ] for _ in range(TotalCodePrograms)
    ]

    # Load programs and tokenize
    for program in Programs:
        with open(program, 'r', encoding='utf-8') as f:
            Tokenizes.append(f.readlines())
        with open(program, 'r', encoding='utf-8') as f:
            Caches.append("".join(f.readlines()))

    html_output = """
    <div class="max-w-5xl mx-auto p-6">
        <h2 class="text-3xl font-semibold mb-4 text-gray-800">Uncommon Functions Report</h2>
    """

    for item in range(TotalCodePrograms):
        html_output += """
        <hr class="my-6 border-t-2 border-gray-200">
        """
        html_output += f"""
        <div class="mb-4">
            <h2 class="text-lg font-semibold mb-2 text-gray-700 mt-4">
                <span class="font-normal text-gray-600">{Programs[item].replace(UPLOAD_FOLDER + '/', '')} - {len(Tokenizes[item])} lines</span>
            </h2>
            <details open class="bg-gray-50 p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <summary class="cursor-pointer text-md font-medium text-teal-700 hover:text-teal-600">Targets - Found: <span class="font-medium text-gray-800"></span></summary>
                <div class="mt-4">
        """

        count_founded = 0
        total_count_founded = 0

        def generate_section_html(title, key):
            nonlocal count_founded, total_count_founded
            # Build Targets into the Title
            targets_text = ", ".join(CItems[key])  # Joining all target items
            section_html = ''
            # Check and add Found elements
            found_keys = set()
            for line, code_snippet in enumerate(Tokenizes[item]):
                for key_item in CItems[key]:
                    if key_item in code_snippet:
                        section_html += f"""
                        <li class="mb-1"><code>[{line:04d}] {code_snippet.replace(key_item, f'<mark>{key_item}</mark>', 1)}</code></li>
                        """
                        count_founded += 1
                        found_keys.add(key_item)

            section_html += f"""
                    </ul>
                </div>
            </details>
            """

            targets_text = '<mark>' + '</mark>, <mark>'.join(keyword for keyword in CItems[key] if keyword in found_keys) + '</mark>'
            
            section_html = f"""
            <details class="my-4 bg-gray-50 p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <summary class="cursor-pointer text-md font-medium text-teal-700 hover:text-teal-600">
                    {title} - Found {count_founded} - 
                    <span class="text-gray-700 font-normal">{targets_text}</span>
                </summary>
                <div class="mt-2">
                    <h4 class="text-md font-semibold text-gray-800">Found:</h4>
                    <ul class="list-disc pl-6 text-gray-700">
            """ + section_html

            
            if count_founded == 0:
                return ''  # Skip sections with no Found elements
            total_count_founded += count_founded
            count_founded = 0
            return section_html

        # Generate sections for each category
        html_output += generate_section_html("Preprocessor Macros", "Preprocessor Macros")
        html_output += generate_section_html("Preprocessor Directives", "Preprocessor Directives")
        html_output += generate_section_html("Keywords", "Keywords")
        html_output += generate_section_html("Type-Related Features", "Type-Related Features")
        html_output += generate_section_html("Input/Output Functions", "Input/Output Functions")
        html_output += generate_section_html("String and Character Functions", "String and Character Functions")
        html_output += generate_section_html("Wide Characters", "Wide Characters")
        html_output += generate_section_html("Math Functions", "Math Functions")
        html_output += generate_section_html("Complex Numbers", "Complex Numbers")
        html_output += generate_section_html("Time Functions", "Time Functions")
        html_output += generate_section_html("Memory Management", "Memory Management")
        html_output += generate_section_html("Localization", "Localization")
        html_output += generate_section_html("Signals and Error Handling", "Signals and Error Handling")
        html_output += generate_section_html("Multithreading", "Multithreading")
        html_output += generate_section_html("Windows.h", "Windows.h")

        html_output = html_output.replace(
            'Targets - Found: <span class="font-medium text-gray-800"></span>',
            f'Targets - Found: <span class="font-medium text-gray-800">{total_count_founded}</span>',
            1
        )
        html_output += "</div></details>"

    html_output += """
    <hr class="my-6 border-t-2 border-gray-200 mb-12">
    """

    html_output += f"""
    <h2 class="mt-4 text-3xl font-semibold my-4 mb-4 text-gray-800">Plagiarism Results</h2>
    <hr class="my-6 border-t-2 border-gray-200 mb-4">
    <p class="text-gray-700 mb-2">Total Candidates: <span class="font-medium">{TotalCodePrograms}</span></p>
    <p class="text-gray-700 mb-2">Transformation Factor: <span class="font-medium">{TransformationFactor}</span></p>
    <p class="text-gray-700 mb-2">Plagiarism Threshold: <span class="font-medium">{LeastPlagiarism}%</span></p>
    <ul class="list-disc pl-6">
    """

    if False: #TODO
        process_similarity(TotalCodePrograms, Scores, Caches)

    # Sort plagiarism scores
    sort_indexes_dict = {}
    for i in range(TotalCodePrograms):
        for j in range(i + 1, TotalCodePrograms):
            for k in range(TotalCodePrograms - 1):
                if (i == j or j == k or i == k) and (TotalCodePrograms > 2):
                    continue
                sort_indexes_dict[Scores[i][j][k][5]] = (i, j, k)
                break

    sorted_indexes = sorted(sort_indexes_dict.keys(), reverse=True)
    for n, s in enumerate(sorted_indexes):
        i, j, k = sort_indexes_dict[s]
        if Scores[i][j][k][5] > LeastPlagiarism:
            html_output += f"""
            <li class="text-red-600 font-medium"><strong>{Scores[i][j][k][5]:.2f}%</strong> >>> {Programs[i]} x {Programs[j]} <<<</li>
            """
        else:
            html_output += f"""
            <li class="text-gray-600">{Scores[i][j][k][5]:.2f}% {Programs[i]} x {Programs[j]}</li>
            """

    html_output += "</ul></div>"

    return html_output
