# auto-indexer
An auto-indexer for a small FPT web page.
Made for me to download file in http://inst.eecs.berkeley.edu/~cs61b/fa16/hw
## Usage
    # Simpile step:
    >>> auto_indexer("http://init-url.com")
    # Print many things
    0
    # File will be downloaded

    # Specific process:
    >>> init-wepage = Webpage("http://init-url.com", True)
    >>> web = Website(init-webpage)
    >>> web
    Website(Webpage("http://init-url.com"))
    >>> web = web.get_subwebsite()
    # Will print webpage url and how many subpage in it
    >>> web
    Website(Webpage("http://init-url.com"),[Website(Webpage("code")), Website(Webpage("homework"
    ), [Website(Webpage("hw01")), Website(Webpage("hw02"))])])
    >>> web.download()
    # Will print downloaded file url
    0
    # File will be downloaded
    
## Problem
- Website.download() is not finish. Now it will only download to current folder.
- Create folder with no content as a file (intentionally).
- Cannot use in shell as `python3 auto-indexer [website] [path]` (not yet finish).

## How does it work
I do not know how others auto-indexer work. This is just how I think an auto-index can work.

Each webpage is a Webpage instance, and can form a Website tree as Website(webpage, subwebpages).
For given initial webpage, Website.get_subwebsite() will recursively form a whole website tree as following step:

1. Website.get_subwebsite() ask webpage to give its subpages as a list

2. When webpage need to return its subpages, webpage first get whatever in the url, and than ask a HTML interpreter to interpret it.

3. HTML interpreter will interpret the web page. It will read the page, and for each tag (since we only want to know the link in the tag.), it return a HTMLTag object. Than interpreter eval this object and return Webpage object.

4. After finish interpret the webpage, interpreter will return all Webpage object it creates as a list

5. Webpage return its link to Website.get_subwebsite()

6. for each subwebpage, subwebpage.get_subwebsite()
