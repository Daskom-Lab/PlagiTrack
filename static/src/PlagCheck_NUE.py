from thefuzz import fuzz as tf
from rapidfuzz import fuzz as rf

# For beginners learning C, there are many features in the standard libraries that they 
# might not encounter or fully appreciate until they have more experience. Below is a 
# categorized list of functions, macros, and tokens from the C Standard Library that are 
# less commonly used by beginners:
CItems: dict[str, list[str]] = {
    "Preprocessor Macros": [
        "__LINE__", "__FILE__", "__DATE__", "__TIME__", 
        "CHAR_BIT", "MB_CUR_MAX", "FLT_EPSILON", "DBL_MAX", "LDBL_MIN"
    ],
    "Preprocessor Directives": [
        "#define", "#undef", "#include",
        "#if", "#elif", "#else", "#endif", "#ifdef", "#ifndef",
        "#pragma", "#error", "#line"
    ],
    "Keywords": [
        "register", "extern", "static", "volatile", "restrict", "_Bool", "_Complex", 
        "_Imaginary", "goto", "continue", "default", "alignas", "alignof", "_Atomic", 
        "thread_local", "_Noreturn", "typedef", "enum", "union", "struct", "sizeof", 
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

CandidatesCItems: str = "candidates_c_items.txt"
CandidatesPlagiarismResults: str = "candidates_plagiarism_results.txt"

# List of available programs, use accordingly to the total amount of code programs
# you have on your PC, or some sort... It can be up to whatever amount you wanted to!
# In order to add a code program here, just copy and paste the file path...
Programs: list[str] = [
    "./a.c",
    "./b.c",
    "./c.c",
    "./d.c",
    "./e.c",
    "./f.c",
    "./g.c",
    "./h.c"
]

# --------------------------------------------------
# ---------- IMPORTANT KEYS OF ALGORITHMS ----------
# --------------------------------------------------
# Value for `transformation_factor`
# 
# 0 < transformation_factor <= 1: Compression factor, diluting the 40-50% and maintains for higher percentages.
# transformation_factor > 1:      Expansion factor, creating a higher amount of percentage values.
# transformation_factor <= 0:     Inverts the percentage values, NOT SUITABLE!
# Recommended ranges: 0.75 up to 0.9
transformation_factor: float = 0.8

# Value for `least_plagiarism`
# 
# Recommeded value: 30.00%
least_plagiarism: float = 30.0
# --------------------------------------------------
# ---------- IMPORTANT KEYS OF ALGORITHMS ----------
# --------------------------------------------------

# Begin initializing important variables...
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

# Begin appending the tokens of each code programs and caches, each individually...
for program in Programs:
    with open(program, 'r', encoding = 'utf-8') as f: Tokenizes.append(f.readlines())
    with open(program, 'r', encoding = 'utf-8') as f: Caches.append("".join(f.readlines()))

# Clearing the `CandidatesCItems` file, just in case...
with open(CandidatesCItems, "w", encoding = "utf-8") as f: f.close()

# Begin analyzing the keys of each C items, all of them of each code programs...
print("Analyzing code programs, each individually...", end = " ")
for item in range(TotalCodePrograms):
    with open(CandidatesCItems, "a", encoding = "utf-8") as f:
        f.write("--------------------------------------------------\n")
        f.write(f"Candidate No. {(item + 1):02d}\n")
    
    count_founded: int = 0
    with open(CandidatesCItems, "a", encoding = "utf-8") as f:
        f.write("--------------------------------------------------\n")
        f.write("1. Preprocessor Macros\n")
        for (count, target) in enumerate(CItems["Preprocessor Macros"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Preprocessor Macros"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Preprocessor Macros"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("2. Preprocessor Directives\n")
        for (count, target) in enumerate(CItems["Preprocessor Directives"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Preprocessor Directives"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Preprocessor Directives"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("3. Keywords\n")
        for (count, target) in enumerate(CItems["Keywords"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Keywords"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Keywords"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("4. Type-Related Features\n")
        for (count, target) in enumerate(CItems["Type-Related Features"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Type-Related Features"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Type-Related Features"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("5. Input/Output Functions\n")
        for (count, target) in enumerate(CItems["Input/Output Functions"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Input/Output Functions"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Input/Output Functions"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("6. String and Character Functions\n")
        for (count, target) in enumerate(CItems["String and Character Functions"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["String and Character Functions"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["String and Character Functions"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("7. Wide Characters\n")
        for (count, target) in enumerate(CItems["Wide Characters"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Wide Characters"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Wide Characters"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("8. Math Functions\n")
        for (count, target) in enumerate(CItems["Math Functions"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Math Functions"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Math Functions"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("9. Complex Numbers\n")
        for (count, target) in enumerate(CItems["Complex Numbers"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Complex Numbers"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Complex Numbers"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("10. Time Functions\n")
        for (count, target) in enumerate(CItems["Time Functions"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Time Functions"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Time Functions"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("11. Memory Management\n")
        for (count, target) in enumerate(CItems["Memory Management"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Memory Management"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Memory Management"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("12. Localization\n")
        for (count, target) in enumerate(CItems["Localization"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Localization"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Localization"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("13. Signals and Error Handling\n")
        for (count, target) in enumerate(CItems["Signals and Error Handling"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Signals and Error Handling"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Signals and Error Handling"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("14. Multithreading\n")
        for (count, target) in enumerate(CItems["Multithreading"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Multithreading"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Multithreading"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n")
        f.write("15. Windows.h\n")
        for (count, target) in enumerate(CItems["Windows.h"]):
            if count > 0 and count % 5 == 0: f.write("\n")
            if count != (len(CItems["Windows.h"]) - 1): f.write(f"{target}, ")
            else: f.write(f"{target}\n\n")
        f.write("Found:\n")
        for (line, code_snippet) in enumerate(Tokenizes[item]):
            for key in CItems["Windows.h"]:
                if key in code_snippet: f.write(f"[{line:04d}] {code_snippet}"); count_founded += 1
        f.write(f"(detected {count_founded}'s of them...)\n")
        count_founded = 0
        
        f.write("\n") if item != (len(CItems) - 1) else f.write("--------------------------------------------------\n")

print("Done!")

print()
print(f"=== Plagiarism Check ===")
print(f"Topic: ???")

print()
print(f"Candidate List ({TotalCodePrograms}):")
print(f"    Candidate 01: ...")
print(f"    Candidate 02: ...")
print(f"    Candidate 03: ...")
print(f"    etc...")

# Clearing the `CandidatesPlagiarismResults` file, just in case...
with open(CandidatesPlagiarismResults, "w", encoding = "utf-8") as f: f.close()

# Begin checking the plagiarism of each code programs on another...
print()
print(f"=== Checking Plagiarism ===")
for i in range(TotalCodePrograms):
    print(f"Analyzing candidate {i + 1} out of {TotalCodePrograms} candidates...", end = " ")
    
    for j in range(TotalCodePrograms):
        for k in range(TotalCodePrograms - 1):
            # if i == j or j == k or i == k: continue
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
                    ), transformation_factor
                )
            
            except IndexError: continue
            
    print("Done!")

# Output the results of each code programs...
with open(CandidatesPlagiarismResults, "a", encoding = "utf-8") as f:
    f.write("Algorithm used in checking [AI/Code Program] plagiarism:\n")
    f.write("\t1.  Qualifying tokens by set ratio\n")
    f.write("\t... Method: `token_set_ratio`\n")
    f.write("\t2.  Checking the overall similarities in ratio\n")
    f.write("\t... Method: `ratio`\n")
    f.write("\t3.  Sorting and tokenizing the tokens over ratios\n")
    f.write("\t... Method: `token_sort_ratio`\n")
    f.write("\t4.  Comparing for quick ratios by preserving unicodes\n")
    f.write("\t... Method: `QRatio` and `UQRatio`\n\n")
    
    f.write(f"Transformation by factor: {transformation_factor}\n")
    f.write(f"Plagiarism treshold:      {least_plagiarism}%\n")
    
    f.write("\n")
    f.write(f"Total candidates:         {TotalCodePrograms}\n")
    f.write(f"C items configuration:    {len(CItems)}\n")
    f.write("--------------------------------------------------\n")
    for i in range(TotalCodePrograms):
        for j in range(i + 1, TotalCodePrograms):
            for k in range(TotalCodePrograms - 1):
                if (i == j or j == k or i == k) and (TotalCodePrograms > 2): continue
                
                if Scores[i][j][k][5] > 30.0: f.write(f"[{Scores[i][j][k][5]:.2f}%] >>> `Candidate {(i + 1):02d}` x `Candidate {(j + 1):02d}` <<<\n")
                else: f.write(f"[{Scores[i][j][k][5]:.2f}%] `Candidate {(i + 1):02d}` x `Candidate {(j + 1):02d}`\n")
                break
        f.write("--------------------------------------------------\n") if i != (TotalCodePrograms - 1) else None