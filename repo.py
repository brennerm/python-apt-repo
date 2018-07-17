import bz2
import gzip
import lzma
import os
import re
import urllib.error
import urllib.request as request


def download_raw(url):
    return request.urlopen(url).read()


def download(url):
    return download_raw(url).decode('utf-8')


decompress = {
    '': lambda c: c,
    '.xz': lambda c: lzma.decompress(c),
    '.gz': lambda c: gzip.decompress(c),
    '.bzip2': lambda c: bz2.decompress(c)
}


def download_compressed(base_url):
    for suffix, method in decompress.items():
        url = base_url + suffix

        try:
            req = request.urlopen(url)
        except urllib.error.URLError:
            continue

        return method(req.read()).decode('utf-8')


def get_value(content, key):
    pattern = key + ': (.*)\n'
    match = re.search(pattern, content)
    return match.group(1)


class ReleaseFile:
    def __init__(self, content):
        self.__content = content

    @property
    def origin(self):
        return get_value(self.__content, 'Origin')

    @property
    def label(self):
        return get_value(self.__content, 'Label')

    @property
    def suite(self):
        return get_value(self.__content, 'Suite')

    @property
    def version(self):
        return get_value(self.__content, 'Version')

    @property
    def codename(self):
        return get_value(self.__content, 'Codename')

    @property
    def date(self):
        return get_value(self.__content, 'Date')

    @property
    def architectures(self):
        return get_value(self.__content, 'Architectures').split()

    @property
    def components(self):
        return get_value(self.__content, 'Components').split()

    @property
    def description(self):
        return get_value(self.__content, 'Description')


class PackagesFile:
    def __init__(self, content):
        self.__content = content


class Package:
    def __init__(self, content):
        self.__content = content
        
    @property
    def package(self):
        return get_value(self.__content, 'Package')

    @property
    def version(self):
        return get_value(self.__content, 'Version')


class APTRepository:
    def __init__(self, url, dist):
        self.__url = url
        self.__dist = dist

    @property
    def components(self):
        return self.get_release().components

    def get_release(self):
        url = os.path.join(
            self.__url,
            'dists',
            self.__dist,
            'Release'
        )

        release_content = download(url)

        return ReleaseFile(release_content)

    def get_binary_packages(self, component, arch='amd64'):
        url = os.path.join(
            self.__url,
            'dists',
            self.__dist,
            component,
            'binary-' + arch,
            'Packages'
        )

        print(download_compressed(url))

repo = APTRepository('http://archive.ubuntu.com/ubuntu', 'xenial')
print(repo.get_binary_packages('main'))