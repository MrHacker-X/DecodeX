<div align="center">

# ⃤ D E C O D E X ⃤

### ✦ High-Speed Hash Cracker - 6 Attack Modes ✦

![Version](https://img.shields.io/badge/Version-2.0-198c6c?style=for-the-badge&logo=python&logoColor=white)
![Modes](https://img.shields.io/badge/Attack%20Modes-6-2d4a2d?style=for-the-badge&logo=hashnode&logoColor=white)
![Speed](https://img.shields.io/badge/Speed-2M%20h%2Fsec-ab3737?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-8a6d3b?style=for-the-badge&logo=open-source-initiative&logoColor=white)

**Ten algorithms. Six attack modes. Auto-detected.**

DecodeX turns a wall of raw `getattr(hashlib, …)` calls into a precise cracking
tool: automatic algorithm detection from hash length, SHA-2/SHA-3
disambiguation, dictionary / brute-force / mask / salted attacks, a hash
identifier, a secure password generator and a benchmark mode - built on the
standard library.

</div>

---

## 📋 Table of Contents

- [🎯 Why DecodeX?](#-why-decodex)
- [🧭 Tool Purpose](#-tool-purpose)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [✨ Features](#-features)
- [🔄 What Changed in v2.0](#-what-changed-in-v20)
- [🖥️ Preview](#️-preview)
- [🧰 Tech Stack](#-tech-stack)
- [⚠️ Disclaimer](#️-disclaimer)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [👨‍💻 Developer](#-developer)

---

## 🎯 Why DecodeX?

> The old DecodeX worked - but it had no Ctrl+C handling, no way to crack ten
> hashes at once, and made you memorize which algorithm a hash belongs to.
>
> **DecodeX v2.0 respects your terminal and your time.** It detects the
> algorithm from the hash itself, asks only when SHA-2 and SHA-3 genuinely
> collide, attacks with a wordlist, raw brute force or a hashcat-style mask,
> handles salted hashes, identifies unknown formats, cracks whole files in one
> pass, and exits cleanly on Ctrl+C every time.

---

## 🧭 Tool Purpose

DecodeX exists to make **hash recovery and password auditing** fast and
unambiguous:

1. **Auto-detection** - the hash length alone narrows the algorithm; DecodeX
   resolves the rest, and asks only on the real SHA-2/SHA-3 collisions
   (56/64/96/128 hex chars).
2. **Six attack modes** - dictionary, batch, raw brute force with 6 charset
   presets, hashcat-style mask attacks (`?l ?u ?d ?s ?a`), salted wordlist
   attacks (word+salt / salt+word / salt+word+salt) and a hash identifier for
   unknown formats - all via Python's standard `hashlib`, no external
   cracking engine needed.
3. **Batch mode + JSON export** - point it at a file of hashes and get one
   verdict per line; export every cracked value to JSON with `-o`.
4. **Your wordlist or ours** - a 1,049,939-word default list ships with the
   tool; pass `-w` to use any file, one word per line.
5. **Security utilities** - a cryptographically random password generator
   (`secrets` module) and a per-algorithm hashing benchmark round out the
   toolkit.
6. **Honest stats** - every run reports elapsed time, attack speed and words
   tried, whether the crack succeeded or not.

> **What it deliberately is not:** DecodeX is a dictionary cracker, not a
> rainbow table or a GPU rig. Strong, salted or long-random passwords will not
> fall to it - and that is fine.

---

## 🚀 Quick Start

```bash
git clone https://github.com/MrHacker-X/DecodeX.git
cd DecodeX
bash setup.sh
python3 decodex.py
```

One-shot from the terminal:

```bash
# dictionary attack (auto-detected algorithm)
python3 decodex.py -H 5f4dcc3b5aa765d61d8327deb882cf99
python3 decodex.py -H <hash> -a sha3_256 -w mylist.txt
python3 decodex.py -f hashes.txt            # batch mode
python3 decodex.py -f hashes.txt -o out.json  # batch + JSON export

# salted wordlist attack
python3 decodex.py -H <hash> -s SALTVALUE --salt-mode salt+word

# raw brute force
python3 decodex.py -H <hash> -m brute -c digits --min 4 --max 6
python3 decodex.py -H <hash> -m brute -c alnum --min 1 --max 4

# hashcat-style mask attack
python3 decodex.py -H <hash> -m mask -c '?l?l?l?l?d?d'

# identify, generate, benchmark, doctor
python3 decodex.py -i <hash-or-format>
python3 decodex.py -g 10 --gen-length 24    # 10 random passwords
python3 decodex.py --benchmark               # per-algorithm speed
python3 decodex.py --doctor                  # environment check + engine self-test
python3 decodex.py -v                        # version
```

---

## 📦 Installation

```bash
git clone https://github.com/MrHacker-X/DecodeX.git
cd DecodeX
bash setup.sh
python3 decodex.py
```

| Platform  | Status       | Notes                                   |
|-----------|--------------|-----------------------------------------|
| Kali      | ✅ Supported | apt detected natively                   |
| Ubuntu    | ✅ Supported | apt detected natively                   |
| Debian    | ✅ Supported | apt detected natively                   |
| Parrot    | ✅ Supported | apt detected natively                   |
| Arch      | ✅ Supported | pacman                                  |
| Fedora    | ✅ Supported | dnf                                     |
| openSUSE  | ✅ Supported | zypper                                  |
| Alpine    | ✅ Supported | apk                                     |
| Termux    | ✅ Supported | pkg, no root needed                     |
| Windows   | ✅ Supported | pure Python - colorama handles the UI   |

<details>
<summary><b>🔍 Manual installation (no script)</b></summary>

<br>

```bash
git clone https://github.com/MrHacker-X/DecodeX.git
cd DecodeX
python3 -m pip install --user colorama
python3 decodex.py
```

One Python dependency: `colorama`. Everything else - hashing, streaming,
batching - is the standard library. Without colorama the UI degrades to plain
text instead of crashing.

</details>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Auto-detection** | Hash length maps straight to the algorithm - no memorizing which hash is which |
| ⚔️ **SHA-2/SHA-3 disambiguation** | On 56/64/96/128-char collisions the tool asks; everywhere else it just knows |
| 📖 **Dictionary attack** | Streamed wordlist cracking at 2M+ hashes/sec, any file size, constant memory |
| 🧨 **Brute force** | Every combination of a charset from length 1 to 16 - 6 presets or your own |
| 🎭 **Mask attack** | Hashcat-style patterns `?l ?u ?d ?s ?a` with keyspace shown before the run |
| 🧂 **Salted hashes** | `-s SALT` with `--salt-mode word+salt`, `salt+word` or `salt+word+salt` |
| 🔍 **Hash identifier** | Recognizes raw hex digests, bcrypt/md5crypt/sha256crypt/sha512crypt/phpass prefixes and unix crypt |
| 🔑 **Password generator** | Cryptographically random passwords via the `secrets` module - length, count, character classes |
| ⏱️ **Benchmark** | Per-algorithm hashes/sec on this machine, honest single-core numbers |
| 📁 **Batch + JSON export** | `-f hashes.txt` cracks a whole file in one pass; `-o out.json` exports the results |
| 📊 **Honest stats** | Elapsed time, attack speed and words tried on every run - success or not |
| 📜 **1M-word default list** | `core/default_list.txt` ships with the tool, used when `-w` is omitted |
| 🩺 **Doctor + self-test** | `--doctor` verifies python, colorama, SHA-3, the wordlist *and* a live engine round-trip |
| 🛡️ **Safe exit** | Ctrl+C, EOF or `q` anywhere - including mid-crack - exits cleanly (code 130) |
| 🎨 **Typographic UI** | Block-letter banner, colorama palette, options-only menus, framed results |

---

## 🔄 What Changed in v2.0

| | v1.x | v2.0 |
|---|------|------|
| **Attack modes** | Wordlist only | Dictionary, batch, raw brute force, hashcat-style mask and salted-hash attacks |
| **Hash detection** | Manual 10-option menu, wrong pick = silent failure | Auto-detect from length, explicit SHA-2/SHA-3 disambiguation |
| **Identification** | None | Hash identifier - bcrypt, md5crypt, sha256crypt, sha512crypt, apr1, phpass, argon2, unix crypt |
| **Utilities** | None | Password generator (`secrets` module) + per-algorithm benchmark |
| **Batch mode** | None - one hash per launch | `-f file` with per-hash verdicts, cracked-count summary and `-o` JSON export |
| **Doctor** | Basic environment checks | Environment checks + live engine self-test (crack round-trip) |
| **CLI** | None | `-H`, `-a`, `-w`, `-f`, `-m`, `-c`, `--min/--max`, `-s`, `--salt-mode`, `-i`, `-g`, `--gen-length`, `--benchmark`, `-o`, `--verbose`, `--doctor`, `-v` |
| **Exit handling** | Ctrl+C or EOF = raw traceback | Central SafeExit - clean exit 130 everywhere, including mid-crack |
| **Wordlist errors** | Traceback on missing file | Clear `✗` message, exit code 1 |
| **UI** | Raw ASCII art + broken color mixtures | Block-letter wordmark, colorama palette, options-only menu, framed result panel |
| **Setup** | None shipped | `setup.sh` with package-manager detection + verification |
 

---

## 🖥️ Preview

<div align="center">
<img src="https://i.ibb.co/mVJsQKPC/image.png" alt="DecodeX v2.0 banner, menu and crack result" width="760">
</div>

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.8+ (standard library only) |
| Hashing | `hashlib` - MD5, SHA-1/2 family, SHA-3 family |
| Reading | Streamed wordlist loading (constant memory, any file size) |
| UI | colorama palette, auto-disabled on pipes/NO_COLOR |
| Setup | Bash with pkg/apt/dnf/yum/pacman/zypper/apk detection |

---

## ⚠️ Disclaimer

> **1.** DecodeX is built for **authorized security auditing, education and
> password recovery on your own systems** only.
>
> **2.** Cracking hashes of systems or accounts you do not own - or lack
> explicit written permission to test - is **illegal** almost everywhere.
>
> **3.** Dictionary cracking only recovers weak passwords; success depends on
> the wordlist, not the tool.
>
> **4.** The 1M-word default list is for legitimate recovery and benchmarking;
> do not point it at data you have no right to test.
>
> **5.** The developer assumes **no liability** for misuse or damage caused
> by this program. By using DecodeX you accept full responsibility for your
> actions.

---

## 🤝 Contributing

Contributions are welcome - especially wordlist packaging improvements.

```bash
# 1. Fork the repository
# 2. Create your branch
git checkout -b feature/awesome-addition
# 3. Commit and push
git commit -m "Add: awesome addition"
git push origin feature/awesome-addition
# 4. Open a Pull Request
```

Found a bug? Open an [issue](https://github.com/MrHacker-X/DecodeX/issues).

---

## 📜 License

This project is licensed under the **MIT License** - see
[LICENSE](LICENSE) for details.

---

## 👨‍💻 Developer

| | |
|---|---|
| **Developer** | MrHacker-X |
| **GitHub** | [github.com/MrHacker-X](https://github.com/MrHacker-X) |
| **Email** | contact@vritrasec.com |
| **Website** | [vritrasec.com](https://vritrasec.com) |
| **Network** | [link.vritrasec.com](https://link.vritrasec.com) |

---

<div align="center">

**⃤ DecodeX ⃤** - *Detect. Crack. Done.*

⭐ **Found it useful? Star the repo - it keeps the tool sharp.** ⭐

</div>
