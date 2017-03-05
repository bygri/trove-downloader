# trove-downloader

Downloads newspapers from [Trove](http://trove.nla.gov.au). All issues, all pages, all articles. High-res
page images and article abstracts.

Do not use in contravention of [copyright](http://help.nla.gov.au/trove/our-policies/copyright)
or Trove's [terms of use](http://trove.nla.gov.au/general/termsofuse). In particular, this means
that **commercial use is not allowed**; you will need to contact [Copies Direct](http://copiesdirect.nla.gov.au)
to purchase copies of your material.

## Installation

Requires Python 3 with a couple of additional packages. Assuming you have a python3 virtualenv,
install additional requirements with `pip install -r requirements.txt`.

## Usage

You will first need to find out the *index letter* and *ID number* of the publication. You can get the latter
from the newspaper's citation link; it will look like `http://nla.gov.au/nla.news-titleXXX` where `XXX` is the
ID number. The former is probably the first letter of the publication's title. You can find out for sure from
Trove's newspaper browser.

If your index letter is `A` and your ID number is `123`, then call the script like this:

```
python trove.py A 123
```

All data will be stored in a folder named `out`. You can change this by adding an argument `--out=pathname`.

You can cancel and re-start the script at any time, as data already downloaded will be cached rather than
downloaded a second time.

## Abuse

Trove is a fantastic service operated by the cash-strapped National Library of Australia. If you make use of
materials provided by the NLA, please [support the library](http://www.nla.gov.au/support-us) financially.

This script intentionally runs slowly to avoid hitting NLA's servers too hard. Please do not alter this
behaviour, and try to run the script overnight or out of peak periods only.
