""" This module is an auto-indexer for a FPT web page
    such as https://inst.eecs.berkeley.edu/~cs61b/fa16/hw/.

    Step:
    Create a webpage as init webpage to start index;
    create a website with this webpage;
    build the site with website.get_subwebsite();
    and website.download() its content.

    website.get_subwebsite() will run a HTML interpreter which will find any linked webpage.
    website.download() won't run a interpreter. It will construct the directorie that well be
    needed, and then download file to the corresponding folder.

    Example:
        for a website such that:
            http://init-url.com -- code
                                -- homework -- hw01
                                            -- hw02
    # Simpile step:
    >>> auto_indexer("http://init-url.com", "~")
    0
    # File will be download to ~

    # Specific process:
    >>> init-wepage = Webpage("http://init-url.com", True)
    >>> web = Website(init-webpage)
    >>> web
    Website(Webpage("http://init-url.com"))
    >>> web = web.get_subwebsite()
    >>> web
    Website(Webpage("http://init-url.com"),[Website(Webpage("code")), Website(Webpage("homework"
    ), [Website(Webpage("hw01")), Website(Webpage("hw02"))])])
    >>> web.download("~")
    0
    # File will be download to ~
"""

import os
import urllib, urllib.request, urllib.error


def auto_indexer(url, directorie="~", webname="auto-indexer"):
    """ Use the given URL, create a Website, and download it. """
    return Website(Webpage(url), True).get_subwebsite().download(directorie, webname)

class Webpage:
    """ Webpage present a webpage. Webpage only content url or part of url.
    """
    def __init__(self, url, full=False):
        if url[-1] == "/":
            url = url[:-1]
        self.url = url
        self.full = full

    def __repr__(self):
        return 'Webpage("{0}")'.format(self.url)

    def get_subwebpage(self):
        """ Return all subwebpage as a list"""
        assert self.full
        content = None
        try:
            content = HTML(urllib.request.urlopen(self.url))
            print("*** Get: [{0}] ***".format(self.url))
        except urllib.error.URLError as _: #look at it latter
            pass
        if content is None:
            return []
        return content.find_link()

    def download(self, filename):
        """ Download whatever in self.url in to current directory.
        Only be called if self is not a webpage but a contant!
        """
        assert self.full
        urllib.request.urlretrieve(self.url, filename)
        return 0

class HTML:
    """ The interpreter that will get link from HTML webpage. """
    others_obj = ()
    def __init__(self, web_content):
        self.content = web_content

    def find_link(self):
        """ Find any webpage that is linked in this HTML content. """
        subwebpages = []

        br_counter = 0
        last_time = ""
        try:
            while True:
                input_str = self.content.readline()
                expression = self.reader(input_str) # rader() read a line each time.
                for tag in expression:
                    result = self.eval(tag)
                    if isinstance(result, Webpage):
                        subwebpages += [result]
                if input_str == last_time:
                    br_counter += 1
                if input_str != last_time:
                    br_counter = 0
                last_time = input_str
                if br_counter == 10:
                    raise EOFError
        except EOFError as _:
            return subwebpages

    def reader(self, input_str):
        """ Read an HTML <tag>, return an expression of it.
        This func actuale only read next token.
        In here we will only look at where is insit the <>, since we only looking for a tag and
        get it herf. Thus, it will return None if there is no tag in input_str.
        """
        def get_token(input_str):
            """ An token Generator. """
            while len(input_str) >= 1:
                yield chr(input_str[0])
                input_str = input_str[1:]
        get_token = get_token(input_str)

        tags = []
        try:
            while True:
                token = next(get_token)
                if token == '<':
                    tag = self.read_tag(get_token)
                    if tag != None:
                        tags += [tag]
        except StopIteration as _:
            return tags

    def read_tag(self, get_token):
        """ Return the expression. """
        try:
            tag = self.read_str(get_token)
            if tag[0] == '!' or tag[0] == '/': # ignore </tag> and <!DOC>
                return None
            if tag[-1] == '>':
                tag = tag[:-1]
                return HTMLTag(tag)
                return None
            if tag[-1] == ' ':
                tag = tag[:-1]
                attributes = self.read_attributes(get_token)
                return HTMLTag(tag, attributes)
        except StopIteration as _:
            pass

    def read_attributes(self, get_token):
        """ Read the attriubutes in a tag. Return a dictionanry {"attr":"value"} """
        # might someproblem here
        attributes = {}
        incoming = self.read_str(get_token)
        while incoming[-1] != '>':
            if incoming[-1] == '=':
                if incoming[-2] == ' ':
                    incoming = incoming[:-2]
                else:
                    incoming = incoming[:-1]
                attribute = incoming
                attribute_value = self.read_attribute_value(get_token)
                attributes[attribute] = attribute_value
            incoming = self.read_str(get_token)
        return attributes


    def read_attribute_value(self, get_token):
        """ Read the attribute value. """
        # might someproblem here
        # self.read_str(get_token) # read "
        # incoming = self.read_str(get_token)
        # print(incoming)
        # if incoming[0] == ' ': # Incase of attr = "somgthing" form.
        #     if incoming[1] == '\"':
        #         return self.read_attribute_value(get_token)
        # if incoming[-1] != '\"':
        #     incoming = incoming[:-1]
        #     return incoming + self.read_attribute_value(get_token)
        # else:
        #     incoming = incoming[:-1]
        #     return incoming

        incoming = next(get_token)
        def read_token_till_quotation(get_token):
            """ Read the token untill meet a quotation mark. """
            incoming = next(get_token)
            while incoming != '\"':
                return incoming + read_token_till_quotation(get_token)
            return ""

        if incoming == '\"':
            return read_token_till_quotation(get_token)
        else:
            return self.read_attribute_value(get_token)

    def read_str(self, get_token):
        """ Read and return a string untill it meet anything in the stop list. """
        token = next(get_token)
        stop_list = ['=', ' ', '\"', '<', '>']
        if token not in stop_list:
            return token + self.read_str(get_token)
        else:
            return token

    def eval(self, expression):
        """ Return the object that the expression eval to.
        In this case it will only return Webpage object and others_obj for others object.
        """
        if expression.tag == "a":
            return expression.get_webpage()
        else:
            return None

