# Project: Iranian Customer Churn

Baca @PROJECT_GUIDE.md sebelum mengerjakan apa pun. File itu adalah sumber kebenaran project ini
(keputusan terkunci, roadmap, dan masalah yang sudah diketahui). Prinsip kerja umum sudah dimuat dari `~/.claude/CLAUDE.md`.

Pengingat paling penting (rincian di PROJECT_GUIDE.md bagian 4):
- Validasi wajib `StratifiedGroupKFold` dengan grup `seed`. Dilarang split acak per baris.
- Bukan fitur: `seed`, `seed_churn`, `orig_pos`, `fold_*`, `Age`, `Customer_Value`.
- `dataset/` dan `program/artifacts/` tidak boleh ditimpa. Hasil baru diberi versi (`_v2`).
- Tanpa Docker untuk saat ini.
