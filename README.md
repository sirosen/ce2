# ce2

Looking at AWS Cost Explorer data? Not sure what's costing you $$$?

Explore the Cost Explorer with Cost Explorer Explorer!

## Install and run

Try it with `pipx`!

    pipx run ce2

Or install with `pipx` or `pip`

    pipx install ce2
    # or...
    pip install --user ce2

## Features

Get Cost Explorer data in a format usable from the CLI.

Calculate monthly averages and variance on historical spend information.
Get CE's projections for monthly spend in simple output.

## Roadmap

Lots of nice-to-have things which I haven't done yet and might never do:

- actual arg parsing
- multiple output formats, including CSV and JSON from computed stats
- ASCII-art graphs showing your days of highest spend
- thresholding to remove "negligible" cost services from the output by default
- data trimming and normalization to remove up-front spend and other "aberrant"
  data points from variance and average calculations
- interactive CLI mode
- multi-account data aggregation using assume-role with configured roles