class HTMLTag:
    """ A class to store HTML tag."""
    def __init__(self, tag, attributes={}):
        self.tag = tag
        self.attributes = attributes

    def get_webpage(self):
        """ Make a webpage object for a tag. """
        assert self.tag == "a"
        assert "href" in self.attributes
        if self.attributes["href"][-1] == '/':
            self.attributes["href"] = self.attributes["href"][:-1]
        if self.attributes["href"][0] == '?':
            return None
        if self.attributes["href"][0] == '/':
            return None
        return Webpage(self.attributes["href"], False)


class Website:
    """ Website is a tree that each node is a wepage.
    Example:
        for a website such that:
            http://init-url.com -- code
                                -- homework -- hw01
                                            -- hw02
    >>> init-wepage = Webpage("http://init-url.com, True")
    >>> web = Website(init-webpage)
    >>> web
    Website(Webpage("http://init-url.com"))
    >>> web = web.get_subwebsite()
    >>> web
    Website(Webpage("http://init-url.com"),[Website(Webpage("code")), Website(Webpage("homework"
    ), [Website(Webpage("hw01")), Website(Webpage("hw02"))])])
    >>> web.subwebpages[0].full_url()
    http://init-url.com/code
    >>> [self.full_url() for subwebpage in web.subwebpages]
    ["http://init-url.com/code", "http://init-url.com/homework"]


"""
    pre_init = ()

    def __init__(self, webpage, subwebpages=(), parent=pre_init):
        assert isinstance(parent, Website) or parent is Website.pre_init
        self.webpage = webpage
        self.parent = parent
        for subwebpage in subwebpages:
            assert isinstance(subwebpage, Website)
        self.subwebpages = list(subwebpages)

    def __repr__(self):
        if self.subwebpages:
            branches_str = ',' + repr(self.subwebpages)
        else:
            branches_str = ''
        return 'Website({0}{1})'.format(repr(self.webpage), branches_str)

    def ls(self):
        """ List all subwebpages. """
        for subwebpage in self.subwebpages:
            print(subwebpage.webpage.url)

    def full_url(self):
        """ Get the full web url for self.webpage. """
        if self.parent is Website.pre_init:
            return self.webpage.url
        else:
            return self.parent.full_url() + '/' + self.webpage.url

    website_building_cache = []

    def _get_subwebsite(self):
        """ construct a full Website. It is destructive!
        After you done this remember to clean the cache if you need to!
        """

        if self.webpage.full == False:
            for token in self.webpage.url:
                if token == '.':
                    return self
        subwebpages = Webpage(self.full_url(), True).get_subwebpage()
        print("* Find {0} Webpages *".format(len(subwebpages)))
        self.subwebpages = [Website(subwebpage, (), self) for subwebpage in subwebpages]
        for subwebpage in self.subwebpages:
            if subwebpage.full_url() in Website.website_building_cache:
                subwebpages.remove(subwebpage)
            else:
                Website.website_building_cache += [subwebpage.full_url()]
        for subwebpage in self.subwebpages:
            subwebpage._get_subwebsite()
        return self



    def get_subwebsite(self):
        """ construct a full Website. It is destructive!
        You don't need to clean cache after you done this.
        """
        self._get_subwebsite()
        website_building_cache = []
        return self

    def download(self, directorie="~", webname="auto-indexer"):
        """ Construct the directorie and download file.
        A file that will be downloaded is a Website taht have no subwebsite.
        Return 0 if success.
        """

        #if directorie != ".":
        #    os.chdir(directorie)
        #    if os.path.isdir(webname):
        #        raise EOFError # Sould be some error but I dont know which one is it.
        #    os.makedirs(webname)
        #    os.chdir(webname)

        if self.subwebpages == []:
            web_file = Webpage(self.full_url(), True)
            web_file.download(self.webpage.url)
            print("*** [Download:{0}]***".format(self.full_url()))
        else:
            for subwebsite in self.subwebpages:
                if subwebsite. subwebpages == []:
                    subwebsite.download(".", subwebsite.webpage.url)
                else:
                    os.makedirs(subwebsite.webpage.url)
                    os.chdir(subwebsite.webpage.url)
                    subwebsite.download(".", subwebsite.webpage.url)
                    os.chdir("..")
        return 0


# Test
#web = Webpage("http://inst.eecs.berkeley.edu/~cs61b/fa16/hw/code", True)
#website = Website(web)
#website.get_subwebsite()
