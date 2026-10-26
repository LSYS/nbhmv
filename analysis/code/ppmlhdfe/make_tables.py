from pathlib import Path

import pandas as pd

RESULTS = Path("../../../results/tables/ppml/ppml_fixest_results.csv")
OUT_DIR = Path("../../../results/tables/ppml")

LABEL_WIDTH = 20  # esttab varwidth(20)
NUM_WIDTH = 8  # esttab modelwidth(8)
STAR_WIDTH = 9  # space for stars

# row labels, from $coeff_labels in set_globals.do
TERM_LABELS = {
    "mismatch_p25": r"Price \pxor{}",
    "mismatch_p25_p2r": r" LP $\rightarrow$ HP",
    "mismatch_p25_r2p": r" HP $\rightarrow$ LP",
    "mismatch_race": r"Ethnic \pxor{}",
    "mismatch_race_m2c": r"Mnr $\rightarrow$ Maj",
    "mismatch_race_c2m": r"Maj $\rightarrow$ Mnr",
}

# p-value row label, directional tables only
JOINT_LABELS = {
    "pxor-wpsm-r2p-p2r": (
        r"$ p $-val: (LP $\rightarrow$ HP) = (HP $\rightarrow$ LP)"
    ),
    "pxor-race-asymmetry": (
        r"$ p $-val: (Mnr $\rightarrow$ Maj) = (Maj $\rightarrow$ Mnr)"
    ),
}

# tick rows, and the first spec that gets a tick
FLAG_ROWS = [
    ("Day fixed effects", 1),
    ("Census area-by-day fixed effects", 1),
    ("Demographics", 2),
    ("Businesses", 3),
    ("Neighborhood-specific rainfall", 4),
    ("Places of interest", 5),
]
CHECK = r"\multicolumn{1}{c}{\checkmark}"


def stars(p: float) -> str:
    """Significance asterisks, from esttab star(* 0.1 ** 0.05 *** 0.01).

    Parameters
    ----------
    p : float
        Two-sided p-value.

    Returns
    -------
    str
        An esttab `\\sym{}` field, padded to the reserved width.
    """
    mark = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
    return (rf"\sym{{{mark}}}" if mark else "").ljust(STAR_WIDTH)


def stata_pval(p: float) -> str:
    """Format a p-value as the Stata do-files do.

    Parameters
    ----------
    p : float
        P-value.

    Returns
    -------
    str
        "<.001" below .0005, otherwise three decimals with leading and
        trailing zeros dropped, so 0.0600 becomes ".06".
    """
    if p < 0.0005:
        return "<.001"
    v = round(p, 3)
    if v == 1:
        return "1"
    return f"{v:.3f}".rstrip("0").lstrip("0")


def cell(content: str) -> str:
    """Pad one table cell to the number field plus the reserved star field."""
    return content.rjust(NUM_WIDTH) + " " * STAR_WIDTH


def row(label: str, cells: list[str]) -> str:
    """Assemble one LaTeX row from a label and its preformatted cells."""
    return label.ljust(LABEL_WIDTH) + "&" + "&".join(cells) + r"\\"


def fragment(df_table: pd.DataFrame) -> str:
    """Build the complete fragment for one table.

    Parameters
    ----------
    df_table : pandas.DataFrame
        Rows of the results file belonging to a single table.

    Returns
    -------
    str
        Fragment text, newline-terminated.
    """
    specs = sorted(df_table["spec"].unique())
    lines = []

    for term in df_table["term"].unique():
        df_term = df_table.loc[lambda df_: df_["term"] == term].set_index("spec")
        lines.append(
            row(
                TERM_LABELS[term],
                [
                    f"{df_term.loc[s, 'coef']:{NUM_WIDTH}.4f}"
                    + stars(df_term.loc[s, "pvalue"])
                    for s in specs
                ],
            )
        )
        lines.append(row("", [cell(f"({df_term.loc[s, 'se']:.4f})") for s in specs]))

    df_model = df_table.drop_duplicates("spec").set_index("spec")

    for label, first_spec in FLAG_ROWS:
        lines.append(
            row(label, [cell(CHECK if s >= first_spec else "") for s in specs])
        )

    table = df_table["table"].iloc[0]
    if table in JOINT_LABELS:
        lines.append(
            row(
                JOINT_LABELS[table],
                [cell(stata_pval(df_model.loc[s, "joint_p"])) for s in specs],
            )
        )

    lines.append(
        row("Pseudo R$^2$", [cell(f"{df_model.loc[s, 'pr2']:.4f}") for s in specs])
    )
    lines.append(
        row(
            "Days",
            [
                cell(rf"\multicolumn{{1}}{{c}}{{$ {df_model.loc[s, 'ndates']} $}}")
                for s in specs
            ],
        )
    )
    for label, col in [("Clusters", "nclust"), ("Observations", "nobs")]:
        lines.append(
            row(
                label,
                [
                    cell(rf"\multicolumn{{1}}{{c}}{{$ {df_model.loc[s, col]:>9,} $}}")
                    for s in specs
                ],
            )
        )
    return "\n".join(lines) + "\n"


df_results = pd.read_csv(RESULTS)

for table in df_results["table"].unique():
    df_table = df_results.loc[lambda df_: df_["table"] == table]
    path = OUT_DIR / f"{table}-ppml-frag.tex"
    path.write_text(fragment(df_table))
    print(f"wrote {path}")
