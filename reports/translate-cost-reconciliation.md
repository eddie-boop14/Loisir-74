# Translation cost reconciliation — HANDOFF-35 Job B

_Written by `translate_batch.py --audit` on 2026-07-05 from the paid batches' own per-request usage (retrieval is free; nothing was submitted)._

## Verified before the audit

1. **Endpoint ✓** — `client.messages.batches.create` (`/v1/messages/batches`): the 50% batch discount applies. Constants $1.50/$7.50 per MTok match claude-sonnet-4-6 batch pricing.
2. **Prompt caching ✗** — the shared system prompt (~780 est. tokens) sits **below Sonnet 4.6's 2048-token minimum cacheable prefix**, so the `cache_control` marker was silently ignored: every request re-billed the system block as plain input. The cache-read column below is the proof.

## Line items (actuals from usage)

| batch | lang | role | ok | err | in tok | cache-write | cache-read | out tok | actual $ |
|---|---|---|---|---|---|---|---|---|---|
| `msgbatch_019XqXZYqfXuPD2DuxfPnBMD` | pt | main | 389 | 0 | 1,012,390 | 231,702 | 179,860 | 1,190,644 | $10.91 |
| `msgbatch_013mcmBnWjd6dKzn9RRx9yTq` | cs | main | 389 | 0 | 1,012,390 | 222,180 | 189,382 | 1,274,364 | $11.52 |
| `msgbatch_012yiCC2k9WNn53dzL2NALxn` | cs | retry | 153 | 0 | 454,764 | 0 | 161,874 | 554,749 | $4.87 |
| `msgbatch_01NEjNaSgd7BYNKwt7pA9oLv` | pl | main | 42 | 0 | 125,064 | 32,480 | 14,560 | 146,460 | $1.35 |
| `msgbatch_01J9oh4JSG2Z8zzhBuckvyU7` | pl | main | 359 | 0 | 645,788 | 305,760 | 96,320 | 794,496 | $7.52 |
| `msgbatch_01Jqm7K5VkihPvBcCNdPioEe` | pl | main | 5034 | 0 | 774,187 | 0 | 0 | 377,087 | $3.99 |
| `msgbatch_01QYagU2Qmbd1sJhWv5HjJpt` | pl | main | 5034 | 0 | 774,187 | 0 | 0 | 375,691 | $3.98 |
| `msgbatch_016SzszP4316C7sTuweiaLTs` | pl | main | 5034 | 0 | 774,187 | 0 | 0 | 375,433 | $3.98 |
| `msgbatch_01J4Uv9ogcR5ZN11nTyNfVJG` | ar | main | 11142 | 0 | 1,340,688 | 0 | 0 | 619,835 | $6.66 |
| `msgbatch_016JysyzBBuaNdGSxiGAbt3w` | he | main | 5732 | 0 | 858,590 | 0 | 0 | 499,216 | $5.03 |
| `msgbatch_017gRYiseXTYmXYaLvgkWHnm` | ja | main | 8799 | 0 | 1,199,528 | 0 | 0 | 520,183 | $5.70 |
| `msgbatch_015gyEt8ShUVmi6NHRRr2Uiw` | pt | retry | 389 | 0 | 1,012,390 | 27,508 | 384,054 | 1,190,925 | $10.56 |
| `msgbatch_01HQwpbffJXBq4t1vaDf9WXH` | pt | retry | 4 | 0 | 9,052 | 0 | 4,232 | 10,711 | $0.09 |

## Contract vs actual, to the cent

### ar

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $2.01 | +0.69 |
| output | $6.36 | $4.65 | -1.71 |
| **main batch** | **$7.68** | **$6.66** | **-1.02** |
| retry round(s) (outside the contract) | $0.00 | $0.00 | +0.00 |
| **total** | **$7.68** | **$6.66** | **-1.02** |

- of the input delta, the never-firing cache accounts for ≈ $12.44 (system block re-billed at 1× on 11141 requests instead of 0.1×).
- measured output: — tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

### cs

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $1.96 | +0.65 |
| output | $6.36 | $9.56 | +3.20 |
| **main batch** | **$7.68** | **$11.52** | **+3.85** |
| retry round(s) (outside the contract) | $0.00 | $4.87 | +4.87 |
| **total** | **$7.68** | **$16.39** | **+8.71** |

- of the input delta, the never-firing cache accounts for ≈ $0.41 (system block re-billed at 1× on 388 requests instead of 0.1×).
- measured output: 0.4286 tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

### he

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $1.29 | -0.03 |
| output | $6.36 | $3.74 | -2.61 |
| **main batch** | **$7.68** | **$5.03** | **-2.65** |
| retry round(s) (outside the contract) | $0.00 | $0.00 | +0.00 |
| **total** | **$7.68** | **$5.03** | **-2.65** |

- of the input delta, the never-firing cache accounts for ≈ $6.40 (system block re-billed at 1× on 5731 requests instead of 0.1×).
- measured output: — tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

### ja

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $1.80 | +0.48 |
| output | $6.36 | $3.90 | -2.46 |
| **main batch** | **$7.68** | **$5.70** | **-1.97** |
| retry round(s) (outside the contract) | $0.00 | $0.00 | +0.00 |
| **total** | **$7.68** | **$5.70** | **-1.97** |

- of the input delta, the never-firing cache accounts for ≈ $9.24 (system block re-billed at 1× on 8798 requests instead of 0.1×).
- measured output: — tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

### pl

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $5.29 | +3.97 |
| output | $6.36 | $15.52 | +9.16 |
| **main batch** | **$7.68** | **$20.81** | **+13.13** |
| retry round(s) (outside the contract) | $0.00 | $0.00 | +0.00 |
| **total** | **$7.68** | **$20.81** | **+13.13** |

- of the input delta, the never-firing cache accounts for ≈ $16.28 (system block re-billed at 1× on 15502 requests instead of 0.1×).
- measured output: 0.299 tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

### pt

| item | contract | actual | delta |
|---|---|---|---|
| input (incl. system block) | $1.32 | $1.98 | +0.66 |
| output | $6.36 | $8.93 | +2.57 |
| **main batch** | **$7.68** | **$10.91** | **+3.23** |
| retry round(s) (outside the contract) | $0.00 | $10.65 | +10.65 |
| **total** | **$7.68** | **$21.56** | **+13.89** |

- of the input delta, the never-firing cache accounts for ≈ $0.41 (system block re-billed at 1× on 388 requests instead of 0.1×).
- measured output: 0.4017 tok per source char vs the old model's implicit 0.2857 (out ≈ in assumption).

## Corrected model (now live in `estimate()`)

- input: **0.3389 tok/char** measured (was chars/3.5 ≈ 0.2857)
- output: per-language measured factors {"cs": 0.4286, "pl": 0.299, "pt": 0.4017} (was out ≈ in)
- system block priced **uncached** below the 2048-token minimum cacheable prefix (was: cached for 388/389 requests)
- observed cache-read share: 0.087

## Permanent rule now enforced in code

The dry-run number is a contract. A run that exceeds it by >15% ABORTS before the next paid submit (retry round / next language) and exits red; the final meter line always prints actual vs contract. No `go <lang>` until its calibrated dry-run lands and the previous languages' deltas are explained above.
