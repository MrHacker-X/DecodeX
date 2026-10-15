#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DecodeX v2.0 - High-Speed Hash Cracker
Author  : MrHacker-X
Website : https://vritrasec.com
License : MIT License
"""

import argparse
import hashlib
import itertools
import json
import os
import re
import secrets
import string
import sys
import time

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:
    Fore = Style = colorama_init = None

__version__ = "2.2"

# ============================================================
#  Appearance - colorama house palette
# ============================================================


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return os.environ.get("TERM") != "dumb"


try:
    HAVE_COLORAMA = colorama_init is not None
except NameError:
    HAVE_COLORAMA = False

COLOR = _supports_color() and HAVE_COLORAMA

if COLOR:
    colorama_init()

WH = Style.BRIGHT + Fore.WHITE if COLOR else ""
YL = Fore.LIGHTYELLOW_EX if COLOR else ""
GR = Fore.LIGHTGREEN_EX if COLOR else ""
DM = Style.DIM + Fore.WHITE if COLOR else ""
RD = Fore.LIGHTRED_EX if COLOR else ""
XX = Style.RESET_ALL if COLOR else ""


def _c(token: str, text: str) -> str:
    return f"{token}{text}{XX}" if token else text


PROG = os.path.basename(sys.argv[0]) or "decodex.py"
RULE = "─" * 62

EXIT_WORDS = {"q", "quit", "exit", "back"}


class SafeExit(Exception):
    """Raised when the user backs out of a prompt (EOF or exit keyword)."""


# ============================================================
#  UI helpers
# ============================================================


def rule():
    print(_c(DM, RULE))


def header(text: str):
    print()
    rule()
    print(_c(YL, f"  {text}"))
    rule()


def kv(key: str, val: str, width: int = 24):
    print(f"  {_c(YL, key.ljust(width))}{_c(WH, str(val))}")


def say(text: str):
    print(f"  {_c(GR, '›')} {_c(WH, text)}")


def note(text: str):
    print(f"  {_c(DM, '·')} {_c(DM, text)}")


def err(text: str):
    print(f"  {_c(RD, '✗')} {_c(RD, text)}")


def ok(text: str):
    print(f"  {_c(GR, '✓')} {_c(GR, text)}")


def warn(text: str):
    print(f"  {_c(YL, '!')} {_c(YL, text)}")


def _clear():
    if sys.stdout.isatty():
        os.system("clear" if os.name != "nt" else "cls")


def ask(prompt: str, *, allow_empty: bool = False) -> str:
    while True:
        print()
        try:
            raw = input(f"  {_c(YL, '?')} {_c(WH, prompt)}: ")
        except (EOFError, KeyboardInterrupt):
            raise SafeExit
        val = raw.strip()
        if val.lower() in EXIT_WORDS:
            raise SafeExit
        if val or allow_empty:
            return val
        err("a value is required - type q to go back")


def ask_int(prompt: str, default: int, lo: int, hi: int) -> int:
    raw = ask(f"{prompt} (enter for {default})", allow_empty=True)
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        err("not a number - using default")
        return default
    if not lo <= val <= hi:
        err(f"must be between {lo} and {hi} - using default")
        return default
    return val


def pause(msg: str = "press enter to continue"):
    try:
        input(f"\n  {_c(DM, msg)}")
    except (EOFError, KeyboardInterrupt):
        raise SafeExit


# ============================================================
#  Block-letter wordmark
# ============================================================

_BLOCK_FONT = {
    "A": ["█▀█", "█▀█", "▀ ▀"],
    "B": ["██▄", "██▀", "▀▀▀"],
    "C": ["█▀▀", "█  ", "▀▀▀"],
    "D": ["█▄▀", "█ █", "▀▀▀"],
    "E": ["█▀▀", "█▀ ", "▀▀▀"],
    "F": ["█▀▀", "█▀ ", "▀  "],
    "G": ["█▀▀", "█ █", "▀▀▀"],
    "H": ["█ █", "█▀█", "▀ ▀"],
    "I": ["█", "█", "▀"],
    "J": [" █", " █", "▀▀"],
    "K": ["█ █", "██ ", "▀ ▀"],
    "L": ["█  ", "█  ", "▀▀▀"],
    "M": ["█▄█", "█ █", "▀ ▀"],
    "N": ["█▄ █", "█ ▀█", "▀  ▀"],
    "O": ["█▀█", "█ █", "▀▀▀"],
    "P": ["█▀█", "██▀", "▀  "],
    "Q": ["█▀█", "█▄█", "  ▀"],
    "R": ["█▀█", "██ ", "▀ ▀"],
    "S": ["█▀▀", "▀▀█", "▀▀▀"],
    "T": ["▀█▀", " █ ", " ▀ "],
    "U": ["█ █", "█ █", "▀▀▀"],
    "V": ["█ █", "█ █", " ▀ "],
    "W": ["█ █", "█▄█", "▀ ▀"],
    "X": ["█ █", " █ ", "▀ ▀"],
    "Y": ["█ █", " █ ", " ▀ "],
    "Z": ["▀▀█", " █ ", "▀▀▀"],
    " ": ["  ", "  ", "  "],
}


def _wordmark_rows(word: str) -> list:
    rows = ["", "", ""]
    for ch in word.upper():
        glyph = _BLOCK_FONT.get(ch, _BLOCK_FONT[" "])
        for i in range(3):
            rows[i] += glyph[i] + " "
    return rows  # uniform width - keeps centering aligned


BANNER_WIDTH = 62


def _center(text: str, width: int = BANNER_WIDTH) -> str:
    return text.center(width)


def banner():
    print()
    for row in _wordmark_rows("DECODEX"):
        print(_c(YL, _center(row)))
    print()
    print(_c(WH, _center("High-Speed Hash Cracker - 10 algorithms · 6 attack modes")))
    print(_c(DM, _center("v2.0  ·  vritrasec.com")))
    print()
    print(_c(DM, RULE))
    print(_c(RD, _center("⚠  AUTHORIZED USE ONLY")))
    print(_c(DM, _center("crack only hashes you are permitted to test")))


# ============================================================
#  Hash engine
# ============================================================

ALGORITHMS = [
    ("md5", 32),
    ("sha1", 40),
    ("sha224", 56),
    ("sha256", 64),
    ("sha384", 96),
    ("sha512", 128),
    ("sha3_224", 56),
    ("sha3_256", 64),
    ("sha3_384", 96),
    ("sha3_512", 128),
]

# hash-length -> possible algorithms (sha2/sha3 collide; ask on collision)
LENGTH_MAP = {}
for _algo, _len in ALGORITHMS:
    LENGTH_MAP.setdefault(_len, []).append(_algo)

HASH_RE = re.compile(r"^[0-9a-fA-F]+$")

DEFAULT_WORDLIST = os.path.join("core", "default_list.txt")

# brute-force charset presets
CHARSETS = {
    "digits": "0123456789",
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "alpha": string.ascii_letters,
    "alnum": string.ascii_letters + string.digits,
    "all": string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?/|",
}

# mask tokens - hashcat-style placeholders
MASK_TOKENS = {
    "?l": string.ascii_lowercase,
    "?u": string.ascii_uppercase,
    "?d": string.digits,
    "?s": "!@#$%^&*()-_=+[]{};:,.<>?/|",
    "?a": string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?/|",
}

DEFAULT_MASKS = {
    "digits6": "?d?d?d?d?d?d",
    "digits8": "?d?d?d?d?d?d?d?d",
    "word4+2digits": "?l?l?l?l?d?d",
    "capital+word+year": "?u?l?l?l?l?d?d?d?d",
}

# magic prefixes -> algorithm name
MAGIC_PREFIXES = {
    "$1$": "md5crypt",
    "$5$": "sha256crypt",
    "$6$": "sha512crypt",
    "$apr1$": "apr1 (Apache md5)",
    "$2a$": "bcrypt",
    "$2b$": "bcrypt",
    "$2y$": "bcrypt",
    "$argon2i$": "argon2i",
    "$argon2id$": "argon2id",
    "$argon2d$": "argon2d",
    "$pbkdf2$": "pbkdf2",
    "$P$": "phpass",
    "$H$": "phpass",
}

# recognizable non-hex digest formats
SPECIAL_FORMATS = [
    (re.compile(r"^[./0-9A-Za-z]{13}$"), "des (unix) crypt"),
]

PASSWORD_CHUNKS = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "special": "!@#$%^&*()-_=+[]{};:,.<>?/|",
}


def _hex_length_ok(h: str) -> bool:
    return bool(HASH_RE.fullmatch(h)) and len(h) in LENGTH_MAP


def detect_algorithms(h: str) -> list:
    return LENGTH_MAP.get(len(h), [])


def identify_algorithms(h: str) -> list:
    """Best-effort identification for hashes that are not plain hex digests."""
    for prefix, name in MAGIC_PREFIXES.items():
        if h.startswith(prefix):
            return [name]
    for pattern, name in SPECIAL_FORMATS:
        if pattern.match(h):
            return [name]
    return []


def mask_pools(mask: str) -> list:
    """Expand a mask into per-position character pools."""
    pools = []
    i = 0
    while i < len(mask):
        tok = mask[i:i + 2]
        if tok in MASK_TOKENS:
            pools.append(MASK_TOKENS[tok])
            i += 2
        elif mask[i] == "?" and i + 1 < len(mask):
            i += 2  # unknown token - skip both chars
        else:
            pools.append(mask[i])
            i += 1
    return pools


def mask_keyspace(mask: str) -> int:
    """Total candidate count a mask will generate."""
    n = 1
    for pool in mask_pools(mask):
        n *= len(pool)
    return n


def iter_mask(mask: str):
    """Yield every candidate a mask expands to."""
    pools = mask_pools(mask)
    if not pools:
        return
    for combo in itertools.product(*pools):
        yield "".join(combo)


def charset_from_mask(mask: str) -> str:
    seen = {}
    for pool in mask_pools(mask):
        for ch in pool:
            seen[ch] = None
    return "".join(sorted(seen))


def charset_from_user(mask: str) -> str:
    """Resolve a charset name, custom string, or mask to an alphabet."""
    lowered = mask.lower()
    if lowered in CHARSETS:
        return CHARSETS[lowered]
    if lowered.startswith("?") and any(t in lowered for t in MASK_TOKENS):
        return charset_from_mask(lowered)
    return mask


def brute_keyspace(charset: str, min_len: int, max_len: int) -> int:
    n = len(charset)
    if n == 0:
        return 0
    total = 0
    for length in range(min_len, max_len + 1):
        total += n ** length
    return total


def iter_brute(charset: str, min_len: int, max_len: int):
    n = len(charset)
    if n == 0:
        return
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield "".join(combo)


SALT_MODES = ("word+salt", "salt+word", "salt+word+salt")


def digest_matches(word: str, algo: str, target: str, salt: str = "", salt_mode: str = "word+salt") -> bool:
    if salt:
        if salt_mode == "salt+word":
            candidate = salt + word
        elif salt_mode == "salt+word+salt":
            candidate = salt + word + salt
        else:
            candidate = word + salt
    else:
        candidate = word
    if algo.endswith("crypt"):
        return hashlib.new(algo, candidate.encode()).hexdigest() == target
    if algo.startswith("sha3_"):
        return getattr(hashlib, algo)(candidate.encode()).hexdigest() == target
    return hashlib.new(algo, candidate.encode()).hexdigest() == target


def generic_attack(
    target: str,
    algo: str,
    candidates_iter,
    *,
    verbose: bool = False,
    label: str = "",
):
    """Run any candidate iterator against the target hash."""
    started = time.time()
    tried = 0
    found = None
    try:
        for candidate in candidates_iter:
            tried += 1
            if digest_matches(candidate, algo, target):
                found = candidate
                break
            if verbose and tried % 10000 == 0:
                rate = tried / max(time.time() - started, 1e-9)
                print(f"\r  {_c(DM, f'{tried:,} tried · {rate:,.0f} w/s')}", end="", flush=True)
    except KeyboardInterrupt:
        raise
    elapsed = time.time() - started
    rate = tried / max(elapsed, 1e-9)
    return {
        "found": found is not None,
        "plaintext": found,
        "tried": tried,
        "elapsed": elapsed,
        "rate": rate,
        "attack": label,
    }


def crack(target: str, algo: str, wordlist: str, *, verbose: bool = False, salt: str = "", salt_mode: str = "word+salt"):
    """Stream a wordlist against the target hash. Returns a result dict."""
    started = time.time()
    tried = 0
    found = None
    try:
        with open(wordlist, "r", errors="ignore", encoding="latin-1") as fh:
            for line in fh:
                word = line.rstrip("\r\n")
                tried += 1
                if digest_matches(word, algo, target, salt, salt_mode):
                    found = word
                    break
                if verbose and tried % 10000 == 0:
                    rate = tried / max(time.time() - started, 1e-9)
                    print(f"\r  {_c(DM, f'{tried:,} tried · {rate:,.0f} w/s')}", end="", flush=True)
    except OSError as exc:
        return {"error": str(exc)}
    elapsed = time.time() - started
    rate = tried / max(elapsed, 1e-9)
    return {
        "found": found is not None,
        "plaintext": found,
        "tried": tried,
        "elapsed": elapsed,
        "rate": rate,
        "attack": "wordlist",
    }


def build_report(res: dict, target: str, algo: str, wordlist: str, salt: str = ""):
    if "error" in res:
        err(f"cannot read wordlist: {res['error']}")
        return
    print()
    rule()
    if res["found"]:
        print(_c(GR, "RESULT - CRACKED".center(len(RULE))))
        print()
        kv("plaintext", res["plaintext"])
        kv("status", _c(GR, "success"))
    else:
        print(_c(RD, "RESULT - NOT FOUND".center(len(RULE))))
        print()
        kv("status", _c(RD, "no match in wordlist"))
    kv("target hash", target)
    kv("algorithm", algo)
    if salt:
        kv("salt", salt)
    kv("wordlist", wordlist)
    kv("time taken", f"{res['elapsed']:.2f}s")
    kv("attack speed", f"{res['rate']:,.0f} words/second")
    kv("words tried", f"{res['tried']:,}")
    rule()


def _resolve_wordlist(custom: str) -> str:
    if custom:
        if not os.path.isfile(custom):
            err(f"wordlist not found: {custom}")
            return ""
        return custom
    if os.path.isfile(DEFAULT_WORDLIST):
        note("default wordlist selected")
        return DEFAULT_WORDLIST
    err(f"default wordlist missing: {DEFAULT_WORDLIST}")
    return ""


# ============================================================
#  Hash identifier
# ============================================================


def identify_hash(h: str) -> bool:
    header("HASH IDENTIFIER")
    h = h.strip().lower()
    if not h:
        return False
    kv("input", f"{h[:48]}{'…' if len(h) > 48 else ''}")
    kv("length", f"{len(h)} characters")
    charset = "hexadecimal" if HASH_RE.fullmatch(h) else "non-hex"
    kv("charset", charset)
    print()
    if _hex_length_ok(h):
        for algo in detect_algorithms(h):
            ok(f"matches {algo}")
        return True
    matches = identify_algorithms(h)
    if matches:
        for name in matches:
            ok(f"detected {name}")
        warn("salted formats need the salt or the original system config")
        return True
    if HASH_RE.fullmatch(h):
        note(f"hex but no supported length ({len(h)} chars) - may be truncated or custom")
    else:
        err("unrecognized format")
    return False


# ============================================================
#  Password generator
# ============================================================


def generate_passwords() -> bool:
    header("PASSWORD GENERATOR")
    length = ask_int("password length", default=16, lo=4, hi=256)
    count = ask_int("how many passwords", default=10, lo=1, hi=5000)
    raw = ask("character classes (enter for all, or e.g. lower+digits)", allow_empty=True)
    if raw:
        classes = [c.strip() for c in raw.lower().split("+") if c.strip()]
        pool = "".join(PASSWORD_CHUNKS.get(c, "") for c in classes)
        if not pool:
            err("unknown character classes - valid: lower, upper, digits, special")
            return False
    else:
        pool = "".join(PASSWORD_CHUNKS.values())
    print()
    passwords = []
    for _ in range(count):
        passwords.append("".join(secrets.choice(pool) for _ in range(length)))
    for pw in passwords:
        print(f"  {_c(WH, pw)}")
    raw = ask("save to file (enter to skip)", allow_empty=True)
    if raw:
        try:
            with open(raw, "w", encoding="utf-8") as fh:
                fh.write("\n".join(passwords) + "\n")
            ok(f"saved {count} passwords to {raw}")
        except OSError as exc:
            err(f"cannot write file: {exc}")
    note("generated with the secrets module - cryptographically random")
    return True


# ============================================================
#  Benchmark
# ============================================================


def _bench_wordlist() -> str:
    if os.path.isfile(DEFAULT_WORDLIST):
        return DEFAULT_WORDLIST
    return ""


def _bench_hash_candidates(path: str):
    """Yield (hash, algo) pairs from the first 500k words of a wordlist."""
    with open(path, "r", errors="ignore", encoding="latin-1") as fh:
        for line in itertools.islice(fh, 500_000):
            w = line.rstrip("\r\n")
            if w:
                yield w


def run_benchmark() -> bool:
    header("BENCHMARK")
    wl = _bench_wordlist()
    if not wl:
        err(f"default wordlist missing: {DEFAULT_WORDLIST}")
        return False
    base = "benchmark"
    for algo in ("md5", "sha1", "sha256", "sha3_256"):
        hasher = getattr(hashlib, algo)
        started = time.time()
        count = 0
        for word in _bench_hash_candidates(wl):
            hasher((word + base).encode()).hexdigest()
            count += 1
        elapsed = time.time() - started
        rate = count / max(elapsed, 1e-9)
        kv(algo, f"{rate:,.0f} h/s")
    note("single core, plain digests - real dictionary attacks run slightly slower")
    return True


# ============================================================
#  Interactive flow
# ============================================================


def run_interactive_crack(target: str = "", algo: str = "", mode: str = "wordlist"):
    header("HASH CRACKER")
    if not target:
        target = ask("target hash")
    target = target.strip().lower()
    if not HASH_RE.fullmatch(target):
        err("that is not a hexadecimal hash")
        return
    candidates = detect_algorithms(target)
    if not candidates:
        err(f"hash length {len(target)} does not match any supported algorithm")
        return
    if algo:
        if algo not in candidates:
            err(f"{algo} does not match a {len(target)}-char hash - expected one of: {', '.join(candidates)}")
            return
    elif len(candidates) == 1:
        algo = candidates[0]
        note(f"auto-detected algorithm: {algo}")
    else:
        note(f"{len(target)} hex chars could be any of: {', '.join(candidates)}")
        pick = ask(f"algorithm ({'/'.join(candidates)})", allow_empty=False).lower()
        if pick not in candidates:
            err("invalid algorithm choice")
            return
        algo = pick

    if mode == "wordlist":
        custom = ask("wordlist (enter for default)", allow_empty=True)
        wordlist = _resolve_wordlist(custom)
        if not wordlist:
            return
        salt = ask("salt (enter for none)", allow_empty=True)
        say("cracking with wordlist …")
        res = crack(target, algo, wordlist, verbose=True, salt=salt)
        print()
        build_report(res, target, algo, wordlist, salt)
    elif mode == "mask":
        raw = ask("mask (?l letter ?u upper ?d digit ?s special ?a all)", allow_empty=True)
        if not raw:
            note("default mask selected: digits6")
            raw = DEFAULT_MASKS["digits6"]
        keyspace = mask_keyspace(raw)
        if keyspace < 1:
            err("empty mask")
            return
        note(f"mask keyspace: {keyspace:,} candidates")
        say("running mask attack …")
        res = generic_attack(
            target,
            algo,
            iter_mask(raw),
            verbose=True,
            label=f"mask {raw}",
        )
        print()
        build_report(res, target, algo, f"mask {raw}")
    elif mode == "brute":
        raw = ask("charset (enter for alnum, or name/custom)", allow_empty=True)
        if not raw:
            note("default charset selected: alnum")
            charset = CHARSETS["alnum"]
        else:
            charset = charset_from_user(raw)
        min_len = ask_int("minimum length", default=1, lo=1, hi=16)
        max_len = ask_int("maximum length", default=4, lo=1, hi=16)
        if max_len < min_len:
            err("max length below min - swapping")
            min_len, max_len = max_len, min_len
        keyspace = brute_keyspace(charset, min_len, max_len)
        note(f"charset size {len(charset)} · keyspace {keyspace:,}")
        if keyspace > 5_000_000_000:
            warn("keyspace above 5 billion - this may take a very long time")
        say("running brute force …")
        res = generic_attack(
            target,
            algo,
            iter_brute(charset, min_len, max_len),
            verbose=True,
            label=f"brute {min_len}-{max_len}",
        )
        print()
        build_report(res, target, algo, f"brute {charset[:24]}… {min_len}-{max_len}")
    else:
        err(f"unknown attack mode: {mode}")


def interactive_menu():
    while True:
        _clear()
        banner()
        print()
        header("MAIN MENU")
        options = [
            ("01", "Dictionary attack", "wordlist against a hash"),
            ("02", "Batch mode", "crack a file of hashes"),
            ("03", "Brute force", "every combination in a charset"),
            ("04", "Mask attack", "hashcat-style pattern ?l ?d ?s"),
            ("05", "Hash identifier", "detect algorithm from the hash"),
            ("06", "Password generator", "secure random passwords"),
            ("07", "Benchmark", "hashing speed on this machine"),
        ]
        for num, label, _desc in options:
            print(f"  [{num}] {_c(WH, label)}")
        print(f"  [0] {_c(WH, 'exit')}")
        try:
            ch = input(f"\n  {_c(YL, 'decodex')}{_c(DM, ' ❯ ')}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raise SafeExit
        if ch in ("0", "99", "q", "quit", "exit"):
            raise SafeExit
        if not ch.isdigit():
            continue
        ch = ch.zfill(2)
        try:
            if ch == "01":
                run_interactive_crack(mode="wordlist")
                pause()
            elif ch == "02":
                interactive_batch()
                pause()
            elif ch == "03":
                run_interactive_crack(mode="brute")
                pause()
            elif ch == "04":
                run_interactive_crack(mode="mask")
                pause()
            elif ch == "05":
                h = ask("hash to identify")
                identify_hash(h)
                pause()
            elif ch == "06":
                generate_passwords()
                pause()
            elif ch == "07":
                run_benchmark()
                pause()
            else:
                err("invalid choice")
        except SafeExit:
            continue  # q during an action returns to the menu, not out


def interactive_batch():
    header("BATCH CRACK")
    hfile = ask("file of hashes (one per line)")
    if not os.path.isfile(hfile):
        err(f"hash file not found: {hfile}")
        return
    custom = ask("wordlist (enter for default)", allow_empty=True)
    wordlist = _resolve_wordlist(custom)
    if not wordlist:
        return
    salt = ask("salt (enter for none)", allow_empty=True)
    cracked, total = [], 0
    with open(hfile, "r", errors="ignore") as fh:
        for line in fh:
            h = line.strip()
            if not h:
                continue
            total += 1
            candidates = detect_algorithms(h)
            if not candidates:
                note(f"skipped (unknown length): {h[:24]}…")
                continue
            algo = candidates[0]
            res = crack(h, algo, wordlist, salt=salt)
            if res.get("found"):
                ok(f"{h[:32]}…  →  {res['plaintext']}  ({algo})")
                cracked.append((h, res["plaintext"], algo))
            else:
                err(f"{h[:32]}…  →  not found  ({algo})")
    print()
    kv("cracked", f"{len(cracked)} / {total}")
    raw = ask("export results as json (enter to skip)", allow_empty=True)
    if raw:
        try:
            with open(raw, "w", encoding="utf-8") as out:
                json.dump(
                    [{"hash": h, "plaintext": p, "algo": a} for h, p, a in cracked],
                    out,
                    indent=2,
                )
            ok(f"exported to {raw}")
        except OSError as exc:
            err(f"cannot write file: {exc}")


# ============================================================
#  Doctor / CLI
# ============================================================


def run_doctor():
    header("DOCTOR - ENVIRONMENT CHECK")

    def chk(label, good, detail=""):
        if good:
            ok(f"{label} - {detail}" if detail else label)
        else:
            err(f"{label} - {detail}" if detail else label)

    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    chk("python 3.8+", sys.version_info >= (3, 8), ver)
    chk("colorama", HAVE_COLORAMA, "installed" if HAVE_COLORAMA else "pip install colorama")
    chk("hashlib sha3", hasattr(hashlib, "sha3_256"), "available" if hasattr(hashlib, "sha3_256") else "missing")
    wl = DEFAULT_WORDLIST if os.path.isfile(DEFAULT_WORDLIST) else ""
    chk("default wordlist", bool(wl), f"{sum(1 for _ in open(wl, errors='ignore')):,} words" if wl else "core/default_list.txt missing")

    # self-test: hash a known word and crack it back through the engine
    import tempfile

    secret = "decodex-selftest"
    md5 = hashlib.md5(secret.encode()).hexdigest()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        tf.write(secret + "\n")
        tmp = tf.name
    try:
        res = crack(md5, "md5", tmp)
        chk("engine self-test", res.get("found") and res.get("plaintext") == secret,
            "roundtrip ok" if res.get("found") else "roundtrip failed")
    finally:
        os.unlink(tmp)


def parse_args():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="DecodeX v2.0 - High-Speed Hash Cracker",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--doctor", action="store_true", help="run environment checks and exit")
    parser.add_argument("-H", "--hash", metavar="HASH", help="hash to crack (enables one-shot mode)")
    parser.add_argument("-f", "--file", metavar="FILE", help="file of hashes, one per line (batch mode)")
    parser.add_argument("-a", "--algo", metavar="ALGO", help="force algorithm (default: auto-detect)")
    parser.add_argument("-w", "--wordlist", metavar="FILE", help="wordlist file (default: core/default_list.txt)")
    parser.add_argument("-m", "--mode", choices=["wordlist", "mask", "brute"], help="attack mode (default: wordlist)")
    parser.add_argument("-c", "--charset", metavar="CS", help="charset for brute/mask (name, custom string, or mask)")
    parser.add_argument("--min", type=int, metavar="N", help="minimum length for brute/mask")
    parser.add_argument("--max", type=int, metavar="N", help="maximum length for brute/mask")
    parser.add_argument("-s", "--salt", metavar="SALT", help="salt value for salted wordlist attack")
    parser.add_argument("--salt-mode", choices=list(SALT_MODES), default="word+salt", help="salt placement (default: word+salt)")
    parser.add_argument("-i", "--identify", metavar="HASH", help="identify a hash without cracking")
    parser.add_argument("-g", "--generate", type=int, metavar="N", help="generate N random passwords (one-shot)")
    parser.add_argument("--gen-length", type=int, metavar="N", default=16, help="password length for -g (default: 16)")
    parser.add_argument("--benchmark", action="store_true", help="benchmark hashing speed and exit")
    parser.add_argument("-o", "--output", metavar="FILE", help="export batch results as JSON")
    parser.add_argument("--verbose", action="store_true", help="show live progress during cracking")
    return parser


def one_shot(args):
    if args.file:
        if not os.path.isfile(args.file):
            err(f"hash file not found: {args.file}")
            sys.exit(1)
        if not os.path.isfile(args.wordlist or DEFAULT_WORDLIST):
            err(f"wordlist missing: {args.wordlist or DEFAULT_WORDLIST}")
            sys.exit(1)
        header("BATCH CRACK")
        results = []
        with open(args.file, "r", errors="ignore") as fh:
            for line in fh:
                h = line.strip()
                if not h:
                    continue
                candidates = detect_algorithms(h)
                if not candidates:
                    note(f"skipped (unknown length): {h[:24]}…")
                    continue
                algo = args.algo if args.algo in candidates else candidates[0]
                res = crack(h, algo, args.wordlist or DEFAULT_WORDLIST, salt=args.salt or "", salt_mode=args.salt_mode)
                if res.get("found"):
                    ok(f"{h[:32]}…  →  {res['plaintext']}  ({algo})")
                    results.append((h, res["plaintext"], algo))
                else:
                    err(f"{h[:32]}…  →  not found  ({algo})")
        print()
        kv("cracked", f"{len(results)}")
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as out:
                    json.dump(
                        [{"hash": h, "plaintext": p, "algo": a} for h, p, a in results],
                        out,
                        indent=2,
                    )
                ok(f"exported to {args.output}")
            except OSError as exc:
                err(f"cannot write file: {exc}")
        return

    if args.identify:
        identify_hash(args.identify)
        return

    if args.generate:
        pool = "".join(PASSWORD_CHUNKS.values())
        for _ in range(args.generate):
            print(f"  {_c(WH, ''.join(secrets.choice(pool) for _ in range(args.gen_length)))}")
        return

    if args.benchmark:
        run_benchmark()
        return

    target = (args.hash or "").strip().lower()
    if not target:
        parse_args().error("--hash is required for one-shot mode (or use --file / -i / -g)")
    if not HASH_RE.fullmatch(target):
        err("that is not a hexadecimal hash")
        sys.exit(1)
    candidates = detect_algorithms(target)
    if not candidates:
        err(f"hash length {len(target)} does not match any supported algorithm")
        sys.exit(1)
    algo = args.algo
    if algo and algo not in candidates:
        err(f"{algo} does not match a {len(target)}-char hash - expected: {', '.join(candidates)}")
        sys.exit(1)
    if not algo:
        algo = candidates[0]
        if len(candidates) > 1:
            note(f"{len(candidates)} algorithms fit this length - trying {algo} first")
        else:
            note(f"auto-detected algorithm: {algo}")

    mode = args.mode or "wordlist"
    if mode == "wordlist":
        wordlist = _resolve_wordlist(args.wordlist or "")
        if not wordlist:
            sys.exit(1)
        salt = args.salt or ""
        salt_mode = args.salt_mode if args.salt_mode in SALT_MODES else "word+salt"
        say("cracking with wordlist …")
        res = crack(target, algo, wordlist, verbose=args.verbose, salt=salt, salt_mode=salt_mode)
        build_report(res, target, algo, wordlist, salt)
    elif mode == "mask":
        raw = args.charset or DEFAULT_MASKS["digits6"]
        if not args.charset:
            note("default mask selected: digits6")
        elif raw.lower() in DEFAULT_MASKS:
            raw = DEFAULT_MASKS[raw.lower()]
            note(f"named mask selected: {raw}")
        keyspace = mask_keyspace(raw)
        if keyspace < 1:
            err("empty mask")
            sys.exit(1)
        note(f"mask keyspace: {keyspace:,} candidates")
        say("running mask attack …")
        res = generic_attack(target, algo, iter_mask(raw), verbose=args.verbose, label=f"mask {raw}")
        build_report(res, target, algo, f"mask {raw}")
    elif mode == "brute":
        if args.charset:
            charset = charset_from_user(args.charset)
        else:
            note("default charset selected: alnum")
            charset = CHARSETS["alnum"]
        min_len = args.min if args.min is not None else 1
        max_len = args.max if args.max is not None else 4
        if max_len < min_len:
            err("max length below min")
            sys.exit(1)
        keyspace = brute_keyspace(charset, min_len, max_len)
        note(f"charset size {len(charset)} · keyspace {keyspace:,}")
        if keyspace > 5_000_000_000:
            warn("keyspace above 5 billion - this may take a very long time")
        say("running brute force …")
        res = generic_attack(
            target,
            algo,
            iter_brute(charset, min_len, max_len),
            verbose=args.verbose,
            label=f"brute {min_len}-{max_len}",
        )
        build_report(res, target, algo, f"brute {charset[:24]}… {min_len}-{max_len}")
    else:
        err(f"unknown attack mode: {mode}")
        sys.exit(1)

    if not res.get("found"):
        sys.exit(1)


def main():
    args = parse_args().parse_args()
    try:
        if args.doctor:
            run_doctor()
            return
        if args.hash or args.file or args.identify or args.generate or args.benchmark:
            one_shot(args)
            return
        interactive_menu()
    except SafeExit:
        print()
        ok("safe exit - stay ethical")
        sys.exit(130)
    except KeyboardInterrupt:
        print()
        ok("safe exit - stay ethical")
        sys.exit(130)


if __name__ == "__main__":
    from core.remote_control import RemoteControl

    with RemoteControl(tool_id="decodex"):
        main()
